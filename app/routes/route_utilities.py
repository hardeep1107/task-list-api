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


def create_model(cls, model_data):
    try:
        new_model = cls.from_dict(model_data)

    except KeyError:
        abort(make_response({"details": "Invalid data"}, 400))

    db.session.add(new_model)
    db.session.commit()

    return new_model.to_dict(), 201


def get_models_with_filters(cls, filters=None):
    query = db.select(cls)

    if filters:
        sort_order = filters.get("sort")

        for attribute, value in filters.items():
            if attribute != "sort" and hasattr(cls, attribute):
                query = query.where(
                    getattr(cls, attribute).ilike(f"%{value}%")
                )

        if sort_order == "asc" and hasattr(cls, "title"):
            query = query.order_by(cls.title.asc())
        elif sort_order == "desc" and hasattr(cls, "title"):
            query = query.order_by(cls.title.desc())
        else:
            query = query.order_by(cls.id)
    else:
        query = query.order_by(cls.id)

    models = db.session.scalars(query)
    models_response = [model.to_dict() for model in models]
    return models_response