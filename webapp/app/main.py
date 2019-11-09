import redis
from rq import Queue, Connection
from flask import Flask, request, jsonify
import time
from flask_sqlalchemy import SQLAlchemy


from long_task_package.long_task import long_task
from long_task_package.long_task import parallel_long_task

app = Flask(__name__)
REDIS_URL = 'redis://redis:6379/0'
REDIS_QUEUES = ['default']


DBUSER = 'ted'
DBPASS = 'ted'
DBHOST = 'db'
DBPORT = '5432'
DBNAME = 'sendodb'

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{db}'.format(
        user=DBUSER,
        passwd=DBPASS,
        host=DBHOST,
        port=DBPORT,
        db=DBNAME)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'ted'


db = SQLAlchemy(app)
r = redis.Redis()
q = Queue(connection=r)


class students(db.Model):
    id = db.Column('student_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(50))
    addr = db.Column(db.String(200))

    def __init__(self, name, city, addr):
        self.name = name
        self.city = city
        self.addr = addr


def database_initialization_sequence():
    db.create_all()
    test_rec = students(
        'John Doe',
        'Los Angeles',
        '123 Foobar Ave')

    db.session.add(test_rec)
    db.session.rollback()
    db.session.commit()


def background_task(n):
    """ Function that returns len(n) and simulates a delay """

    delay = 2

    print("Task running")
    # print(f"Simulating a {delay} second delay")

    time.sleep(delay)

    print(len(n))
    print("Task complete")

    return len(n)


@app.route("/")
def index():
    if request.args.get("n"):

        job = q.enqueue(background_task, request.args.get("n"))

        return f"Task ({job.id}) added to queue at {job.enqueued_at}"

    return "No value for count provided"


@app.route('/long_task', methods=['POST'])
def run_long_task():
    task_duration = 1000
    with Connection(redis.from_url(REDIS_URL)):
        q = Queue()
        # task need to be executed within the specified timeout
        task = q.enqueue(long_task, task_duration, timeout=1200)
    response_object = {
        'status': 'success',
        'data': {
            'task_id': task.get_id()
        }
    }
    return jsonify(response_object), 202


@app.route('/parallel_long_task', methods=['POST'])
def run_parallel_long_task():
    task_duration = int(request.form['duration'])
    with Connection(redis.from_url(REDIS_URL)):
        q = Queue()
        # task need to be executed within the specified timeout
        task = q.enqueue(parallel_long_task, task_duration, timeout=1200)
    response_object = {
        'status': 'success',
        'data': {
            'task_id': task.get_id()
        }
    }
    return jsonify(response_object), 202


@app.route('/tasks/<task_id>', methods=['GET'])
def get_status(task_id):
    with Connection(redis.from_url(REDIS_URL)):
        q = Queue()
        task = q.fetch_job(task_id)
    if task:
        response_object = {
            'status': 'success',
            'data': {
                'task_id': task.get_id(),
                'task_status': task.get_status(),
                'task_result': task.result
            }
        }

        if task.is_failed:
            response_object = {
                'status': 'failed',
                'data': {
                    'task_id': task.get_id(),
                    'message': task.exc_info.strip().split('\n')[-1]
                }
            }
    else:
        response_object = {
            'status': 'ERROR: Unable to fetch the task from RQ'
        }
    return jsonify(response_object)


if __name__ == '__main__':
    # Only for debugging while developing
    # app.run(host='0.0.0.0', debug=True, port=80)
    dbstatus = False
    while dbstatus == False:
        try:
            db.create_all()
        except:
            time.sleep(2)
        else:
            dbstatus = True
    database_initialization_sequence()
    app.run(debug=True, host='0.0.0.0')
    pass
