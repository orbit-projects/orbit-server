import inspect

def generate_openapi(app):
    paths = {}

    for route in app.get_routes():
        path = route.path
        method = route.method.lower()

        if path not in paths:
            paths[path] = {}

        paths[path][method] = {
            "summary": route.handler.__name__,
            "responses": {
                "200": {
                    "description": "Successful Response"
                }
            }
        }

        if (
            route.request_model
            and route.request_model != inspect._empty
            and hasattr(route.request_model, "model_json_schema")
        ):
            paths[path][method]["requestBody"] = {
                "content": {
                    "application/json": {
                        "schema": route.request_model.model_json_schema()
                    }
                }
            }

        if (
            route.response_model
            and route.response_model != inspect._empty
            and hasattr(route.response_model, "model_json_schema")
        ):
            paths[path][method]["responses"]["200"]["content"] = {
                "application/json": {
                    "schema": route.response_model.model_json_schema()
                }
            }

    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Orbit API",
            "version": "1.0.0"
        },
        "paths": paths
    }
