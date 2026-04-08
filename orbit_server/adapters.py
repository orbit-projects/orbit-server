from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from orbit_types.exceptions import OrbitError
from orbit_types import ResponseModel


async def parse_request(request: Request):
    try:
        return await request.json()
    except Exception:
        return {}


def to_response(result):
    if isinstance(result, Response):
        return result

    if isinstance(result, ResponseModel):
        return JSONResponse(result.to_dict())

    if isinstance(result, dict):
        return JSONResponse(result)

    return JSONResponse({"data": result})

def error_response(error: Exception, debug=False):
    if isinstance(error, OrbitError):
        return JSONResponse(
            {
                "error": "validation_error",
                "details": format_validation_errors(error.args[0])
            },
            status_code=400,
        )

    return JSONResponse(
        {
            "error": "internal_server_error",
            "message": str(error) if debug else "Something went wrong",
        },
        status_code=500,
    )


def format_validation_errors(errors):
    return [
        {
            "field": ".".join(map(str, e["loc"])),
            "message": e["msg"],
            "type": e["type"],
        }
        for e in errors
    ]
