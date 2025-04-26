import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
import sqlalchemy_serializer
from sqlalchemy_serializer import SerializerMixin

from db_session import SqlAlchemyBase

class ChatInfo(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'chat_info'
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    initiator_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    receiver_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)


class MessagesInfo(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'message_info'
    id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, primary_key=True, autoincrement=True)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    context = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    sender_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    receiver_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.datetime.now())