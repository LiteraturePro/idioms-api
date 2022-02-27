# coding: utf-8
import leancloud
from leancloud import Engine
from leancloud import LeanEngineError
import json
import os
import mysql.connector
from hashlib import sha1
import hmac
import requests
import json
import re
import time
import urllib
import urllib.request

engine = Engine()


@engine.define
def hello(**params):
    if 'name' in params:
        return 'Hello, {}!'.format(params['name'])
    else:
        # return 'Hello, LeanCloud!'
        ss = [{"data":"ss"},{"data":"ee"}]
        print(type(ss))
        dir =  {"data":ss}
        return dir


@engine.define
def Request_sms_code(**params):
    msg = ""
    try:
        leancloud.cloud.request_sms_code('+8619825085100')

    except Exception as e:
        msg = str(e)
    return msg

@engine.define
def Sign_up(**params):
    # # 创建实例
    user = leancloud.User()
    user.set_username(params['name'])
    user.set_password(params['passwd'])
    # 可选
    # user.set_mobile_phone_number(params['name'])
    user.set_email(params['email'])
    # 设置其他属性的方法跟 leancloud.Object 一样
    user.set('gender', 'secret')
    try:
        msg = user.sign_up()
    except Exception as e:
        msg = e
    return str(msg)

@engine.define
def Password_reset(**params):
    # # 创建实例
    user = leancloud.User()
    try:
        msg = user.request_password_reset(params['email'])
    except Exception as e:
        msg = e
    return str(msg)
    
@engine.define
def Feedback_save(**params):
    msg = ""
    # 声明 class
    Feedback = leancloud.Object.extend('Feedback')
    # 构建对象
    feedback = Feedback()
    # 为属性赋值
    feedback.set('text', params['feedback'])
    # 将对象保存到云端
    try:
        msg = feedback.save()
    except Exception as e:
        msg = e
    return str(msg)

@engine.define
def Message_Get(**params):
    # 声明 class
    Message = leancloud.Object.extend('Message')
    query = Message.query
    if 'message' in params:
        if params['message'] == "activity":
            query.equal_to('Class', 'activity')
        else:
            query.equal_to('Class', 'system')
            
        # 获取云端数据
        Message_list = query.find()
        data_list =[]
        for i in Message_list:
            data = {"Time":str(i.created_at)[:19],"Text":i.get('text')}
            data_list.append(data)
        return {"data":data_list}
    else:
        return 'message参数调用错误!'

@engine.define
def Card_Get(**params):
    # 声明 class
    Card = leancloud.Object.extend('Coupon')
    query = Card.query
    if 'UserID' in params:
        query.equal_to('UserID', params['UserID'])
        Card_list = query.find()
        data_list =[]
        for i in Card_list:
            data = {"Time":i.get("Time"),"Quota":i.get("Quota"),"Course":i.get("Course"),"Limit":i.get("Limit"),"Used":i.get("Used")}
            data_list.append(data)
        return {"data":data_list}

    else:
        return 'UserID参数调用错误!'

@engine.define
def Get_News_api(**params):
    data = {}
    data["appkey"] = "76b55ad828c4abe1"
    data["channel"] = "教育" 
    data["num"] = 1
    url_values = urllib.parse.urlencode(data)
    url = "https://api.jisuapi.com/news/get" + "?" + url_values
    request = urllib.request.Request(url)
    result = urllib.request.urlopen(request)
    jsonarr = json.loads(result.read())
    
    # 为 leancloud.Object 创建子类
    News = leancloud.Object.extend('News')
    # 为该类创建一个新实例
    news = News()
    datas = {}
    if jsonarr["status"] == 0:
        # 为属性赋值
        u = re.sub(r"<[^>]*>|\n","",re.sub(r"<[^>]*>|\n\n","",jsonarr["result"]["list"][0]["content"])).replace(' ','')
        news.set('Title', jsonarr["result"]["list"][0]["title"])
        news.set('Image_url', jsonarr["result"]["list"][0]["pic"])
        news.set('Src', jsonarr["result"]["list"][0]["src"])
        news.set('Text', re.sub(r"<[^>]*>|\t","",u))
        news.set('Time', jsonarr["result"]["list"][0]["time"])
    
        # 将对象保存到云端
        news.save()
        datas["result"] = True
        return datas
    else:
        datas["result"] = False
        return datas


