from datetime import datetime

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class Metadata(BaseModel):
    timestamp: datetime


class SearchResponse(BaseModel):
    search_query: str
    search_results: list
    metadata: Metadata
