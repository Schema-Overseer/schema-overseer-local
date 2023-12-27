from fastapi import FastAPI

from .models import UserSiteSearchQuery

app = FastAPI(version='1.1')


@app.post("/log-site-search")
def main(payload: UserSiteSearchQuery) -> str:
    message = f'User query: "{payload.query}"'

    # In a real life we would save processed payload in some kind of a database
    return message
