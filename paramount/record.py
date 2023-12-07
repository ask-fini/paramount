import inspect
import json


def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


def serialize_item(item):
    if is_jsonable(item):
        return item
    elif hasattr(item, 'json') and callable(getattr(item, 'json', None)):  # JSON-serializable method?
        try:
            return item.json()  # Try to get json content from the object.
        except Exception:
            pass
    elif hasattr(item, 'data'):  # Raw data attribute accessible?
        try:
            return json.loads(item.data.decode())
        except (json.JSONDecodeError, AttributeError):
            pass
    return str(item)


def serialize_response(response):
    """Attempt to serialize response to a more JSON-friendly format."""
    if isinstance(response, tuple):
        return tuple(serialize_item(item) for item in response)  # Handle each tuple item.
    else:
        return serialize_item(response)


def record(func):
    def wrapper(*args, **kwargs):
        func_params = inspect.signature(func).parameters
        args_names = list(func_params.keys())
        args_dict = dict(zip(args_names[:len(args)], args))
        args_dict.update(kwargs)
        result = func(*args, **kwargs)
        serialized_result = serialize_response(result)

        print(f"Args and kwargs: {json.dumps(args_dict, indent=2)}, Result: {json.dumps(serialized_result, indent=2)}")
        # todo: put as cols, record to df
        return result
    return wrapper
