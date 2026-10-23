from flask import Blueprint, abort, make_response, request, Response
from werkzeug.exceptions import HTTPException
from ..models.task import Task
from ..db import db
from .route_utilities import create_model, validate_model
from datetime import datetime
import os
import requests

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

# Post - Create Task
@tasks_bp.post("")
def create_task():
    request_body = request.get_json()
    return create_model(Task, request_body)


# GET route
@tasks_bp.get("")
def get_all_tasks():
    sort_order = request.args.get("sort")

    query = db.select(Task)

    if sort_order == "asc":
        query = query.order_by(Task.title.asc())
    elif sort_order == "desc":
        query = query.order_by(Task.title.desc())
    else:
        query = query.order_by(Task.id)

    tasks = db.session.scalars(query)

    response = []
    for task in tasks:
        response.append(task.to_dict())

    return response, 200

@tasks_bp.get("/<task_id>")
def get_task(task_id):
    try:
        task = validate_model(Task, task_id)
    except HTTPException as e:
        if e.get_response().status_code == 404:
            abort(make_response({"details": "Not found"}, 404))
        raise

    return task.to_dict(include_goal_id=task.goal_id is not None), 200

# Update Route
@tasks_bp.put("/<task_id>")
def update_task(task_id):
    try:
        task = validate_model(Task, task_id)
    except HTTPException as e:
        if e.get_response().status_code == 404:
            abort(make_response({"details": "Not found"}, 404))
        raise

    request_body = request.get_json()

    if not request_body or "title" not in request_body or "description" not in request_body:
        return {"details": "Invalid data"}, 400

    task.title = request_body["title"]
    task.description = request_body["description"]

    db.session.commit()

    return Response(status=204)


# Delete Route
@tasks_bp.delete("/<task_id>")
def delete_task(task_id):
    try:
        task = validate_model(Task, task_id)
    except HTTPException as e:
        if e.get_response().status_code == 404:
            abort(make_response({"details": "Not found"}, 404))
        raise

    db.session.delete(task)
    db.session.commit()

    return Response(status=204)

# Patch
# Slack message
@tasks_bp.patch("/<task_id>/mark_complete")
def mark_task_complete(task_id):
    try:
        task = validate_model(Task, task_id)
    except HTTPException as e:
        if e.get_response().status_code == 404:
            abort(make_response({"details": "Not found"}, 404))
        raise

    task.completed_at = datetime.now()
    db.session.commit()

    slack_token = os.environ.get("SLACK_BOT_TOKEN")

    requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={
            "Authorization": f"Bearer {slack_token}"
        },
        json={
            "channel": "task-notifications-c26",
            "text": f"Someone just completed the task {task.title}"
        }
    )

    return Response(status=204, mimetype="application/json")

@tasks_bp.patch("/<task_id>/mark_incomplete")
def mark_task_incomplete(task_id):
    try:
        task = validate_model(Task, task_id)
    except HTTPException as e:
        if e.get_response().status_code == 404:
            abort(make_response({"details": "Not found"}, 404))
        raise
    
    task.completed_at = None
    db.session.commit()

    return Response(status=204, mimetype="application/json")