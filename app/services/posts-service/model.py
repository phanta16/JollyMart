import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
import sqlalchemy_serializer
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase

class PostsInfo(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'posts_info'
    post_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, autoincrement=True, primary_key=True)
    media = sqlalchemy.Column(sqlalchemy.BLOB, nullable=False)
    date_created = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.datetime.now)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)