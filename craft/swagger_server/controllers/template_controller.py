import os
from flask import request, jsonify
from . import *

def post_template():
    try:
        file = request.files['file']
        if file:
            file.save(os.path.join(template_folder, file.filename))
            print(file.filename)
            return jsonify(message=f"Template uploaded, it is available at http://{server}:{template_port}"), 200
        else:
            return jsonify(error="File not provided"), 400
    except Exception as e:
        return "Failed to accept template POST request. Error:{}".format(str(e)), 500

