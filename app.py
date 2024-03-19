from flask import Flask, request
from flask_cors import CORS  # Import the CORS module
import subprocess

app = Flask(__name__)
CORS(app)  # Allow CORS for all routes

@app.route('/run-script', methods=['POST'])
def run_script():
    path = request.json['path']
    result = subprocess.run(["python", path], capture_output=True, text=True)
    return {'result': result.stdout}