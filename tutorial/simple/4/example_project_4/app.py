from flasgger import Swagger
from flask import Flask, Response, abort, request

from schema_overseer_local import InvalidSchemaError

from .payload.registry import payload_schema_registry

app = Flask(__name__)
swagger_config = Swagger.DEFAULT_CONFIG.copy()
swagger_config.update(
    {
        'specs_route': '/',
        'openapi': '3.0.3',
        'title': 'Swagger | Example Project',
        'info': {
            'version': '1.4',
            'title': 'Example Project',
        },
    }
)
Swagger(app, config=swagger_config)
payload_schema_registry.setup()


@app.post('/log-site-search')
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
                  create_at:
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
        context = payload_schema_registry.build(source_dict=payload_dict)
    except InvalidSchemaError:
        abort(Response('Invalid payload schema', status=400))

    message = f'User query for logging: "{context.log_entry}" at {context.log_datetime}'

    # In a real life we would save processed payload in some kind of a database
    return message
