from flask import Flask, jsonify
app = Flask(__name__)

'''
Evaluate page:
    GET /latest - get latest 100 as JSON
    POST /evals - write any chosen evals to those, merging on ID

Optimize page:
    GET /evals - get evals (batched on evaluated_at ?)
    POST /test - param to vary, new value, param to test -> Simil scores
'''


@app.route('/latest', methods=['GET'])
def get_latest():
    return jsonify({"latest": "test"}), 200


@app.route('/evals', methods=['POST'])
def post_evals():
    return jsonify({"evals": "test"}), 200


@app.route('/evals', methods=['GET'])
def get_evals():
    return jsonify({"evals": "test"}), 200


@app.route('/test', methods=['POST'])
def post_test():
    return jsonify({"results": []}), 200
