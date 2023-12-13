#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from flask_cors import CORS


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


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run()