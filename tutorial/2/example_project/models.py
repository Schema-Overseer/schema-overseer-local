from pydantic import AnyHttpUrl, BaseModel


class UserSiteSearchQuery(BaseModel):
    query: str


class NewSiteSearchQuery(BaseModel):
    text: str | None = None
    image: AnyHttpUrl | None = None