@engine.define
def News_Get(**params):
    # 声明 class
    News = leancloud.Object.extend('News')
    query = News.query
    query.ascending('createdAt')
    Card_list = query.find()
    data_list =[]
    data = {}
    for i in Card_list:
        data = {"Title":i.get("Title"),"Text":i.get("Text"),"Time":i.get("Time"),"Src":i.get("Src"),"Image":i.get("Image_url"),"NewsID":i.id}
    data_list.append(data)
    return {"data":data_list}


@engine.define
def Study_Status_Daka_Auto(**params):
    Study_Status = leancloud.Object.extend('Study_Status')
    
    study_status = Study_Status()
    
    Daka_Data = leancloud.Object.extend('Daka_Data')
    
    daka_data = Daka_Data()
    
    
    User = leancloud.Object.extend('_User')
    query = User.query
    
    User_list = query.find()
    
    for user in User_list:
        # 为属性赋值
        study_status.set('Date', time.strftime("%Y-%m-%d", time.localtime()))
        study_status.set('UserID', str(user.id))
        study_status.set('do', False)
        
        # 将对象保存到云端
        study_status.save()
        
        # 为属性赋值
        daka_data.set('UserID', str(user.id))
        daka_data.set('Time', time.strftime("%Y-%m-%d", time.localtime()))
        daka_data.set('Use_time', "00:00:00")
        daka_data.set('Do',False)
        
        # 将对象保存到云端
        daka_data.save()
    
    return {"relust":"done"}
    
   
@engine.define
def Study_Status_Get(**params):
    # 声明 class
    Study_Status = leancloud.Object.extend('Study_Status')
    study_status = Study_Status.query
    study_status.equal_to('UserID', params['UserID'])
    study_status.equal_to('Date', time.strftime("%Y-%m-%d", time.localtime()))
    status_list = study_status.first()
    status = status_list.get("do")
    
    if params['tag'] == 0:
        return {"status":status}
    else:
        Study_Status_Update = Study_Status.create_without_data(status_list.id)
        Study_Status_Update.set('do', True)
        Study_Status_Update.save()
        
        Daka_Data = leancloud.Object.extend('Daka_Data')
        daka_data = Daka_Data.query
        daka_data.equal_to('UserID', params['UserID'])
        daka_data.equal_to('Time', time.strftime("%Y-%m-%d", time.localtime()))
        daka_list = daka_data.first()
        
        Daka_Data_Update = Daka_Data.create_without_data(daka_list.id)
        Daka_Data_Update.set('Do', True)
        Daka_Data_Update.set('Use_time',params['Use_time'] )
        Daka_Data_Update.save()
        
        return {"data":"done"}

@engine.define
def Daka_Data_Get(**params):
    # 声明 class
    data_list = []
    Daka_Data = leancloud.Object.extend('Daka_Data')
    Daka_data = Daka_Data.query
    Daka_data.equal_to('UserID', params['UserID'])
    
    daka_list = Daka_data.find()
    
    for i in daka_list:
        data = {"Time":i.get("Time"),"Use_time":i.get("Use_time"),"Do":i.get("Do")}
        data_list.append(data)
        
    return {"data":data_list}


@engine.define
def Version_Get(**params):
    Version = leancloud.Object.extend('Version')
    query = Version.query
    Version_list = query.find()
    data_list = []
    data = {"Apk_Url":Version_list.get("Apk_url"),"New_Version":Version_list.get("New_Version"),"Old_Version":Version_list.get("Old_Version")}
    data_list.append(data)
    return {"data":data_list}

@engine.define
def Get_all_video_list(**params):
    lists = [5041,5042,5043,5044,5045,5046]
    video_list = []
    video_list_info = {}
    for list_one in lists:
        video_list.append(Dogecloud_api(list_one))
    video_list_info["data"] = video_list
    data_json = json.dumps(video_list_info,ensure_ascii=False)
    return video_list_info
   
