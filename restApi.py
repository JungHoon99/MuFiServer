#from sqlite3 import Timestamp
from urllib import request
from flask import Flask, request, send_file
from flask_restx import Resource, Api
#from pymysql import NULL
from werkzeug.serving import WSGIRequestHandler
from dbpy import MufiData, crypto
from TossPay import tosspay
import json
import socket 
from flask import make_response
from werkzeug.utils import secure_filename
import time
from datetime import datetime
import base64

WSGIRequestHandler.protocol_version = "HTTP/1.1"

app = Flask(__name__)
app.config['RESTFUL_JSON'] = {'ensure_ascii' : False}
app.config['JSON_AS_ASCII'] = False
api = Api(app)

# 개발자 : 정훈
# 개발 시작일 : 2022.08.18
# 간단한 설명 : 무피 앱에서 사용자의 아이디와 비밀번호를 통해 로그인 시 작동
@api.route('/mufiApp/app/login/<string:id>/<string:pw>')  # url pattern으로 name 설정
class mufiApp(Resource):
    def get(self, id, pw):
        LoginSuccess = 0
        user={'userid' : 0, 'userpw' : 0, 'name' : 0, 'phone' : 0, 'birth' : 0, 'gender' : 0}
        md = MufiData()
        cry = crypto()
        pwlist = md.selectdb("select * from appuser where userid = '"+ id +"';")
        for i in pwlist:
            if(cry.decoded(i['userpw']) == pw):
                LoginSuccess = 1
                user = i
        name = user['name']
        result = json.dumps({"isLoginSuccess" : LoginSuccess, "name" : name, "phone": str(user['phone']), "birth" : str(user['birth']), "gender" : user['gender']}, ensure_ascii=False)
        res = make_response(result)
        return res

# 개발자 : 정훈
# 개발 시작일 : 2022.08.18
# 간단한 설명 : 무피 앱에서 아이디 중복 여부 확인 시 작동
@api.route('/mufiApp/app/signup/inspection/<string:id>')
class mufiApp(Resource):
    def get(self, id):
        checkId = 1
        md = MufiData()
        idlist = md.selectdb("select userid from appuser where userid = '"+ id +"';")
        for i in idlist:
            checkId = 0
        result = json.dumps({"isNotDuplicated" : checkId}, ensure_ascii=False)
        res = make_response(result)
        return res

# 개발자 : 정훈
# 개발 시작일 : 2022.08.18
# 간단한 설명 : 무피 앱에서 등록하고 싶은 사용자의 정보를 전송할 시 작동
@api.route('/mufiApp/app/signup/<string:id>/<string:pw>/<string:name>/<string:callNumber>/<string:birth>/<string:gender>')
class mufiApp(Resource):
    def get(self, id, pw, name, callNumber, birth, gender):
        md = MufiData()
        cry = crypto()
        pw = cry.encoded(pw)
        a = md.insertdb("insert into appuser value ('" + id +"', '"+pw+"', '"+name+"', '"+callNumber+"', '"+birth+"', "+gender+");")
        result = json.dumps({"isSignUpSuccess" : a}, ensure_ascii=False)
        res = make_response(result)
        return res


# 개발자 : 정훈
# 개발 시작일 : 2022.08.18
# 간단한 설명 : 무피 앱에서 카드를 등록 요청 시 작동
@api.route('/mufiApp/app/payments/<string:cardnumber>/<string:cardExpirationYear>/<string:cardExpirationMonth>/<string:cardPassword>/<string:customerIdentityNumber>/<string:customerKey>')
class mufiApp(Resource):
    def get(self,cardnumber, cardExpirationYear, cardExpirationMonth, cardPassword, customerIdentityNumber, customerKey):
        payload = '''{"cardNumber":"'''+cardnumber+'''","cardExpirationYear":"'''+cardExpirationYear+'''","cardExpirationMonth":"'''+cardExpirationMonth+'''","cardPassword":"'''+cardPassword+'''","customerIdentityNumber":"'''+customerIdentityNumber+'''","customerKey":"'''+customerKey+'''"}'''
        tp = tosspay()
        data = tp.cardENROLL()
        md = MufiData(payload)
        a = md.insertdb("insert into card(mld, cardid, userid, method, billingkey, cardcompany, cardNumber) value ('" + data['mId'] +"', '"+crypto().encodedcard(data['cardNumber'],data['cardCompany'])+"', '"+data['customerKey']+"', '"+data['method']+"', '"+data['billingKey']+"', '"+data['cardCompany']+"', '"+data['cardNumber']+"');")
        result = json.dumps({"isRegistrationSuccess" : a}, ensure_ascii=False)
        res = make_response(result)
        return res

