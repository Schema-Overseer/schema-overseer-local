from fastapi import FastAPI

from .models import UserSiteSearchQuery, NewSiteSearchQuery

app = FastAPI(version="1.2")


@app.post("/log-site-search")
def main(payload: UserSiteSearchQuery | NewSiteSearchQuery) -> str:
    if isinstance(payload, UserSiteSearchQuery):
        message = f'User query: "{payload.query}"'
    else:
        message = f'User query: "{payload.text}"'

    # In a real life we would save processed payload in some kind of a database
    return message