@engine.define
def Get_video_list(**params):
    """
    调用 DogeCloud API

    :param api_path:    调用的 API 接口地址，包含 URL 请求参数 QueryString，例如：/console/vfetch/add.json?url=xxx&a=1&b=2
    :param data:        POST 的数据，字典，例如 {'a': 1, 'b': 2}，传递此参数表示不是 GET 请求而是 POST 请求
    :param json_mode:   数据 data 是否以 JSON 格式请求，默认为 false 则使用表单形式（a=1&b=2）

    :type api_path: string
    :type data: dict
    :type json_mode bool

    :return dict: 返回的数据
    """
    
    # 这里替换为你的 DogeCloud 永久 AccessKey 和 SecretKey，可在用户中心 - 密钥管理中查看
    access_key  = "7e4f5fec921e1096"
    secret_key  = "7f0909e24cab5b57f1abbb1c19a54bf7"
    data={}
    json_mode=False
    
    body = ''
    mime = ''
    api_path = "/console/video/list.json?order=name&cid=" + str(params["videocid"]) 
    if json_mode:
        body = json.dumps(data)
        mime = 'application/json'
    else:
        body = urllib.parse.urlencode(data) # Python 2 可以直接用 urllib.urlencode
        mime = 'application/x-www-form-urlencoded'
    
    
    #现在我们要请求这个 API 地址
    # https://api.dogecloud.com/console/video/list.json?order=name&cid=videocid
    #那么此例需要签名的原始字符串是
    sign_str = api_path + "\n" + body
    
    #对字符串进行签名
    signed_data = hmac.new(secret_key.encode('utf-8'), sign_str.encode('utf-8'), sha1)
    
    #获取签名字符串
    sign = signed_data.digest().hex()
    
    #生成最终的 Authorization 请求头值
    authorization = 'TOKEN ' + access_key + ':' + sign
    
    response = requests.post('https://api.dogecloud.com' + api_path, data=body, headers = {
        'Authorization': authorization,
        'Content-Type': mime
    })
    
    videos_info = {}
    
    video_list = []
    
    for i in response.json()["data"]["videos"]:
        video_list.append(i["vcode"])
    
    
    
    # print(response.json()["data"]["videos"][0]["thumb"])
    videos_info["data"] = video_list
    return videos_info

    
def Dogecloud_api(videocid):
    """
    调用 DogeCloud API

    :param api_path:    调用的 API 接口地址，包含 URL 请求参数 QueryString，例如：/console/vfetch/add.json?url=xxx&a=1&b=2
    :param data:        POST 的数据，字典，例如 {'a': 1, 'b': 2}，传递此参数表示不是 GET 请求而是 POST 请求
    :param json_mode:   数据 data 是否以 JSON 格式请求，默认为 false 则使用表单形式（a=1&b=2）

    :type api_path: string
    :type data: dict
    :type json_mode bool

    :return dict: 返回的数据
    """
    
    # 这里替换为你的 DogeCloud 永久 AccessKey 和 SecretKey，可在用户中心 - 密钥管理中查看
    access_key  = "7e4f5fec921e1096"
    secret_key  = "7f0909e24cab5b57f1abbb1c19a54bf7"
    data={}
    json_mode=False
    
    body = ''
    mime = ''
    api_path = "/console/video/list.json?order=name&cid=" + str(videocid) 
    if json_mode:
        body = json.dumps(data)
        mime = 'application/json'
    else:
        body = urllib.parse.urlencode(data) # Python 2 可以直接用 urllib.urlencode
        mime = 'application/x-www-form-urlencoded'
    
    
    #现在我们要请求这个 API 地址
    # https://api.dogecloud.com/console/video/list.json?order=name&cid=videocid
    #那么此例需要签名的原始字符串是
    sign_str = api_path + "\n" + body
    
    #对字符串进行签名
    signed_data = hmac.new(secret_key.encode('utf-8'), sign_str.encode('utf-8'), sha1)
    
    #获取签名字符串
    sign = signed_data.digest().hex()
    
    #生成最终的 Authorization 请求头值
    authorization = 'TOKEN ' + access_key + ':' + sign
    
    response = requests.post('https://api.dogecloud.com' + api_path, data=body, headers = {
        'Authorization': authorization,
        'Content-Type': mime
    })
    
    video_list = []
    
    videos_info = {}
    # print(response.json()["data"]["count"])
    videos_info["count"] = response.json()["data"]["count"]
    
    # print(response.json()["data"]["filters"][0]["text"][3:-3])
    videos_info["name"] = response.json()["data"]["filters"][0]["text"][3:-3]
    
    # print(response.json()["data"]["videos"])
    for i in response.json()["data"]["videos"]:
        video_list.append(i["vid"])
    
    # print(video_list)
    videos_info["video_list"] = video_list
    
    # print(response.json()["data"]["videos"][0]["thumb"])
    videos_info["thumb"] = response.json()["data"]["videos"][0]["thumb"]
    
    videos_info["videocid"] =  videocid
    
    return videos_info