# 개발자 : 정훈
# 개발 시작일 : 2022.08.18
# 간단한 설명 : 무피 앱에서 사용자의 등록된 카드정보를 요청 시 작동
@api.route('/mufiApp/app/payments/info/<string:userid>')
class mufiApp(Resource):
    def get(self,userid):
        reback = {'is_fection':0, "cards":[]}
        md = MufiData()
        cardlist = md.selectdb("select cardid, method, cardcompany, cardnumber from card where userid = '"+ userid +"';")
        for i in cardlist:
            reback["is_fection"] += 1
            reback["cards"].append({"cardCompany":i["cardcompany"], "cardNumber":i["cardnumber"], "method":i["method"],"cardId":i["cardid"]})
        result = json.dumps(reback, ensure_ascii=False)
        res = make_response(result)
        return res

# 개발자 : 정훈
# 개발 시작일 : 2022.08.18
# 간단한 설명 : 무피 앱에서 키오스크 정보와 사용자 정보를 보내주면 키오스크에 유저 정보 전송
@api.route('/mufiApp/app/login/<string:ip>/<string:storeid>/<string:kioskid>/<string:userid>/<string:username>')  # url pattern으로 name 설정
class mufiApp(Resource):
    def get(self, ip, storeid, kioskid, userid, username):
        LoginSuccess = 0
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, 5555))
        data2 = { "isLoginSuccess" : LoginSuccess, "name" : username, "userid" : userid }
        data2 = json.dumps(data2,ensure_ascii=False)
        data2 = data2.encode('utf-8')
        client_socket.send(data2)
        client_socket.close()
        result = json.dumps({"isLoginSuccess" : LoginSuccess, "name" : username, "userid" : userid}, ensure_ascii=False)
        res = make_response(result)
        return res

# 개발자 : 정훈
# 개발 시작일 : 2022.08.18
# 간단한 설명 : 키오스크에서 결제를 요청할 때 실행
@api.route('/mufiApp/kiosk/payments/<string:userid>/<string:kioskid>/<string:storeid>/<int:amount>/<string:ordername>/<string:cardId>')
class mufiApp(Resource):
    def get(self,userid,kioskid,storeid,amount,ordername,cardId):
        orderid = datetime.now().strftime('%Y%m%d%H%M%S')
        orderid += "MF"+str(int((time.time()%1)*100000000))
        payload = '''{"amount":'''+str(amount)+''',"customerKey":"'''+userid+'''","orderId":"'''+orderid+'''","cutomerEmail":"junghun9904@naver.com","cutomerName":"Hun","orderName":"'''+ordername+'''","taxFreeAmount":0}'''
        payload = payload.encode('utf-8').decode('iso-8859-1')

        data = tosspay().billingPayment(payload,cardId)

        result = json.dumps({"ispaymentSuccess" : 1, "orderid" : orderid}, ensure_ascii=False)
        res = make_response(result)
        return res

# 개발자 : 정훈
# 개발 시작일 : 2022.08.18
# 간단한 설명 : 키오스크에서 이미지를 업로드할 때 작동
@api.route('/mufiApp/kiosk/pictures/upload/<string:userid>/<string:orderid>/<int:count>')
class mufiApp(Resource):
    def post(self,userid,orderid,count):
        md = MufiData()
        for i in range(count):
            f = request.files['image'+str(i+1)]
            f.save(secure_filename('imges/image'+str(i+1)))
        for i in range(count):
            with open("images/image"+i+".png",'rb') as image_file:
                binaryImage = image_file.read()
            binaryImage = base64.b64encode(binaryImage)
            binaryImage = binaryImage.decode("UTF-8")
            a = md.insertdb("insert into pictures(userid, picture_id, picturedata, priority, orderid) value ('" + userid +"', '"+orderid+str(i)+"', '"+binaryImage+"', "+str(i)+", '"+orderid+"');")
        result = json.dumps({"isUploadSuccess" : a}, ensure_ascii=False)
        res = make_response(result)
        return res

# 개발자 : 정훈
# 개발 시작일 : 2022.08.18
# 간단한 설명 : 키오스크에 동영상 전송
@api.route('/mufiApp/kiosk/pictures/play/ads')
class mufiApp(Resource):
    def get(self):
        return send_file("video/test1.mp4")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)