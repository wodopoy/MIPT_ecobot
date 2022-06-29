from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

#добавляем sql алхимию и настраиваем
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#создаем таблицу (название колонки = колонка(тип данных колонки))
class UserInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer())
    address = db.Column(db.String(1024))
    x = db.Column(db.Float())
    y = db.Column(db.Float())
    trash_weight = db.Column(db.Float())


def init_user(chat_id: int):
    try:
        sample = UserInfo.query.filter_by(chat_id=chat_id).first()

        if sample:
            return f'User alreday added: chat_id = {chat_id}'

        else:
            obj = UserInfo(chat_id = chat_id)
            db.session.add(obj)
            db.session.commit()
        
            return f'User added: chat_id = {obj.chat_id}'
            

    except Exception as e:
        return f'Error | [dbworker: init_user] : {e}'

def set_position(chat_id: int, address: str, x: float, y: float):
    try:
        obj = UserInfo.query.filter_by(chat_id=chat_id).first()

        obj.address = address
        obj.x = x
        obj.y = y

        db.session.add(obj)
        db.session.commit()
        
        return obj

    except Exception as e:
        return f'Error | [dbworker: add_position] : {e}'

def set_trash_weight(chat_id: int, trash_weight: float):
    try:
        obj = UserInfo.query.filter_by(chat_id=chat_id).first()

        if trash_weight <= 0:
            return 'error'

        else:
            obj.trash_weight = trash_weight

            db.session.add(obj)
            db.session.commit()
            
            return obj

    except Exception as e:
        return f'Error | [dbworker: add_trash_weight] : {e}'

def get_user_pos_and_trash_weight(chat_id: int):
    obj = UserInfo.query.filter_by(chat_id=chat_id).first()

    output = {
        'x': obj.x,
        'y': obj.y,
        'trash_weight': obj.trash_weight
    }

    if output['trash_weight'] == None or output['x'] == None or output['y'] == None:
        return 'none'
    
    else:

        return output

def get_users():
    obj = UserInfo.query.filter(UserInfo.chat_id!=None).all()
    return obj

def get_users_chatids():
    obj = UserInfo.query.filter(UserInfo.chat_id!=None).all()
    chat_ids = []
    for i in range(len(obj)):
        chat_ids.append(obj[i].chat_id)
    return chat_ids

def get_user_address(chat_id: int):
    obj = UserInfo.query.filter_by(chat_id=chat_id).first()
    if obj.address == None:
        return 'none'
    return obj.address

def get_trash_weight(chat_id: int):
    obj = UserInfo.query.filter_by(chat_id=chat_id).first()
    if obj.trash_weight == None:
        return 'none'
    return obj.trash_weight

def clearDB():
    try:
        chatids = get_users_chatids()

        for i in range(len(chatids)):
            obj = UserInfo.query.filter_by(chat_id=chatids[i]).first()
            obj.address = None
            obj.x = None
            obj.y = None
            obj.trash_weight = None
            db.session.commit()

        return "db is clear"

    except Exception as e:
        return f'Error | [dbworker: add_trash_weight] : {e}'