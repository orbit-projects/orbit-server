from orbit_types import RequestModel
from orbit_types.exceptions import ValidationError as OrbitValidationError
from orbit_server.context import RequestContext

from pydantic import ValidationError as PydanticValidationError
import inspect


async def resolve_async(value):
    import inspect

    if inspect.iscoroutine(value):
        return await value

    if isinstance(value, dict):
        return {
            k: await resolve_async(v)
            for k, v in value.items()
        }

    if isinstance(value, list):
        return [await resolve_async(v) for v in value]

    return value
    
async def execute_handler(handler, request_data, container=None, request_cache=None, context=None):
    try:
        sig = inspect.signature(handler)
        kwargs = {}

        for name, param in sig.parameters.items():
            param_type = param.annotation

            if param_type == inspect._empty:
                kwargs[name] = None
                continue

            if isinstance(param_type, str):
                import sys
                module = sys.modules[handler.__module__]
                param_type = getattr(module, param_type)

            if param_type == RequestContext:
                kwargs[name] = context
                continue

            if issubclass_safe(param_type, RequestModel):
                try:
                    kwargs[name] = param_type(**request_data)
                except PydanticValidationError as e:
                    raise OrbitValidationError(e.errors())
                continue

            if container and isinstance(param_type, type):
                instance = container.resolve(param_type, request_cache)

                if instance is None:
                    raise Exception(f"DI failed for {param_type}")

                kwargs[name] = instance
                continue

            kwargs[name] = None

        result = handler(**kwargs)
        result = await resolve_async(result)

        return result

    except OrbitValidationError:
        raise

    except Exception as e:
        raise Exception(f"Handler execution failed: {str(e)}")

def issubclass_safe(cls, base):
    try:
        return issubclass(cls, base)
    except Exception:
        return False
