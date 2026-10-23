from flask import Blueprint, make_response, request, Response
from ..models.goal import Goal
from ..models.task import Task
from ..db import db
from .route_utilities import create_model, validate_model


goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@goals_bp.route("", methods=["POST"])
def create_goal():
    request_body = request.get_json()
    return create_model(Goal, request_body)

@goals_bp.route("", methods=["GET"])
def get_all_goals():
    query = db.select(Goal).order_by(Goal.id)
    goals = db.session.scalars(query)

    goals_response = [goal.to_dict() for goal in goals]

    return make_response(goals_response, 200)

@goals_bp.route("/<goal_id>", methods=["GET"])
def get_one_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    return make_response(goal.to_dict(), 200)

@goals_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    request_body = request.get_json()
    goal.title = request_body["title"]

    db.session.commit()

    return Response(status=204, mimetype="application/json")

@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    db.session.delete(goal)
    db.session.commit()

    return Response(status=204, mimetype="application/json")

@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_for_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    response_body = goal.to_dict()
    response_body["tasks"] = [
        task.to_dict(include_goal_id=True) for task in goal.tasks
    ]

    return make_response(response_body, 200)

@goals_bp.route("/<goal_id>/tasks", methods=["POST"])
def add_tasks_to_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    request_body = request.get_json()
    task_ids = request_body["task_ids"]

    tasks = []
    for task_id in task_ids:
        task = validate_model(Task, task_id)
        tasks.append(task)

    goal.tasks = tasks
    db.session.commit()

    response_body = {
        "id": goal.id,
        "task_ids": [task.id for task in goal.tasks]
    }

    return make_response(response_body, 200)