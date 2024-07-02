from flask import Flask, jsonify, Response, make_response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column

from configparser import ConfigParser
from pdb import set_trace

config_file_path = "config.ini"
cp = ConfigParser()
cp.read(config_file_path)
main_section = cp["main"]
user = main_section.get("user")
pw = main_section.get("password")
host= main_section.get("host")
db = main_section.get("db")

DB_CONNECT_STRING = "mysql+pymysql://{}:{}@{}/{}".format(user, pw, host, db)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_CONNECT_STRING


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Task(db.Model):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    completion_status: Mapped[str] = mapped_column(String(50), nullable=False)



@app.route("/deletetask/<int:taskid>", methods=["DELETE"])
def delete_task(taskid):

    # retrieve task object to be deleted.
    select_query = db.select(Task).filter_by(id=taskid)
    print(select_query)
    results = db.session.execute(select_query)
    row = results.first()
    if row:
        ob = list(row)[0]
        db.session.delete(ob)
        db.session.commit()
    return "/deletetask endpoint code ran"


@app.route("/addtask", methods=["POST"])
def add_task():
    json_data = request.get_json()

    new_task = Task()
    new_task.name = json_data["task_name"]
    new_task.completion_status = json_data["completion_status"]
    db.session.add(new_task)
    db.session.commit()

    return "/addtask endpoint code ran"

@app.route("/tasks", methods=["GET"])
def get_tasks():
    """
    TODO: There needs to be a creation of a task list based on a query of the
    sqlalchemy model.... once I figure out how to make sense of new sqlalchemy. (shrugs)
    :return:
    """
    query = db.select(Task)
    tasks = db.session.execute(query).scalars()
    # task_list=[
    #     dict(description="Dishes", status="Not yet done"),
    #     dict(description="Laundry", status="Not yet done"),
    # ]

    task_list = [dict(description=task.name, status=task.completion_status)
                 for task in tasks]


    res_data = jsonify(dict(tasks=task_list))
    res = make_response(res_data)
    res.headers.add("Access-Control-Allow-Origin", "*")
    return res

if __name__ == '__main__':
    DEBUG_MODE = True
    PORT = 5001
    print(db)
    with app.app_context():
        db.create_all()

    app.run(debug=DEBUG_MODE, port=PORT)
