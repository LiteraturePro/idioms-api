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
    
@app.route("/api")
def api():
    config = {
        'url': 'https://sts.tencentcloudapi.com/',
        # 域名，非必须，默认为 sts.tencentcloudapi.com
        'domain': 'sts.tencentcloudapi.com', 
        # 临时密钥有效时长，单位是秒
        'duration_seconds': 1800,
        'secret_id': os.environ['COS_SECRET_ID'],
        # 固定密钥
        'secret_key': os.environ['COS_SECRET_KEY'],
        # 设置网络代理
        # 'proxy': {
        #     'http': 'xx',
        #     'https': 'xx'
        # },
        # 换成你的 bucket
        'bucket': 'cloud-1258693536',
        # 换成 bucket 所在地区
        'region': 'ap-shanghai',
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        
        'allow_prefix': 'exampleobject', 
        # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            # 简单上传
            'name/cos:PutObject',
            'name/cos:PostObject',
            # 分片上传
            'name/cos:InitiateMultipartUpload',
            'name/cos:ListMultipartUploads',
            'name/cos:ListParts',
            'name/cos:UploadPart',
            'name/cos:CompleteMultipartUpload'
        ],

    }

    try:
        sts = Sts(config)
        response = sts.get_credential()
        return json.dumps(dict(response), indent=4)
    except Exception as e:
        return str(e)

@app.route('/version',methods=['POST','GET'])
def version():
    # 声明 class
    File = leancloud.Object.extend('_File')
    file = File.query
    file.descending('createdAt')
    file_list = file.first()
    
    
    Version = leancloud.Object.extend('Version')
    version = Version.query
    version_list = version.first()
    print(version_list.id)
    
    Version_Update = Version.create_without_data(version_list.id)
    Version_Update.set('Apk_url', file_list.get("url"))
    Version_Update.set('Version',file_list.get("name")[8:13] )
    Version_Update.save()
    
    return "done"

@app.route('/getversion',methods=['POST','GET'])
def getversion():
    # 声明 class
    File = leancloud.Object.extend('_File')
    file = File.query
    file.descending('createdAt')
    file.limit(2)
    file_list = file.find()
    url =""
    for liste in file_list:
        url = liste.get("url")
    
    return url


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
