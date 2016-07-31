from flask import Flask
from flask import jsonify
from flask import make_response
from flask import request
from flask import abort
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)


# model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    description = db.Column(db.String(120))
    done = db.Column(db.Boolean())

    def __init__(self, title, description, done):
        self.title = title
        self.description = description
        self.done = done

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

db.create_all()


# web site
@app.route('/')
def index():
    return render_template('index.html')


# API
# 404 handler
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'not found'}), 404)


@app.errorhandler(400)
def custom400(error):
    return make_response(jsonify({'error': 'incorrect data'}), 400)


# get tasks
@app.route('/api/v1/tasks', methods=['GET'])
def get_tasks():
    tasks = []
    query = Task.query.all()
    for q in query:
        tasks.append(q.as_dict())
    return jsonify({'tasks': tasks})


# get single task
@app.route('/api/v1/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    query = Task.query.get_or_404(task_id)
    task = query.as_dict()
    return jsonify({'task': task})


# post task
@app.route('/api/v1/tasks', methods=['POST'])
def create_task():
    # validate data
    if not request.json or 'title' and 'description' not in request.json:
        abort(400)
    # create Task object
    task = Task(
        request.json['title'],
        request.json['description'],
        False
    )
    # save to database
    db.session.add(task)
    db.session.commit()
    return jsonify(task.as_dict()), 201


# update task
@app.route('/api/v1/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    if not request.json:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task = Task.query.get_or_404(task_id)
    task.title = request.json['title']
    task.description = request.json['description']
    task.done = request.json['done']
    db.session.commit()
    return jsonify(task.as_dict())


# delete task
@app.route('/api/v1/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'result': True})


if __name__ == '__main__':
    app.run()
