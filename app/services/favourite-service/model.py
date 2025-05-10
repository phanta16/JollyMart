import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
import sqlalchemy_serializer
from sqlalchemy_serializer import SerializerMixin

from db_session import SqlAlchemyBase

class FavouriteInfo(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'favourite_info'
    rate_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, primary_key=True, autoincrement=True)
    post_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    post_header = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    post_image = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)