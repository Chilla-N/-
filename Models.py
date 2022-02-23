from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy() #SQLAlchemy를 사용해 데이터베이스 저장

class User(db.Model): #데이터 모델을 나타내는 객체 선언
    __tablename__ = 'user_table' #테이블 이름
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(32), unique=False, nullable=False)
    userid = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)
    point = db.Column(db.Integer, default = 0)

    def __init__(self, userid, email, password):
        self.userid=userid
        self.email = email
        self.set_password(password)
    def set_password(self, password):
        self.password = generate_password_hash(password)
 
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Vm(db.Model): #데이터 모델을 나타내는 객체 선언
    __tablename__ = 'user_VM' #테이블 이름
    
    userid = db.Column(db.Integer, primary_key=True)
    host_id=db.Column(db.String(32), unique=True, default = None)
    host_pw=db.Column(db.String(32), default = None)
    server_ip = db.Column(db.String(32), unique=True, default = None)
    end_time = db.Column(db.DateTime(32), default = None)
    service_num = db.Column(db.Integer, default = None)
    auto = db.Column(db.Boolean, default = None)

    def __init__(self,userid,host_id,host_pw,end_time,service_num,auto):
        self.userid = userid
        self.host_id = host_id
        self.host_pw = host_pw
        self.end_time = end_time
        self.service_num = service_num
        self.auto = auto