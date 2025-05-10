import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
import sqlalchemy_serializer
from sqlalchemy_serializer import SerializerMixin

from db_session import SqlAlchemyBase

class CommentaryInfo(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'comment_info'
    comment_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, primary_key=True, autoincrement=True)
    post_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    comment_author_id = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    comment_author_username = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    comment_author_image = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    context = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.datetime.now())