@engine.define
def Comment_Get(**params):
    if 'NewsID' in params:
        Commentlist = []
        # 声明 class
        Comment = leancloud.Object.extend('Comment')
        query = Comment.query
        query.equal_to('NewsID', params['NewsID'])
        Comment_list = query.find()
        
        for i in Comment_list:
            Comment_reply = leancloud.Object.extend('Comment_reply')
            query2 = Comment_reply.query
            query2.equal_to('Comment_replyID', i.id)
            Comment_reply_list = query2.find()
            Replylist = []
            for j in Comment_reply_list:
                ReplyData = {
                    "nickName": j.get("nickName"),
                    "userLogo": j.get("userLogo"),
                    "id": j.id,
                    "commentId": j.get("Comment_replyID"),
                    "content": j.get("content"),
                    "status": j.get("status"),
                    "createDate": str(j.created_at)[:10]
                }
                Replylist.append(ReplyData)
            CommentData = {
                "id": i.id,
                "NewsId": i.get("NewsID"),
        		"nickName": i.get("nickName"),
        		"userLogo": i.get("userLogo"),
        		"content": i.get("content"),
        		"imgId": "xcclsscrt0tev11ok364",
        		"replyTotal": len(Comment_reply_list),
        		"createDate":str(i.created_at)[:10],
        		"replyList": Replylist
            }
            #print(CommentData)
            Commentlist.append(CommentData)  
        data = {
            "code": 200,
        	"message": "查看评论成功",
        	"data":{
                "total": len(Comment_list),
        		"list":Commentlist
            }
        }
        
        data_json = json.dumps(data,ensure_ascii=False)
        return data
    else:
        return 'NewsID参数调用错误!'

@engine.define
def Comment_save(**params):
    if 'NewsId' in params:
        User = leancloud.Object.extend('UserLogo')
        User_query = User.query
        User_query.equal_to('UserName', params['Username'])
        User_list = User_query.first()

        # 声明 class
        Comment = leancloud.Object.extend('Comment')
        
        # 构建对象
        comment = Comment()
        # 为属性赋值
        comment.set('NewsID', params['NewsId'])
        comment.set('content', params['content'])
        comment.set('nickName', params['Username'])
        comment.set('userLogo', User_list.get("LogoUrl"))
        # 将对象保存到云端
        try:
            msg = comment.save()
        except Exception as e:
            msg = e
        return str(msg)
    else:
        return 'CommentData参数调用错误!'

@engine.define
def Commentreply_save(**params):
    if 'Comment_replyID' in params:
        # 声明 class
        User = leancloud.Object.extend('UserLogo')
        User_query = User.query
        User_query.equal_to('UserName', params['Username'])
        User_list = User_query.first()
        
        
        Commentreply = leancloud.Object.extend('Comment_reply')
        # 构建对象
        commentreply = Commentreply()
        # 为属性赋值
        commentreply.set('status', "01")
        commentreply.set('Comment_replyID', params['Comment_replyID'])
        commentreply.set('content', params['content'])
        commentreply.set('nickName', params['Username'])
        commentreply.set('userLogo', User_list.get("LogoUrl"))
        # 将对象保存到云端
        try:
            msg = commentreply.save()
        except Exception as e:
            msg = e
        return str(msg)

    else:
        return 'CommentreplyData参数调用错误!'

@engine.define
def Get_word_do(**params):
    data = {}
    # 声明 class
    Study_word_tag = leancloud.Object.extend('Study_word_tag')
    study_word = Study_word_tag.query
    study_word.equal_to('UserID', params['UserID'])
    tag_list = study_word.first()
    tag2 = tag_list.get("id")
    data["no"] = 30862 - tag2
    data["do_bili"] = round(tag2/30862*100, 2)  
    
    return data


