#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename


# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# sanity check route
@app.route('/open', methods=['GET'])
def open_door():
    return jsonify(u'Hello World!')

last_sequence = 'imhere'
@app.route('/api/analysis', methods=['GET', 'POST'])
def analysis():
    global last_sequence
    response_object = {'status': 'success'}
    if request.method == 'POST':
        input_method = request.form.get('inputMethod') or request.json.get('inputMethod')
        if input_method == 'file':
            file = request.files['file']
            filename = secure_filename(file.filename)
            file.save('/public/yxshen/DposFinderWeb/server/upload/' + filename)
            last_sequence = 'upload success!!!'
            return jsonify(response_object)
        else:
            post_data = request.get_json()
            last_sequence = post_data.get('inputProtein')
            return jsonify(response_object)
    else:
        response_object['sequence'] = last_sequence
        return jsonify(response_object)

if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run()