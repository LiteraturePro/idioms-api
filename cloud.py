# coding: utf-8
import leancloud
from leancloud import Engine
from leancloud import LeanEngineError
import json
import os
import mysql.connector

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
def News_Get(**params):
    # 声明 class
    News = leancloud.Object.extend('News')
    query = News.query
    Card_list = query.first()
    data_list =[]
    
    File = leancloud.Object.extend('_File')
    File_query = File.query
    File_query.equal_to('name', Card_list.get("Image").name)
    File_list = File_query.first()
    
    data = {"Title":Card_list.get("Title"),"Text":Card_list.get("Text"),"Time":str(Card_list.created_at)[:10],"Image":File_list.get("url"),"NewsID":Card_list.id}
    data_list.append(data)
    return {"data":data_list}

@engine.define
def Version_Get(**params):
    Version = leancloud.Object.extend('Version')
    query = Version.query
    Version_list = query.first()
    data_list = []
    data = {"Apk_Url":Version_list.get("Apk_url"),"New_Version":Version_list.get("New_Version"),"Old_Version":Version_list.get("Old_Version")}
    data_list.append(data)
    return {"data":data_list}
    
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
def db(**params):
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
        cursor.execute('SELECT * from word_url limit 1')
        for row in cursor:
            lists.append(row)
            
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