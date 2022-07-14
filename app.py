from flask import Flask, render_template, request, jsonify, redirect, url_for
from pip._vendor import requests

app = Flask(__name__)

from pymongo import MongoClient

import certifi

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.txbva.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.hanghae99

import jwt   #(pyjwt 설치)
import hashlib
import datetime
SECRET_KEY = 'hanghae'


@app.route('/')
def gu():
    return render_template('gu_choice_00.html')


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/register')
def register_page():
    return render_template('register.html')


@app.route('/review/<gu>')
def multi_page(gu):
    token = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        user = db.user.find_one({'id': payload['id']})
        return render_template('review.html', name=user['name'], gu=gu)
    except jwt.ExpiredSignatureError:
        return redirect(url_for('login_page'))
    except jwt.exceptions.DecodeError:
        return redirect(url_for('login_page'))

@app.route('/api/register', methods=['POST'])
def register():
    id = request.form['id_give']
    pw = request.form['pw_give']
    name = request.form['name_give']

    user = db.user.find_one({'id': id})
    print(user)
    if user is not None:
        return jsonify({'result': True, 'msg': '* 동일한 ID가 존재합니다'})
    else:
        pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

        db.user.insert_one({'id': id, 'pw': pw_hash, 'name': name})
        return jsonify({'msg': '회원가입 성공!'})


@app.route('/api/login', methods=['POST'])
def login():
    id = request.form['id_give']
    pw = request.form['pw_give']

    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    user = db.user.find_one({'id': id, 'pw': pw_hash})
    print(pw_hash, user)
    if user is not None:
        payload = {
            'id': id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60*60*24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        print(token)
        return jsonify({'result': True, 'msg': '로그인 성공!', 'token': token})
    else:
        return jsonify({'result': False, 'msg': '아이디/비밀번호가 일치하지 않습니다'})

# -------------------
# 유경님 app.py merge


@app.route("/api/review/<gu>", methods=["POST"])
def comment_save(gu):
    name_receive = request.form['name_give']
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']

    doc = {
        'name': name_receive,
        'star': star_receive,
        'comment': comment_receive,
        'gu': gu
    }

    db.review.insert_one(doc)

    return jsonify({'msg':'기록 완료!'})


@app.route("/api/review/<gu>", methods=["GET"])
def review_get(gu):
    all_comments = list(db.review.find({'gu': gu}, {'_id': False}))
    return jsonify({'comments': all_comments})


if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)



# gu_choice DB에 저장 코드
#
# r = requests.get("http://openapi.seoul.go.kr:8088/6a4c6750656c6a63363572677a7573/json/SearchParkInfoService/1/132")
#     result = r.json()
#
#     rows = result['SearchParkInfoService']['row']
#     for row in rows:
#         try:
#             doc = {
#                 'P_IDX': row['P_IDX'],
#                 'P_PARK': row['P_PARK'],
#                 'LONGITUDE': row['LONGITUDE'],
#                 'LATITUDE': row['LATITUDE'],
#                 'P_LIST_CONTENT': row['P_LIST_CONTENT'],
#                 'MAIN_EQUIP': row['MAIN_EQUIP'],
#                 'P_ADDR': row['P_ADDR'],
#                 'TEMPLATE_URL': row['TEMPLATE_URL']
#             }
#             db.gu.insert_one(doc)
#         except:
#             print('자료가 부족합니다.')
#
#
# DB에 저장된 gu 주소 변수로 받은 거 하나씩 GET 으로 전달
# @app.route('/review/<gu>', methods=['GET'])
# def gu_choice(gu):
#
#     find_one = db.gu.find_one({'P_PARK': gu}, {'_id': False})
#     print(find_one)
#
#     return jsonify({'result': True, 'gu_choice': find_one})