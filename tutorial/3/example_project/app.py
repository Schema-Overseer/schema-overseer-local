from flasgger import Swagger
from flask import Flask, Response, request

from .payloads import InvalidPayload, build_log_entry

app = Flask(__name__)
swagger_config = Swagger.DEFAULT_CONFIG.copy()
swagger_config.update(
    {
        "specs_route": "/",
        "openapi": "3.0.3",
        "title": "Swagger | Example Project",
        "info": {
            "version": "1.3",
            "title": "Example Project",
        },
    }
)
Swagger(app, config=swagger_config)


@app.post("/log-site-search")
def log_site_search() -> str:
    """Log site search queries
    ---
    requestBody:
      content:
        application/json:
          schema:
            anyOf:
              - properties:
                  text:
                    type: string
                  image:
                    type: string
                type: object
              - properties:
                  query:
                    type: string
                required:
                  - query
                type: object
          examples:
            legacy:
              value:
                query: pepperoni pizza
            new:
              value:
                text: what kind of pizza is this?
                image: http://example.com/pizza.jpg
    responses:
      200:
        description: OK
        content:
          text/plain:
              schema:
                type: string
    """
    payload_dict = request.get_json()

    try:
        log_entry = build_log_entry(payload_dict)
    except InvalidPayload:
        return Response("Invalid payload scheme", status=400)

    message = f'User query for logging: "{log_entry}"'

    # In a real life we would save processed payload in some kind of a database
    return message
