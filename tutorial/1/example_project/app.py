from flask import Flask, request
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(
    app,
    config=Swagger.DEFAULT_CONFIG
    | {
        "specs_route": "/",
        "openapi": "3.0.3",
        "title": "Swagger | Example Project",
        "info": {
            "version": "1.1",
            "title": "Example Project",
        },
    },
)


@app.post("/log-site-search")
def log_site_search():
    """Log site search queries
    ---
    requestBody:
      content:
        application/json:
          schema:
            type: object
            required:
              - query
            properties:
              query:
                type: string
                example: pepperoni pizza
    responses:
      200:
        description: OK
        content:
          text/plain:
              schema:
                type: string
    """
    payload = request.get_json()
    log_entry = payload["query"]

    message = f'User query for logging: "{log_entry}"'

    # In a real life we would save processed payload in some kind of a database
    return message
