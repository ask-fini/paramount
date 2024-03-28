import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from paramount.server.db_connector import db
import traceback
import requests
import uuid
import pytz
import threading
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from paramount.server.library_functions import get_result_from_colname, load_config
from datetime import datetime


app = Flask(__name__, static_folder='../client/dist', static_url_path='/')

config = load_config()

paramount_identifier_colname = config['api']['identifier_colname']
base_url = config['record']['function_url']
db_type = config['db']['type']
split_by_id = config['api']['split_by_id']

connection_string = ""
if db_type in config['db']:
    db_config = config['db'].get(db_type)
    if db_config and 'connection_string' in db_config:
        connection_string = db_config['connection_string']

db_instance = db.get_database(db_type, connection_string)

print(f"paramount_identifier_colname: {paramount_identifier_colname}")
print(f"Function replay base_url: {base_url}")
print(f"DB connection string length: {len(connection_string)} characters")  # Don't print the actual str: security risk
print(f"db type: {db_type}")
print(f"split by id: {split_by_id}")


def err_dict(err_type, err_tcb):
    return {"type": err_type, "stacktrace": err_tcb}


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "OK", "time": datetime.now()}), 200


# Entry route for the client
@app.route("/")
def serve():
    return send_from_directory(app.static_folder, "index.html")


@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)


# For disabling CORS
@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    header['Access-Control-Allow-Methods'] = 'OPTIONS, HEAD, GET, POST, DELETE, PUT'
    return response


@app.route('/api/config', methods=['GET'])
def get_client_config():
    try:
        ui_config = config['ui']
        return jsonify(ui_config), 200
    except Exception as e:
        err_obj = {"error": err_dict(f"{type(e).__name__}: {e}", traceback.format_exc())}
        return jsonify(err_obj), 500


def check_id_splitter(data):
    if split_by_id:
        if 'identifier_value' in data:
            identifier_value = str(data['identifier_value'])
        else:
            raise ValueError('split_by_id is True, so you must provide identifier_value to split by in json body')
        determined_id_colname = paramount_identifier_colname
    else:
        identifier_value = None
        determined_id_colname = None
    return identifier_value, determined_id_colname


@app.route('/api/latest', methods=['POST'])
def latest():
    data = request.get_json()
    try:
        ground_truth_table_name = 'paramount_data'

        identifier_value, determined_id_colname = check_id_splitter(data)

        evaluated_rows_only = bool(data.get('evaluated_rows_only', False))
        recording_ids = list(data.get('recording_ids', []))
        response_data = {"result": None, "column_order": []}

        # TODO: Only get non-error rows. Possible by passing "output cols that are supposed to be non-null" to read_df
        # eg. PARAMOUNT_OUTPUT_COLS env var, to get_recordings() fct: can tell _and() clause that cols must be non-null
        if db_instance.table_exists(ground_truth_table_name):
            read_df = db_instance.get_recordings(ground_truth_table_name, evaluated_rows_only=evaluated_rows_only,
                                                 split_by_id=split_by_id,
                                                 identifier_value=identifier_value,
                                                 identifier_column_name=determined_id_colname,
                                                 recording_ids=recording_ids)
            # Convert the DataFrame into a dictionary with records orientation to properly format it for JSON
            # Doing None Cleaning: Otherwise None becomes 'None' and UUID upsert fails (UUID col does not accept 'None')
            # TODO: Ideally, need for cleaning would be prevented upstream, so that 'None' never happens to begin with..
            data_dict = [{k: None if v is None or v == "None" else v for k, v in record.items()}
                         for record in read_df.to_dict(orient='records')]
            response_data["result"] = data_dict
            response_data["column_order"] = read_df.columns.tolist()
    except Exception as e:
        err_obj = {"error": err_dict(f"{type(e).__name__}: {e}", traceback.format_exc())}
        print(err_obj)
        return jsonify(err_obj), 500

    return jsonify(response_data), 200


@app.route('/api/submit_evaluations', methods=['POST'])
def submit_evaluations():
    data = request.get_json()
    try:
        # Save updated recordings
        ground_truth_table_name = 'paramount_data'
        updated_records = list(data['updated_records'])
        merged = pd.DataFrame(updated_records)
        # TODO: Protect this endpoint with token or other mechanism (similar to company_uuid for /latest endpoint)
        # Currently not done as this db action only succeeds if there is a valid reference to paramount__recording_id
        # Which a potential attacker normally wouldn't have access to
        db_instance.update_ground_truth(merged, ground_truth_table_name)

        # Save new session
        sessions_table_name = 'paramount_sessions'
        session_accuracy = float(data.get('session_accuracy', 0))
        if session_accuracy > 1 or session_accuracy < 0:
            raise ValueError('Accuracy must be a float value between 0 and 1 inclusive')
        session_name = str(data.get('session_name', "Unnamed session"))
        recorded_ids = list(data['recorded_ids'])
        session_id = str(uuid.uuid4())
        timestamp_now = datetime.now(pytz.timezone('UTC')).replace(microsecond=0).isoformat()
        id_splitter = None
        if split_by_id:
            id_splitter = str(data['identifier_value'])
        session_data = {
            'paramount__session_id': session_id,
            'paramount__session_timestamp': timestamp_now,
            'paramount__session_recorded_ids': recorded_ids,
            'paramount__session_accuracy': session_accuracy,
            'paramount__session_name': session_name,
            'paramount__session_splitter_id': id_splitter
        }
        df = pd.DataFrame([session_data])
        ts_col = 'paramount__session_timestamp'
        df[ts_col] = pd.to_datetime(df[ts_col])  # To ensure correct dtype: timestamptz, upon table creation
        # Fire and forget for this heavy operation
        threading.Thread(target=db_instance.create_or_append,
                         args=(df, sessions_table_name, 'paramount__session_id'), daemon=True).start()
        print(f"Saving session {session_id} with acc: {round(100*session_accuracy,1)}%, and splitter id: {id_splitter}")
    except Exception as e:
        err_obj = {"error": err_dict(f"{type(e).__name__}: {e}", traceback.format_exc())}
        print(err_obj)
        return jsonify(err_obj), 500

    return jsonify({"success": True}), 200


