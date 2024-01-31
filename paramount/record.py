import pandas as pd
import json
import inspect
from datetime import datetime
import pytz
from time import time
import uuid
import traceback
from flask import request, jsonify
from .db_connector import db
from dotenv import load_dotenv, find_dotenv
import os
if find_dotenv():
    load_dotenv()
import threading


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
    elif callable(response):  # Check if it is a generator function, eg. LLM streaming is on (with SSE)
        return False
    else:
        return serialize_item(response)


def record(flask_app):
    db_instance = db.get_database()
    is_live = os.getenv('PARAMOUNT_IS_LIVE') == "TRUE"
    print(f"Paramount enabled: {is_live}")

    def decorator(func):
        endpoint = f'/paramount_functions/{func.__name__}'

        # Define the Flask view function.
        @flask_app.route(endpoint, methods=['POST'])  # TODO: Password protect endpoint by default (+2FA?)
        def view_func():
            # Here we grab the JSON data from the request
            data = request.json

            # In the end separate handling of args/kwargs was not necessary
            # Here we use kwargs syntax for all vars (in order to not pass unnamed vars)
            func_kwargs = data.get('args', {})
            additional_kwargs = data.get('kwargs', {})
            func_kwargs.update(additional_kwargs)

            # Call the actual function with the provided keyword arguments.
            result = func(**func_kwargs)

            # Serialize the result and return as JSON
            serialized_result = serialize_response(result)
            if serialized_result:
                return jsonify(serialized_result)
            else:
                return jsonify({'Error': 'Streaming/SSE unsupported'}), 501  # SSE / streaming unsupported

        def wrapper(*args, **kwargs):
            if not is_live:
                return func(*args, **kwargs)
            else:
                try:
                    func_params = inspect.signature(func).parameters
                    args_names = list(func_params.keys())

                    # Create a dictionary for positional arguments with the prefix 'args_'
                    prefixed_args = {'args__' + key: value for key, value in zip(args_names[:len(args)], args)}

                    # Create a dictionary for keyword arguments with the prefix 'kwargs_'
                    prefixed_kwargs = {'kwargs__' + key: value for key, value in kwargs.items()}

                    # Merge the two dictionaries
                    args_dict = {**prefixed_args, **prefixed_kwargs}

                    start_time = time()
                    result = func(*args, **kwargs)
                    end_time = time()
                except Exception as e:
                    err_tcb = traceback.format_exc()
                    print(f"PARAMOUNT: An error occurred while invoking {func.__name__}: {e}: {err_tcb}")
                    raise  # Re-raise the exception for further handling if necessary

                try:
                    serialized_result = serialize_response(result)

                    if not serialized_result:
                        # to support SSE/streaming, can intercept here and pick out metadata / answer upon finish
                        return result  # SSE / streaming unsupported, forwarding the raw streamer

                    # Get current UTC timestamp
                    timestamp_now = datetime.now(pytz.timezone('UTC')).replace(microsecond=0).isoformat()

                    # Update result data dictionary with invocation information
                    # TODO: In future, could measure CPU/MEM usage per invocation. Skipped for now to not add overhead
                    # Skipped exception logging since functions may have internal handling: difficult to capture
                    result_data = {
                        'paramount__evaluation': "",
                        'paramount__recording_id': str(uuid.uuid4()),
                        'paramount__recorded_at': timestamp_now,
                        'paramount__evaluated_at': timestamp_now,
                        'paramount__function_name': func.__name__,
                        'paramount__execution_time': end_time - start_time,
                        **{f'input_{k}': v for k, v in args_dict.items()}}  # prefix for column name: to differentiate
                    for i, output in enumerate(serialized_result, start=1):
                        if isinstance(output, dict):
                            for key, value in output.items():
                                result_data[f'output__{i}_{key}'] = value
                        else:
                            result_data[f'output__{i}'] = output
                    df = pd.DataFrame([result_data])
                    df['paramount__recorded_at'] = pd.to_datetime(df['paramount__recorded_at'])

                    # Fire and forget for this heavy operation
                    threading.Thread(target=db_instance.create_or_append,
                                     args=(df, 'paramount_data', 'paramount__recording_id'), daemon=True).start()

                except Exception as e:
                    err_tcb = traceback.format_exc()
                    print(f"PARAMOUNT: Wrapper logic issue: {e}: {err_tcb}")

                return result

        return wrapper
    return decorator
