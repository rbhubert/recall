# coding=utf-8
import json
import os

import rq
from flask import Flask, Response
from flask import request
from flask_cors import CORS

import task_handler
from enums.type_data import DataType
from worker import conn

FLASK_APP = Flask(__name__)
CORS(FLASK_APP)  # allowing request from different urls... (localhost in another port)

# just to avoid a windows error...
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

tasksQueue = rq.Queue(connection=conn, default_timeout=3600)


# TODO revisar esto por posibles errores

@FLASK_APP.route("/task/<task_id>", methods=["GET"])
def get_task_status(task_id):
    task = tasksQueue.fetch_job(task_id)

    if task:
        response_object = {
            "status": "success",
            "data": {
                "task_id": task.get_id(),
                "task_status": task.get_status(),
                "task_result": task.result,
            },
        }
    else:
        response_object = {"status": "error"}

    response = json.dumps(response_object)
    return Response(response, status=200, mimetype='application/json')


@FLASK_APP.route("/user/<username>", methods=["GET"])
def get_user(username):
    username = username.lower()
    user_info = task_handler.get_user(username)

    resp_js = json.dumps({"user_info": user_info})
    status = 200 if user_info[0] else 400

    return Response(resp_js, status=200, mimetype='application/json')


@FLASK_APP.route('/model/<model_name>', methods=['GET', 'POST'])
def create_model(model_name):
    if request.method == 'GET':
        job = task_handler.load_model(model_name)
        result = json.dumps(job)
    else:
        documents = json.loads(request.form.get('training_documents'))
        user = request.form.get('username')
        job = tasksQueue.enqueue(task_handler.create_model, model_name, documents, user)
        result = json.dumps(job.get_id())
    return Response(result, status=200, mimetype='application/json')


@FLASK_APP.route('/search/google/<model_name>', methods=['POST'])
def search_news(model_name):
    query = request.form.get('query')

    job = tasksQueue.enqueue(task_handler.search_keywords, DataType.GOOGLE, model_name, query)
    job_id_js = json.dumps(job.get_id())
    return Response(job_id_js, status=200, mimetype='application/json')


@FLASK_APP.route('/search/reddit/<model_name>', methods=['POST'])
def search_posts(model_name):
    query = request.form.get('query')

    job = tasksQueue.enqueue(task_handler.search_keywords, DataType.REDDIT, model_name, query)
    job_id_js = json.dumps(job.get_id())
    return Response(job_id_js, status=200, mimetype='application/json')


@FLASK_APP.route('/search/twitter/<model_name>', methods=['POST'])
def search_tweets(model_name):
    query = request.form.get('query')

    job = tasksQueue.enqueue(task_handler.search_keywords, DataType.TWITTER, model_name, query)
    job_id_js = json.dumps(job.get_id())
    return Response(job_id_js, status=200, mimetype='application/json')


@FLASK_APP.route('/documents_in_range/<model_name>/<range>')
def get_documents_to_classify(model_name, range):
    result = task_handler.get_items_to_classify(model_name, range)
    resultjs = json.dumps(result, default=str)
    return Response(resultjs, status=200, mimetype='application/json')


@FLASK_APP.route('/classify/<model_name>', methods=['POST'])
def classify_documents(model_name):
    documents = json.loads(request.form.get('documents'))

    job = tasksQueue.enqueue(task_handler.classify_documents, model_name, documents)
    jobId_js = json.dumps(job.get_id())
    return Response(jobId_js, status=200, mimetype='application/json')


@FLASK_APP.route('/plot/<model_name>/<already_classified>', methods=['POST'])
def get_information_plot(model_name, already_classified):
    already_classified = True if already_classified == "true" else False
    response = task_handler.get_information_plot(model_name, already_classified)
    response_js = json.dumps(response)
    return Response(response_js, status=200, mimetype='application/json')


@FLASK_APP.route('/update', methods=['POST'])
def update_document():
    url_item = request.form.get('url')
    title = request.form.get('title')
    text = request.form.get('text')

    response = task_handler.update_document(url_item, title, text)
    response_js = json.dumps(response)
    return Response(response_js, status=200, mimetype='application/json')


#
# @FLASK_APP.route('/to_txt/<model_name>', methods=['POST'])
# def to_txt(model_name):
#     documents = json.loads(request.form.get('documents'))
#
#     job = tasksQueue.enqueue(task_handler_new.classify_documents, model_name, documents)
#     jobId_js = json.dumps(job.get_id())
#     return Response(jobId_js, status=200, mimetype='application/json')


if __name__ == '__main__':
    FLASK_APP.run()
