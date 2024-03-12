import logging
from datetime import datetime

import uvicorn
from asyncer import asyncify
from fastapi import FastAPI, Request

from collector.app_models import LoginRequest, Metadata, SearchResponse
from collector.companies.company_flow import search_companies_flow
from collector.login.login_page import check_linkedin_login, login_to_linkedin
from collector.users.users_flow import search_users_flow

logger = logging.getLogger(__name__)

app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    logger.info(f"Request: '{request.url}'| method: {request.method} | processing...")
    start_time = datetime.now()
    response = await call_next(request)
    process_time = datetime.now() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Request: '{request.url}' finished | time took {round(process_time.total_seconds(), 1)} seconds.")
    return response


@app.get("/")
async def read_root():
    return {"message": "Welcome to the SearchRunner API!"}


@app.post("/login")
async def login_linkedin(request: LoginRequest):
    await asyncify(login_to_linkedin)(username=request.username, password=request.password)
    return {"message": "Login succeeded!"}


@app.get("/search/users")
async def search_users(search_query: str) -> SearchResponse:
    search_results = await asyncify(search_users_flow)(search_query=search_query, number_of_search_results=5)
    return SearchResponse(
        search_query=search_query,
        metadata=Metadata(timestamp=datetime.now()),
        search_results=search_results,
    )


@app.get("/search/companies")
async def search_companies(search_query: str) -> SearchResponse:
    search_results = await asyncify(search_companies_flow)(search_query=search_query, number_of_search_results=5)
    return SearchResponse(
        search_query=search_query,
        metadata=Metadata(timestamp=datetime.now()),
        search_results=search_results,
    )


@app.get("/health")
async def health_check():
    expired_at = await asyncify(check_linkedin_login)()
    return {"status": "ok", "expired_at": expired_at}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
