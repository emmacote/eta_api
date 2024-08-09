from flask import Flask, jsonify, Response, make_response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column

from configparser import ConfigParser

# SQL Alchemy database connection setup to MySQL
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
    """
    SQL Alchemy data model for a task to be done.
    """
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    completion_status: Mapped[str] = mapped_column(String(50), nullable=False)


@app.route("/deletetask/", methods=["DELETE", "OPTIONS"])
def delete_task():
    """
    Delete a task
    :param taskid: The ID of a task to be deleted from the data store
    :return: nothing.
    """

    # CORS logic
    if request.method == "OPTIONS":
        res = make_response("delete allowed")
        res.headers["Access-Control-Allow-Origin"] = "*"
        res.headers["Access-Control-Allow-Methods"] = "DELETE, OPTIONS"
        res.headers["Access-Control-Allow-Headers"] = "Content-type, Authorization"
        return res


    # retrieve task object to be deleted.
    taskid = request.json.get("taskid")
    select_query = db.select(Task).filter_by(id=taskid)
    print(select_query)
    results = db.session.execute(select_query)

    # Delete the task (assuming it was found in the data store to begin with
    row = results.first()
    if row:
        ob = list(row)[0]
        db.session.delete(ob)
        db.session.commit()

    db.session.close()

    res_data = jsonify(dict(status="successful_deletion"))
    res = make_response(res_data)
    res.headers.add("Access-Control-Allow-Origin", "*")
    return res


@app.route("/addtask", methods=["POST", "OPTIONS"])
def add_task():
    """
    Add a new task to the data store.
    :param task_json: A new task as represented by a passed in json structure.
    :return: nothing
    """

    # CORS LOGIC
    if request.method == "OPTIONS":
        res = make_response("delete allowed")
        res.headers["Access-Control-Allow-Origin"] = "*"
        res.headers["Access-Control-Allow-Methods"] = "DELETE, OPTIONS"
        res.headers["Access-Control-Allow-Headers"] = "Content-type, Authorization"
        return res

    json_data = request.get_json()
    new_task = Task()
    new_task.name = json_data["task_name"]
    new_task.completion_status = json_data["completion_status"]

    db.session.add(new_task)
    db.session.commit()
    db.session.close()

    res = make_response(jsonify(dict(status="successfully added task")))
    res.headers.add("Access-Control-Allow-Origin", "*")
    return res

@app.route("/tasks", methods=["GET"])
def get_tasks():
    """
    Get a list of tasks from the data store
    :return: A list of tasks in json format.
    """
    task_list = []

    # run the query
    query = db.select(Task)
    tasks = db.session.execute(query).scalars()
    task_list = [dict(id=task.id, description=task.name, status=task.completion_status)
                 for task in tasks]
    db.session.close()

    # return the list of tasks as json data
    res_data = jsonify(dict(tasks=task_list))
    res = make_response(res_data)
    res.headers.add("Access-Control-Allow-Origin", "*")
    return res

if __name__ == '__main__':
    # start up flask
    DEBUG_MODE = True
    PORT = 5001
    print(db)
    with app.app_context():
        db.create_all()

    app.run(debug=DEBUG_MODE, port=PORT)
