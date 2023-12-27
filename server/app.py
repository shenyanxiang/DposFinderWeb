#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
from flask_cors import CORS


# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

RESOURCES = [
    {
        'sn': '100',
        'teacher': 'Mike',
        'learnt': True
    },
    {
        'sn': '101',
        'teacher': 'John',
        'learnt': False
    },
    {
        'sn': '102',
        'teacher': 'Walter',
        'learnt': True
    }
]

@app.route('/resources', methods=['GET', 'POST'])
def all_res():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        RESOURCES.append({
            'sn': post_data.get('sn'),
            'teacher': post_data.get('teacher'),
            'learnt': post_data.get('learnt')
        })
        response_object['message'] = 'Resource added!'
    else:
        response_object['resources'] = RESOURCES
    return jsonify(response_object)

# sanity check route
@app.route('/open', methods=['GET'])
def open_door():
    return jsonify(u'Hello World!')


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run()