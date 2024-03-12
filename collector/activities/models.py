from pydantic import BaseModel


class User(BaseModel):
    user_url: str
    user_name: str
    company: str


class Reply(BaseModel):
    user_url: str
    user_name: str
    duration_since: str
    content: str


class Comment(BaseModel):
    user_url: str
    user_name: str
    duration_since: str
    content: str
    replies: list[Reply]


class PostActivity(BaseModel):
    user: User
    time_posted: str
    content: str
    number_of_reactions: int | None
    number_of_comments: int | None
    comments_list: list[Comment]
