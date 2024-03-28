import uuid
import toml
import os


def load_config():
    config_path = os.getenv('PARAMOUNT_CONFIG_FILE', 'paramount.toml')  # Default: paramount.toml at root

    # Check if the configuration file exists
    if not os.path.exists(config_path):
        print(f"paramount.toml was not found at current working directory. Creating it with default values.")
        # If the file does not exist, create it with the default configuration
        with open(config_path, 'w') as config_file:
            toml.dump(default_config(), config_file)

    return toml.load(config_path)


def default_config():
    default = {
        "record": {
            "enabled": True,
            "function_url": "http://localhost:9000"
        },
        "db": {
            "type": "csv",
            "postgres": {
                "connection_string": ""
            }
        },
        "api": {
            "endpoint": "http://localhost",
            "port": 9001,
            "split_by_id": False,
            "identifier_colname": ""
        },
        "ui": {
            "meta_cols": [''],
            "input_cols": [''],
            "output_cols": ['']
        }
    }
    return default


def get_result_from_colname(result, output_col):
    '''
    Match function outputs to column names.
    For example, This turns 'output__1_answer' into -> (1, answer)
    Where 1 is the index to use of the returned tuple, and answer is the output varname (if exists)
    :param result:
    :param output_col:
    :return:
    '''
    identifying_info = output_col.split('__')[1].split('_')  # output__1_answer -> [1, answer]
    output_index = int(identifying_info[0]) - 1  # 1 -> 0th index
    output_colname = None if len(identifying_info) < 2 else "_".join(identifying_info[1:])  # answer or blank if no name
    data_item = result[output_index] if not output_colname else result[output_index][output_colname]  # Get the value
    return output_index, output_colname, data_item


def is_valid_uuidv4(uuid_to_test):
    try:
        # Try converting string to UUID object
        uuid_obj = uuid.UUID(uuid_to_test, version=4)

        # Check if generated UUID matches the supplied string
        # and that the version is 4
        return str(uuid_obj) == uuid_to_test and uuid_obj.version == 4
    except (ValueError, AttributeError, TypeError):
        return False
