import os
import pandas as pd
from flask import Flask, request, jsonify
from db_connector import db
import traceback
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
db_instance = db.get_database()
app = Flask(__name__)

paramount_identifier_colname = os.getenv('PARAMOUNT_IDENTIFIER_COLNAME')
base_url = os.getenv('FUNCTION_API_BASE_URL')


def err_dict(err_type, err_tcb):
    return {"type": err_type, "stacktrace": err_tcb}


@app.route('/latest', methods=['POST'])
def latest():
    data = request.get_json()
    try:
        ground_truth_table_name = 'paramount_data'
        company_uuid = str(data['company_uuid'])
        evaluated_rows_only = bool(data.get('evaluated_rows_only', False))
        all_rows = not evaluated_rows_only
        response_data = {"result": None}

        if db_instance.table_exists(ground_truth_table_name):
            read_df = db_instance.get_table(ground_truth_table_name, all_rows=all_rows,
                                            identifier_value=company_uuid,
                                            identifier_column_name=paramount_identifier_colname)
            # Convert the DataFrame into a dictionary with records orientation to properly format it for JSON
            data_dict = read_df.to_dict(orient='records')
            response_data["result"] = data_dict
    except Exception as e:
        err_obj = {"error": err_dict(f"{type(e).__name__}: {e}", traceback.format_exc())}
        print(err_obj)
        return jsonify(err_obj), 500

    return jsonify(response_data), 200


@app.route('/submit_evaluations', methods=['POST'])
def submit_evaluations():
    data = request.get_json()
    try:
        ground_truth_table_name = 'paramount_data'
        updated_records = list(data['updated_records'])
        merged = pd.DataFrame(updated_records)
        # TODO: Protect this endpoint with token or other mechanism (similar to company_uuid for /latest endpoint)
        # Currently not done as this db action only succeeds if there is a valid reference to paramount__recording_id
        # Which a potential attacker normally wouldn't have access to
        db_instance.update_ground_truth(merged, ground_truth_table_name)
    except Exception as e:
        err_obj = {"error": err_dict(f"{type(e).__name__}: {e}", traceback.format_exc())}
        print(err_obj)
        return jsonify(err_obj), 500

    return jsonify({"success": True}), 200


@app.route('/infer', methods=['POST'])
def infer():
    data = request.get_json()
    try:
        row = dict(data['record'])
        session_output_cols = list(data['output_cols'])

        args = get_values_dict('input_args__', row)
        kwargs = get_values_dict('input_kwargs__', row)

        result = invoke_via_functions_api(base_url=base_url, func_name=row['paramount__function_name'],
                                          args=args, kwargs=kwargs)

        for output_col in session_output_cols:
            # Match function outputs to column names.
            # For example, This turns 'output__2_answer' into -> (2, answer)
            # Where 2 is the order of received outputs, and answer is the output varname (if exists)
            identifying_info = output_col.split('__')[1].split('_')
            output_index = int(identifying_info[0]) - 1
            output_colname = None if len(identifying_info) < 2 else \
                "_".join(identifying_info[1:])

            data_item = result[output_index] if not output_colname else \
                result[output_index][output_colname]
            testcol = 'test_' + output_col
            result[testcol] = str(data_item)

    except Exception as e:
        err_obj = {"error": err_dict(f"{type(e).__name__}: {e}", traceback.format_exc())}
        print(err_obj)
        return jsonify(err_obj), 500

    return jsonify({"result": result}), 200


@app.route('/similarity', methods=['POST'])
def similarity():
    data = request.get_json()
    try:
        vectorizer = TfidfVectorizer()

        selected_output_var = str(data['output_col_to_be_tested'])
        clean_test_set = pd.DataFrame(dict(data['records']))

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