@engine.define
def DB_Get_word(**params):
    result = ''
    host = 'cdb-9f2p00jq.cd.tencentcdb.com'
    port = '10104'
    user = 'literature'
    password = 'yxl981204@'
    
    # 声明 class
    Study_word_tag = leancloud.Object.extend('Study_word_tag')
    study_word = Study_word_tag.query
    study_word.equal_to('UserID', params['UserID'])
    tag_list = study_word.first()
    tag2 = tag_list.get("id")
    try:
        lists =[]
        
        cnx = mysql.connector.connect(
        user=user, password=password, database='idioms', host=host, port=port)
        cursor = cnx.cursor()
        if params['tag'] == 0:
            cursor.execute("select * from idiom limit " + str(tag2-20) +","+ params['count'] + "")
            for rows in cursor:
                list_data ={}
                list_data["uuid"] = rows[0]
                list_data["word"] = rows[1]
                list_data["pinyin"] = rows[2]
                list_data["derivation"] = rows[3]
                list_data["explanation"] = rows[4]
                list_data["example"] = rows[5]
                list_data["abbreviation"] = rows[6]
                list_data["pinyin_r"] = rows[7]
                list_data["first"] = rows[8]
                list_data["last"] = rows[9]
                lists.append(list_data)
        elif params['tag'] == 1:
            cursor.execute("select * from idiom limit " + str(tag2) +","+ str(params['count']) + "")
            for rows in cursor:
                list_data ={}
                list_data["uuid"] = rows[0]
                list_data["word"] = rows[1]
                list_data["pinyin"] = rows[2]
                list_data["derivation"] = rows[3]
                list_data["explanation"] = rows[4]
                list_data["example"] = rows[5]
                list_data["abbreviation"] = rows[6]
                list_data["pinyin_r"] = rows[7]
                list_data["first"] = rows[8]
                list_data["last"] = rows[9]
                lists.append(list_data)
        elif params['tag'] == 2:
            if tag2 >= params['count']:
                cursor.execute("select * from idiom limit " + str(tag2-params['count']) +","+ str(params['count']*2) + "")
            else:
                cursor.execute("select * from idiom limit " + str(0) +","+ str(params['count']*2) + "")
            for rows in cursor:
                list_data ={}
                list_data["uuid"] = rows[0]
                list_data["word"] = rows[1]
                list_data["pinyin"] = rows[2]
                list_data["derivation"] = rows[3]
                list_data["explanation"] = rows[4]
                list_data["example"] = rows[5]
                list_data["abbreviation"] = rows[6]
                list_data["pinyin_r"] = rows[7]
                list_data["first"] = rows[8]
                list_data["last"] = rows[9]
                lists.append(list_data)
                
        else:
            cursor.execute("select * from idiom")
            for rows in cursor:
                list_data ={}
                list_data["uuid"] = rows[0]
                list_data["word"] = rows[1]
                list_data["pinyin"] = rows[2]
                list_data["derivation"] = rows[3]
                list_data["explanation"] = rows[4]
                list_data["example"] = rows[5]
                list_data["abbreviation"] = rows[6]
                list_data["pinyin_r"] = rows[7]
                list_data["first"] = rows[8]
                list_data["last"] = rows[9]
                lists.append(list_data)
            
        return {"data":lists}
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
        return "err"
      
@engine.define
def DB_Get_riddle(**params):
    result = ''
    host = 'cdb-9f2p00jq.cd.tencentcdb.com'
    port = '10104'
    user = 'literature'
    password = 'yxl981204@'
    try:
        lists =[]
        cnx = mysql.connector.connect(
        user=user, password=password, database='idioms', host=host, port=port)
        cursor = cnx.cursor()
        cursor.execute('SELECT * from riddle ORDER BY RAND() limit 1')
        for row in cursor:
            lists = row 
            
        return {"data":lists}
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
        return "err"

