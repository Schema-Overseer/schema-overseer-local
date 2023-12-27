from pydantic import BaseModel


class UserSiteSearchQuery(BaseModel):
    query: str
