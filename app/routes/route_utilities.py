from flask import abort, make_response
from ..db import db


def validate_model(model, model_id):
    model_name = model.__name__.lower()

    try:
        model_id = int(model_id)
    except (ValueError, TypeError):
        response = {"message": f"{model_name} {model_id} invalid"}
        abort(make_response(response, 400))

    query = db.select(model).where(model.id == model_id)
    model_instance = db.session.scalar(query)

    if model_instance is None:
        response = {"message": f"{model_name} {model_id} not found"}
        abort(make_response(response, 404))

    return model_instance


def create_model(model, request_body):
    if (not request_body or "title" not in request_body
        or (hasattr(model, "description") and "description" not in request_body)):
        abort(make_response({"details": "Invalid data"}, 400))

    new_model = model.from_dict(request_body)

    db.session.add(new_model)
    db.session.commit()

    return new_model.to_dict(), 201
