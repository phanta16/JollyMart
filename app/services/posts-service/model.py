import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
import sqlalchemy_serializer
from sqlalchemy_serializer import SerializerMixin

from db_session import SqlAlchemyBase

class PostsInfo(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'posts_info'
    post_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, autoincrement=True, primary_key=True)
    date_created = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.datetime.now)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    price = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    author_username = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    author_image = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    image_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    post_headers = sqlalchemy.Column(sqlalchemy.String, nullable=False)