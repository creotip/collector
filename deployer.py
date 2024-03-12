import logging
import os
import subprocess
from io import StringIO
from pathlib import Path
from time import time
from typing import Annotated

from boto3 import Session as Boto3Session
from generic_service_chart.aws_utils import set_session_profile
from generic_service_chart.common import (
    render_service_manifests,
    render_template,
    run_command,
)
from generic_service_chart.constants import AWS_REGION, ECR_REGISTRY, ENV
from generic_service_chart.kube_utils import kubectl_apply, use_eks_kubeconfig
from typer import Option, Typer

app = Typer()


def format_to_image_tag(name: str) -> str:
    return name.replace("/", "-")


aws_session: Boto3Session | None = None
GIT_BRANCH = format_to_image_tag(os.environ.get("BRANCH_NAME", subprocess.getoutput("git rev-parse --abbrev-ref HEAD")))
AWS_ROLE = "service-deployer"
DEFAULT_NAMESPACE = "collector"


@app.callback()
def init():
    global aws_session

    aws_session = set_session_profile(ENV, AWS_ROLE, AWS_REGION)

    logging.basicConfig(level=logging.INFO)


@app.command()
def deploy(
    dry_run: Annotated[bool, Option(envvar="DRY_RUN")] = False,
    tag: Annotated[str, Option(envvar="TAG")] = GIT_BRANCH,
    override_kubeconfig: Annotated[bool, Option(envvar="OVERRIDE_KUBECONFIG")] = True,
):
    dirname = Path(__file__).parent / "infra"

    if override_kubeconfig:
        use_eks_kubeconfig(aws_session, dirname / "generated")

    # Create namespace essentials if not exists
    try:
        run_command(f"kubectl get ns {DEFAULT_NAMESPACE}")
    except RuntimeError:
        run_command(f"kubectl create ns {DEFAULT_NAMESPACE}")

    # Deploy service essentials
    with StringIO(render_template(Path(__file__).parent / "infra" / "env_template.yml.tpl", params={})) as f:
        kubectl_apply(
            render_service_manifests(f, namespace=DEFAULT_NAMESPACE),  # type: ignore
            dry_run=dry_run,
        )

    # Deploy manifests

    params = {
        "namespace": DEFAULT_NAMESPACE,
        "image": {
            "registry": ECR_REGISTRY,
            "repository": "revrod/linkedin-collector",
            "tag": tag,
        },
        "now": int(time()),
    }

    for file in (dirname / "manifests").glob("*"):
        kubectl_apply(render_template(file, params), dry_run=dry_run)


def main():
    app()


if __name__ == "__main__":
    main()