@app.route('/api/get_sessions', methods=['POST'])
def get_sessions():
    data = request.get_json()
    try:
        sessions_table_name = 'paramount_sessions'
        identifier_value, _ = check_id_splitter(data)
        all_sessions = db_instance.get_sessions(sessions_table_name, split_by_id=split_by_id,
                                                identifier_value=identifier_value,
                                                identifier_column_name='paramount__session_splitter_id')
    except Exception as e:
        err_obj = {"error": err_dict(f"{type(e).__name__}: {e}", traceback.format_exc())}
        print(err_obj)
        return jsonify(err_obj), 500

    return jsonify(all_sessions.to_dict(orient='records')), 200


@app.route('/api/infer', methods=['POST'])
def infer():
    data = request.get_json()
    print(data)
    try:
        row = dict(data['record'])
        session_output_cols = list(data['output_cols'])

        args = get_values_dict('input_args__', row)
        kwargs = get_values_dict('input_kwargs__', row)

        print("\n\n", 'args', args, 'kwargs', kwargs, 'baseurl', base_url, 'row', row['paramount__function_name'], "\n\n")

        result = invoke_via_functions_api(base_url=base_url, func_name=row['paramount__function_name'],
                                          args=args, kwargs=kwargs)

        for output_col in session_output_cols:
            output_index, _, data_item = get_result_from_colname(result, output_col)
            testcol = 'test_' + output_col
            result[output_index][testcol] = str(data_item)

    except Exception as e:
        err_obj = {"error": err_dict(f"{type(e).__name__}: {e}", traceback.format_exc())}
        print(err_obj)
        return jsonify(err_obj), 500

    return jsonify({"result": result}), 200


@app.route('/api/similarity', methods=['POST'])
def similarity():
    data = request.get_json()
    try:
        vectorizer = TfidfVectorizer()

        selected_output_var = str(data['output_col_to_be_tested'])
        clean_test_set = pd.DataFrame(data['records'])

        # To ensure comparability
        clean_test_set[selected_output_var] = clean_test_set[selected_output_var].astype(str)
        clean_test_set['test_' + selected_output_var] = \
            clean_test_set['test_' + selected_output_var].astype(str)

        vectorizer.fit_transform(clean_test_set[selected_output_var])

        # Transform both the ground truth and test set data (columns 1 and 2)
        tfidf_matrix_ground_truth = vectorizer.transform(clean_test_set[selected_output_var])
        tfidf_matrix_test_set = vectorizer.transform(clean_test_set['test_' + selected_output_var])

        # Calculate cosine similarity between the corresponding rows in columns 1 and 2
        cosine_similarities = [cosine_similarity(tfidf_matrix_ground_truth[i:i + 1],
                                                 tfidf_matrix_test_set[i:i + 1])[0][0]
                               for i in range(tfidf_matrix_ground_truth.shape[0])]
    except Exception as e:
        err_obj = {"error": err_dict(f"{type(e).__name__}: {e}", traceback.format_exc())}
        print(err_obj)
        return jsonify(err_obj), 500

    return jsonify({"result": cosine_similarities}), 200


def invoke_via_functions_api(func_name, base_url, args=None, kwargs=None):
    # construct the endpoint based on the function name
    endpoint = f'{base_url}/paramount_functions/{func_name}'
    data_payload = {}
    if args is not None:
        data_payload['args'] = args
    if kwargs is not None:
        data_payload['kwargs'] = kwargs
    try:
        # Send the POST request to the endpoint with JSON payload
        response = requests.post(endpoint, json=data_payload)

        # Check if the request was successful
        if response.status_code == 200:
            # Handle successful response
            response = response.json()
        else:
            # Handle errors
            err = (response.status_code, response.text)
            print("Error:", err)
            response = err
    except requests.exceptions.RequestException as e:
        # Handle request exceptions (e.g., connection errors)
        print("Request failed:", e)
        response = e

    return response


def get_values_dict(col_prefix, row_dict):
    # row_dict is a dictionary where keys are column names (from DataFrame's columns)
    # and values are the corresponding values of the row
    vals = {col.replace(col_prefix, ''): row_dict[col] for col in row_dict.keys() if col.startswith(col_prefix)}
    return vals
