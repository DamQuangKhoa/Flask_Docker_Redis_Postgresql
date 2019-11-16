import redis
from rq import Queue, Connection
from flask import Flask, request, jsonify
import time
from flask_sqlalchemy import SQLAlchemy


from long_task_package.long_task import long_task
from long_task_package.long_task import parallel_long_task

from flask_restful import Api, Resource, reqparse
import os
from dotenv import load_dotenv

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# app = Flask(__name__)
# # REDIS_URL = 'redis://redis:6379/0'
# # REDIS_QUEUES = ['default']


# # DBUSER = 'ted'
# # DBPASS = 'ted'
# # DBHOST = 'db'
# # DBPORT = '54320'
# # DBNAME = 'sendodb'

# # app.config['SQLALCHEMY_DATABASE_URI'] = \
# #     'postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{db}'.format(
# #         user=DBUSER,
# #         passwd=DBPASS,
# #         host=DBHOST,
# #         port=DBPORT,
# #         db=DBNAME)
# # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# # app.secret_key = 'ted'


# # db = SQLAlchemy(app)
# # r = redis.Redis()
# # q = Queue(connection=r)

app = Flask(__name__)
api = Api(app)
#
# Load Environment variable
APP_ROOT = os.path.join(os.path.dirname(__file__), '.')
dotenv_path = os.path.join(APP_ROOT, ".env")
print('Loading environment variables in ', dotenv_path)
load_dotenv(dotenv_path)

# Database Config
postgre_address = os.getenv('POSTGRE_ADDRESS')
postgre_database = os.getenv('POSTGRE_DATABASE')
postgre_user = os.getenv('POSTGRE_USER')
postgre_password = os.getenv('POSTGRE_PASSWORD')
posgre_port = os.getenv('POSTGRE_PORT')

# Print Maria config to examinate
print('Postgre IP: ', postgre_address)
print('Postgre Database Name: ', postgre_database)
print('Postgre user: ', postgre_user)
print('Postgre password: ', postgre_password)
print('Postgre Port: ', posgre_port)

app = Flask(__name__)
api = Api(app)

# Engine
Base = declarative_base()
db_string = 'postgres://ted:ted@172.18.0.1:54320/sendodb'
engine = create_engine(db_string)

# Schema


class Users(Base):
    __tablename__ = 'users'
    user_id = Column(String, primary_key=True)
    username = Column(String)
    password = Column(String)
    mac_address = Column(String)
    last_activity = Column(String)


class Category(Base):
    __tablename__ = 'category'
    cate3_id_new = Column(String, primary_key=True)
    cate1_id, cate1_name = Column(String), Column(String)
    cate2_id, cate2_name = Column(String), Column(String)
    cate3_id, cate3_name = Column(String), Column(String)


class Product(Base):
    __tablename__ = 'products'
    product_id = Column(String, primary_key=True)
    product_name = Column(String)
    uri = Column(String)
    oldprice = Column(Float)
    price = Column(Float)
    status = Column(Integer)


class Cate_Prod(Base):
    __tablename__ = 'cate_product'
    id = Column(String, primary_key=True)
    cate3_id_new = Column(String)
    product_id = Column(String)


# API Class
category_parser = reqparse.RequestParser()
category_parser.add_argument('cate1_id', type=str, required=False)


class Cate1(Resource):
    def get(self):
        try:
            args = category_parser.parse_args()
            cate1_id = args["cate1_id"]
            print("HELLO: ", cate1_id)

            Session = sessionmaker(bind=engine)
            session = Session()

            result = session.query(Category)\
                .filter(Category.cate1_id == cate1_id).distinct(Category.cate2_id)

            print("RESULT: ", result)

            result = list(map(lambda x: x.cate2_id, result))

            print("BEAUTIFUL: ", result)

            return {"result": result, "status": 200}
        except:
            return {"status": 500}


# Routing
api.add_resource(Cate1, "/cate1")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
