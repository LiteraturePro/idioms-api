# coding: utf-8
import sys
from datetime import datetime
import json
import leancloud
from flask import Flask, jsonify, request
from flask import render_template
from flask_sockets import Sockets
from leancloud import LeanCloudError
from leancloud import cloud
import os
import mysql.connector
app = Flask(__name__)
sockets = Sockets(app)
app.config['JSON_AS_ASCII'] = False



# routing
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/time')
def time():
    return cloud.run('hello', name='夏洛特烦恼')


@app.route('/db')
def db():
    result = ''
    host = os.environ['DB_Host']
    port = os.environ['DB_Port']
    user = os.environ['DB_User']
    password = os.environ['DB_Password']
    try:
        lists =[]
        cnx = mysql.connector.connect(
        user=user, password=password, database='idioms', host=host, port=port)
        cursor = cnx.cursor()
        cursor.execute('SELECT * from word_url limit 1')
        for row in cursor:
            lists.append(row)
            
        return jsonify(lists)
    except mysql.connector.Error as err:
        if err.errno != 0:
            print(err)
        else:
            cursor = cnx.cursor()
            cursor.execute('SELECT 1 + 1 AS solution')
            for row in cursor:
                result = "The solution is {}".format(row[0])
    
        cursor.close()
        cnx.close()
        return jsonify(err)
    
@app.route('/api')
def api():
    return str(datetime.now())

@sockets.route('/echo')
def echo_socket(ws):
    while True:
        message = ws.receive()
        ws.send(message)


# REST API example
class BadGateway(Exception):
    status_code = 502

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_json(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return jsonify(rv)


class BadRequest(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_json(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return jsonify(rv)


@app.errorhandler(BadGateway)
def handle_bad_gateway(error):
    response = error.to_json()
    response.status_code = error.status_code
    return response


@app.errorhandler(BadRequest)
def handle_bad_request(error):
    response = error.to_json()
    response.status_code = error.status_code
    return response


@app.route('/api/python-version', methods=['GET'])
def python_version():
    return jsonify({"python-version": sys.version})


@app.route('/api/todos', methods=['GET', 'POST'])
def todos():
    if request.method == 'GET':
        try:
            todo_list = leancloud.Query(leancloud.Object.extend('Todo')).descending('createdAt').find()
        except LeanCloudError as e:
            if e.code == 101:  # Class does not exist on the cloud.
                return jsonify([])
            else:
                raise BadGateway(e.error, e.code)
        else:
            return jsonify([todo.dump() for todo in todo_list])
    elif request.method == 'POST':
        try:
            content = request.get_json()['content']
        except KeyError:
            raise BadRequest('''receives malformed POST content (proper schema: '{"content": "TODO CONTENT"}')''')
        todo = leancloud.Object.extend('Todo')()
        todo.set('content', content)
        try:
            todo.save()
        except LeanCloudError as e:
            raise BadGateway(e.error, e.code)
        else:
            return jsonify(success=True)
