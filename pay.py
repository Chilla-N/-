from flask import Blueprint, redirect, session, render_template, request, jsonify, escape,url_for, make_response
import requests
import json
import pymongo


import logging
#logging.basicConfig(filename='test.log', level=logging.ERROR)


bp = Blueprint('bp', __name__)
client = pymongo.MongoClient("localhost",27017)
db = client.get_database("test")
admins = client.get_database("admin")
admin = admins.get_collection("admin")
user = db.get_collection("user")
Vm = db.get_collection("Vm")

@bp.route('/point', methods=['GET','POST'])  
def point():
    user_id = session.get('login',None)
    if user_id == None:
        return redirect(url_for("login"))
    if request.method == 'GET':
        return render_template('point.html',user_info = user.find_one({"user_id":user_id}), price = admin.find_one({"lable":"price"}))
    else:
        dc_col = admin.find_one({"lable":"DC"})
        DC_num = request.form.get('DC_num')
        bprice = float(request.form.get('pay_price'))
        dc = float(dc_col[DC_num])


        aprice = int(bprice*(1-0.01*dc))
        
        URL = 'https://kapi.kakao.com/v1/payment/ready'
        headers = {
            'Authorization': "KakaoAK " + "47505261b90a9bd874b965a27a6abc3e",
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        params = {
            "cid": "TC0ONETIME", #가맹점 코드
            "partner_order_id": "1001",  #가맹점 주문코드
            "partner_user_id": user_id,  #가맹점 회원
            "item_name": "포인트)옵션:"+DC_num,  #상품명
            "quantity": 1, #상품 수량
            "total_amount": aprice, #상품총액 
            "tax_free_amount": 0,  #비과세 금액(그냥 0)
            "approval_url": "http://localhost:5000/kakaopay/success",
            "cancel_url": "http://localhost:5000/kakaopay/cancel",
            "fail_url": "http://localhost:5000/kakaopay/fail",
        }
        res = requests.post(URL, headers=headers, params=params)
        print(res)
        session["tid"] = res.json()['tid']
        session['user_id'] = user_id
        return redirect(res.json()['next_redirect_pc_url'])

@bp.route("/kakaopay/success", methods=['POST', 'GET'])
def sucess():
    tid = session.get("tid")
    user_id = session.get("user_id")

    URL = 'https://kapi.kakao.com/v1/payment/approve'
    headers = {
        "Authorization": "KakaoAK " + "47505261b90a9bd874b965a27a6abc3e",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    params = {
        "cid": "TC0ONETIME",  # 테스트용 코드
        "tid": tid,  # 결제 요청시 세션에 저장한 tid
        "partner_order_id": "1001",  # 주문번호
        "partner_user_id": user_id,  # 유저 아이디
        "pg_token": request.args.get("pg_token"),  # 쿼리 스트링으로 받은 pg토큰
    }
    res = requests.post(URL, headers=headers, params=params)
    print(res.text)
    print(res.json())
    print(res.json()['amount'])
    print(res.json()['amount']['total'])
    amount = res.json()['amount']['total']
    res = res.json()
    context = {
        'res': res,
        'amount': amount,
    }
    item = res['item_name'][7:]
    added_point= admin.find_one({"lable":"default_cash"})[item]
    session['user_id'] = user_id
    point = user.find_one({"user_id":user_id})["point"]
    point = point + added_point
    user.update_one({"user_id":user_id},{"$set":{"point":point}})
    return render_template('success.html', context=context, res=res)

@bp.route("/kakaopay/cancel", methods=['POST', 'GET'])
def cancel():
    URL = "https://kapi.kakao.com/v1/payment/order"
    headers = {
        "Authorization": "KakaoAK " + "47505261b90a9bd874b965a27a6abc3e",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    params = {
        "cid": "TC0ONETIME",  # 가맹점 코드
        "tid": session.get('tid'),  # 결제 고유 코드
    }

    res = requests.post(URL, headers=headers, params=params)
    print(res.text)

    amount = res.json()['cancel_available_amount']['total']
    context = {
        'res': res,
        'cancel_available_amount': amount,
    }
    
    if res.json()['status'] == "QUIT_PAYMENT":
        res = res.json()
        return render_template('cancel.html', params=params, res=res, context=context)

@bp.route("/kakaopay/fail", methods=['POST', 'GET'])
def fail():

    return render_template('fail.html')