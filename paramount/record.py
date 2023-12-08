import pandas as pd
import json
import inspect
import os
from datetime import datetime
import pytz


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

        # Get current UTC timestamp
        timestamp_now = datetime.now(pytz.timezone('UTC')).replace(microsecond=0).isoformat()

        # Update result data dictionary with timestamp
        result_data = {
            'paramount_timestamp': timestamp_now,
            'paramount_ground_truth': False,
            **args_dict}
        for i, output in enumerate(serialized_result, start=1):
            if isinstance(output, dict):
                for key, value in output.items():
                    result_data[f'output_{i}_{key}'] = value
            else:
                result_data[f'output_{i}'] = output
        df = pd.DataFrame([result_data])
        df['paramount_timestamp'] = pd.to_datetime(df['paramount_timestamp'])
        df['paramount_ground_truth'] = df['paramount_ground_truth'].astype('bool')

        # Determine the filename based on the current date
        filename = f"paramount_data_{datetime.utcnow().strftime('%Y_%m_%d')}.csv"

        # Check if the file exists, and if not, create it with header, else append without header
        if not os.path.isfile(filename):
            df.to_csv(filename, mode='a', index=False)
        else:
            df.to_csv(filename, mode='a', index=False, header=False)

        return result

    return wrapper
