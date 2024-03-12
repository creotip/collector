from playwright.sync_api import ElementHandle

from collector.activities.models import Comment, Reply
from collector.helpers import get_attribute, get_inner_text


def extract_comments(comments_list_elements: list[ElementHandle]):
    comments_list = []
    for comment in comments_list_elements:
        comment_header = "section.comment .comment__body .comment__header .comment__author"
        comment_user_url = get_attribute(comment, comment_header, "href")
        comment_user_name = get_inner_text(comment, comment_header)

        comment_duration_since = get_inner_text(
            comment, "section.comment .comment__body .comment__header .comment__duration-since"
        )
        comment_content = get_inner_text(
            comment, ".comment__body > .attributed-text-segment-list__container > .comment__text"
        )

        replies = []
        reply_elements = comment.query_selector_all(".comments-list__comments-list--reply")

        for reply in reply_elements:
            has_children = reply.evaluate("""element => element.children.length > 0""")

            if not has_children:
                continue

            reply_header = "section.comment .comment__body .comment__header .comment__author"
            reply_user_url = get_attribute(reply, reply_header, "href")
            reply_user_name = get_inner_text(reply, reply_header)

            reply_duration_since = get_inner_text(
                reply, "section.comment .comment__body .comment__header .comment__duration-since"
            )
            reply_content = get_inner_text(
                reply, ".comment__body > .attributed-text-segment-list__container > .comment__text"
            )
            replies.append(
                Reply(
                    user_url=reply_user_url,
                    user_name=reply_user_name,
                    duration_since=reply_duration_since,
                    content=reply_content,
                )
            )

        comments_list.append(
            Comment(
                user_url=comment_user_url,
                user_name=comment_user_name,
                duration_since=comment_duration_since,
                content=comment_content,
                replies=replies,
            )
        )
    return comments_list
