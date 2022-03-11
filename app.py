import numbers
from flask import Flask, request, render_template, session, redirect, flash, jsonify, url_for
import pymongo
from bson import ObjectId
from datetime import datetime
from dateutil.relativedelta import *
import os
import hashlib
import subprocess,sys
from time import sleep
from pay import bp
import requests
from datetime import timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import logging
#logging.basicConfig(filename='test.log', level=logging.ERROR)
#logging.error(result)

def sensor():
    print("서버 점검 중입니다")
    start_time = datetime.today() 
    end_time = datetime.today() + relativedelta(days= +1)
    find_query = { 'end_time': { '$gte' : start_time, '$lt' : end_time }}
    cols = Vm.find(find_query)
    if cols is not None:
        for col in cols:
            if col["running"] == True:
                host_id = col["host_id"]
                Vm.update_one({"host_id":host_id},{"$set":{"trans":True}})
                subprocess.call([".\stop.bat"])
                sleep(3)
                Vm.update_one({"host_id":host_id},{"$set":{"trans":False}})
                Vm.update_one({"host_id":host_id},{"$set":{"running":False}})
                print("VM:"+host_id+"가 기간 만료로 종료되었습니다.")
    print("점검이 종료되었습니다.")

sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor,'cron', hour='00', minute='00')
sched.start()

app = Flask(__name__)
app.register_blueprint(bp)

app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=15)

client = pymongo.MongoClient("localhost",27017)
db = client.get_database("test")
admins = client.get_database("admin")
admin = admins.get_collection("admin")
user = db.get_collection("user")
Vm = db.get_collection("Vm")

SECRET_KEY = os.urandom(32)

app.config['SECRET_KEY'] = SECRET_KEY
def number_changer(num):
    if num == "1":
        return "one"
    elif num == "2":
        return "two"
    elif num == "3":
        return "three"
    elif num == "4":
        return "four"
    elif num == "5":
        return "five"
    elif num == "6":
        return "six"
    elif num == "7":
        return "seven"
    elif num == "8":
        return "eight"
    elif num == 9:
        return "nine"

def boolean_changer(bool):
    if bool == "동의":
        return True
    elif bool == "거부":
        return False
    else:
        flash("자동연장여부를 선택해주세요.")
        return redirect(url_for("creat"))

@app.route('/')
def main():
    user_id = session.get('login',None)
    if user_id == None:
        return redirect(url_for("login"))
    elif  user_id == "admin":
        return redirect(url_for("Admin"))
    else:
        user_info = user.find_one({"user_id":user_id})
        Vm_info = Vm.find_one({"user_id":user_id})
        service_num = Vm_info["service_num"]
        ad_col = admin.find_one({"lable":"price"})
        sche_point = ad_col[service_num]
        return render_template("index.html",user_info = user_info, Vm_info = Vm_info, sche_point = sche_point)


@app.route('/register/', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        user_id = request.form.get('user_id')
        user_pw = request.form.get('user_pw')
        user_pw2 = request.form.get('user_pw2')
        email = request.form.get('email')
        if user_pw != user_pw2:
            flash("비밀번호가 일치하지 않습니다")
            return redirect(url_for("register"))
        else:
            pw_hash = hashlib.sha256(user_pw.encode('utf-8')).hexdigest()
            user.insert_one({'user_id':user_id, 'user_pw': pw_hash, 'email': email, "point": 0})
            flash("정상적으로 가입되었습니다.")
            return redirect(url_for("login"))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        user_pw = request.form['user_pw']
        result = user.find_one({'user_id' : user_id})
        pw_hash = hashlib.sha256(user_pw.encode('utf-8')).hexdigest()
        if result == None:
            flash("올바른 아이디가 아닙니다..")
            return redirect(url_for("login"))
        elif result["user_pw"] != pw_hash:
            flash("올바른 패스워드가 아닙니다.")
            return redirect(url_for("login"))
        else:
            session['login'] = user_id
            return redirect(url_for("main", msg=user_id+"님 로그인 되었습니다"))
    else:
        return render_template("login.html")

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('login', None)
    return redirect(url_for("main"))

@app.route('/create', methods=['GET','POST'])  
def create():
    user_id = session.get('login',None)
    if user_id == None:
        return redirect(url_for("login"))
    if request.method == 'GET':
        return render_template('create.html',user_info = user.find_one({"user_id":user_id}), price = admin.find_one({"lable":"price"}))
    else:
        result = user.find_one( {'user_id' : user_id})
        service_num = request.form['service_num']
        nums = number_changer(service_num)
        price = admin.find_one({"lable":"price"})
        auto = request.form['auto']
        autos = boolean_changer(auto)
        host_id = request.form['host_id']
        host_pw = request.form['host_pw']
        host_pw2 = request.form['host_pw2']
        end_time = datetime.today() + relativedelta(months= +1)
        start_time = datetime.today()
        pw_hash = hashlib.sha256(host_pw.encode('utf-8')).hexdigest()
        if host_pw != host_pw2:
            flash("호스트 비밀번호가 다릅니다.")
            return render_template('create.html',user_info = user.find_one({"user_id":user_id}), price = admin.find_one({"lable":"price"}))
        if result["point"] >= price[nums] :
            Vm.insert_one({
                'user_id':user_id,
                'host_pw': pw_hash,
                'host_id': host_id,
                'auto' : autos,
                'service_num' : nums,
                'start_time' : start_time,
                'end_time': end_time,
                'trans':True,
                'running':True})
            subprocess.call([".\create.bat"])
            sleep(3)
            after_point = result["point"] - price[nums]
            user.update_one({"user_id":user_id},{"$set":{"point":after_point}})
            Vm.update_one({"trans":True},{"$set":{"trans":False}})
            flash("서버가 성공적으로 생성되었습니다.")
            return redirect(url_for("main"))
        else:
            flash("포인트가 부족합니다.")
            return redirect(url_for('create'))


@app.route('/admin', methods=['GET','POST'])
def Admin():
    user_id = session.get('login',None)
    if user_id != 'admin':
        return redirect(url_for("login"))
    if request.method == 'GET':
        #logging.error(admin.find_one({"lable":"price"}))
        return render_template("admin.html",user_info = user.find_one({"user_id":user_id}), price = admin.find_one({"lable":"price"}))
    else:
        service_num = request.form['service_num']
        nums = number_changer(service_num)
        prices = int(request.form['price'])
        admin.update_one({"lable":"price"},{"$set":{nums:prices}})
        return redirect(url_for("Admin"))

if __name__ == "__main__":

    app.run(host="127.0.0.1", port=5000, debug=True)

