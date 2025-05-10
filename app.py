from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory key-value storage
data_store = {}

@app.route("/fetch", methods=["POST"])
def fetch():
    key = request.json.get("key")
    value = data_store.get(key, "No info found.")

    # Truncate if the response is too large
    if isinstance(value, str) and len(value) > 1000:
        value = value[:1000] + " ... [truncated]"

    return jsonify({"result": value})

@app.route("/add", methods=["POST"])
def add():
    key = request.json.get("key")
    value = request.json.get("value")
    data_store[key] = value
    return jsonify({"result": "Info added."})

@app.route("/modify", methods=["POST"])
def modify():
    key = request.json.get("key")
    if key not in data_store:
        return jsonify({"result": "Key not found."})
    new_value = request.json.get("value")
    data_store[key] = new_value
    return jsonify({"result": "Info updated."})

@app.route("/delete", methods=["POST"])
def delete():
    key = request.json.get("key")
    if key in data_store:
        del data_store[key]
        return jsonify({"result": "Info deleted."})
    return jsonify({"result": "Key not found."})

@app.route('/list_keys', methods=['GET'])
def list_keys():
    keys = list(knowledge_base.keys())
    return jsonify({"keys": keys})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
