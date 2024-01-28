from __future__ import annotations

from flasgger import Swagger
from flask import Flask, Response, request

app = Flask(__name__)
swagger_config = Swagger.DEFAULT_CONFIG.copy()
swagger_config.update(
    {
        'specs_route': '/',
        'openapi': '3.0.3',
        'title': 'Swagger | Example Project',
        'info': {
            'version': '1.2',
            'title': 'Example Project',
        },
    }
)
Swagger(app, config=swagger_config)


@app.post('/log-site-search')
def log_site_search() -> str | Response:
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
    payload = request.get_json()

    if 'query' in payload:
        log_entry = payload['query']

    elif 'text' in payload or 'image' in payload:
        text_log_entry = payload.get('text', '<no text>')
        image_log_entry = payload.get('image', 'empty')
        log_entry = f'{text_log_entry} | <image "{image_log_entry}">'

    else:
        return Response('Invalid payload scheme', status=400)

    message = f'User query for logging: "{log_entry}"'

    # In a real life we would save processed payload in some kind of a database
    return message