@engine.define
def DB_Get_word_url(**params):
    result = ''
    host = 'cdb-9f2p00jq.cd.tencentcdb.com'
    port = '10104'
    user = 'literature'
    password = 'yxl981204@'
    try:
        lists =[]
        cnx = mysql.connector.connect(
        user=user, password=password, database='idioms', host=host, port=port)
        cursor = cnx.cursor()
        cursor.execute('SELECT * from word_url ORDER BY RAND() limit 1')
        for row in cursor:
            lists = row 
            
        return {"data":lists}
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
        return "err"

@engine.define
def DB_Get_couplet(**params):
    result = ''
    host = 'cdb-9f2p00jq.cd.tencentcdb.com'
    port = '10104'
    user = 'literature'
    password = 'yxl981204@'
    try:
        lists =[]
        cnx = mysql.connector.connect(
        user=user, password=password, database='idioms', host=host, port=port)
        cursor = cnx.cursor()
        cursor.execute('SELECT * from couplet ORDER BY RAND() limit 1')
        for row in cursor:
            lists = row 
        # str = lists[0]
        return {"data":str(lists[0]).split(' --- ')}
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
        return "err"

@engine.define
def DB_Get_fun(**params):
    result = ''
    host = 'cdb-9f2p00jq.cd.tencentcdb.com'
    port = '10104'
    user = 'literature'
    password = 'yxl981204@'
    try:
        lists =[]
        cnx = mysql.connector.connect(
        user=user, password=password, database='idioms', host=host, port=port)
        cursor = cnx.cursor()
        cursor.execute('SELECT * from ' + params["dbname"]+ ' limit 50')
        for row in cursor:
            lists.append(row[0])
        # str = lists[0]
        return {"data":lists}
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
        return "err"
        
@engine.define
def Get_idioms_info(**params):
    # 查询是否存在这个成语
    if Get_idioms_info_api(params["word"]) == True or Get_idioms_info_db(params["word"]):
        return {"result": True}
    else:
        return {"result": False}
        
@engine.define
def Get_one_word(**params):
    result = ''
    host = 'cdb-9f2p00jq.cd.tencentcdb.com'
    port = '10104'
    word = ''
    info = {}
    user = 'literature'
    password = 'yxl981204@'
    try:
        cnx = mysql.connector.connect(
        user=user, password=password, database='idioms', host=host, port=port)
        cursor = cnx.cursor()
        cursor.execute('SELECT * from idiom ORDER BY RAND() limit 1')
        for row in cursor:
            word = row[1]
        info["word"] = word
        info["words"] = Get_idioms_search_api(word[-1])
        return info
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
        return "err"
    
    
def Get_idioms_info_api(word):
    data = {}
    data["appkey"] = "76b55ad828c4abe1"
    data["chengyu"] = word
     
    url_values = urllib.parse.urlencode(data)
    url = "https://api.jisuapi.com/chengyu/detail" + "?" + url_values
    request = urllib.request.Request(url)
    result = urllib.request.urlopen(request)
    jsonarr = json.loads(result.read())
     
    if jsonarr["status"] == 0:
        return True
    else:
        return False

def Get_idioms_info_db(word):
    result = ''
    host = 'cdb-9f2p00jq.cd.tencentcdb.com'
    port = '10104'
    user = 'literature'
    password = 'yxl981204@'
    try:
        lists =[]
        cnx = mysql.connector.connect(
        user=user, password=password, database='idioms', host=host, port=port)
        cursor = cnx.cursor()
        cursor.execute("select * from idiom where word = '" + word + "'")
        for row in cursor:
            lists.append(row[0])
        if len(lists) == 0:
            return False
        else:
            return True
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
        return "err"
        
def Get_idioms_search_api(word):
    data = {}
    data["appkey"] = "76b55ad828c4abe1"
    data["keyword"] = word
     
    url_values = urllib.parse.urlencode(data)
    url = "https://api.jisuapi.com/chengyu/search" + "?" + url_values
    request = urllib.request.Request(url)
    result = urllib.request.urlopen(request)
    jsonarr = json.loads(result.read())
     
    if jsonarr["status"] == 0:
        result = jsonarr["result"]
        word_list = []
        words = {}
        for val in result:
            if val["name"][0] == word:
                print (val["name"])
                word_list.append(val["name"])
        return word_list
    else:
        word_list = []
        return word_list