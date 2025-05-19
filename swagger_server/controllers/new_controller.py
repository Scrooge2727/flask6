import connexion
from flask import jsonify, request
from swagger_server.models.new import New
from swagger_server.sqldate import db
from swagger_server.logger import logger
from swagger_server.tracer import tracer

def new_controller_create_new_entity(body):
    """Создать новый объект"""
    with tracer.start_as_current_span("create_new_entity"):
        if connexion.request.is_json:
            with tracer.start_as_current_span("parse_json_body"):
                data = connexion.request.get_json()
            with tracer.start_as_current_span("db_insert_entity"):
                new_entity = New(name=data.get('name'), email=data.get('email'))
                db.session.add(new_entity)
            with tracer.start_as_current_span("db_commit"):
                db.session.commit()
            logger.info("Создан новый объект")
            return jsonify(new_entity.to_dict()), 201
        logger.error("Неверный формат запроса при создании объекта")
        return {"message": "Неверный формат запроса"}, 400

def new_controller_get_new_entities():
    """Получить все новые объекты"""
    with tracer.start_as_current_span("get_all_new_entities"):
        with tracer.start_as_current_span("db_query_all"):
            new_entities = New.query.all()
        logger.info(f"Получено объектов: {len(new_entities)}")
        return jsonify([entity.to_dict() for entity in new_entities]), 200

def new_controller_get_new_entity(new_entity_id):
    """Получить новый объект по ID"""
    with tracer.start_as_current_span("get_new_entity_by_id"):
        with tracer.start_as_current_span("db_query_by_id"):
            new_entity = New.query.get(new_entity_id)
        if new_entity:
            logger.info(f"Объект найден: id={new_entity_id}")
            return jsonify(new_entity.to_dict()), 200
        logger.error(f"Объект с id={new_entity_id} не найден")
        return {"message": "Объект не найден"}, 404

def new_controller_update_new_entity(body, new_entity_id):
    """Обновить новый объект"""
    with tracer.start_as_current_span("update_new_entity"):
        with tracer.start_as_current_span("db_query_by_id"):
            new_entity = New.query.get(new_entity_id)
        if not new_entity:
            logger.error(f"Объект с id={new_entity_id} не найден")
            return {"message": "Объект не найден"}, 404

        if connexion.request.is_json:
            with tracer.start_as_current_span("parse_json_body"):
                data = connexion.request.get_json()
            with tracer.start_as_current_span("update_fields"):
                new_entity.name = data.get('name', new_entity.name)
                new_entity.email = data.get('email', new_entity.email)
            with tracer.start_as_current_span("db_commit"):
                db.session.commit()
            logger.info(f"Объект с id={new_entity_id} обновлён")
            return jsonify(new_entity.to_dict()), 200
        logger.error("Неверный формат запроса при обновлении")
        return {"message": "Неверный формат запроса"}, 400

def new_controller_delete_new_entity(new_entity_id):
    """Удалить новый объект"""
    with tracer.start_as_current_span("delete_new_entity"):
        with tracer.start_as_current_span("db_query_by_id"):
            new_entity = New.query.get(new_entity_id)
        if not new_entity:
            logger.error(f"Объект с id={new_entity_id} не найден")
            return {"message": "Объект не найден"}, 404
        with tracer.start_as_current_span("db_delete"):
            db.session.delete(new_entity)
        with tracer.start_as_current_span("db_commit"):
            db.session.commit()
        logger.info(f"Объект с id={new_entity_id} удалён")
        return {"message": "Объект удалён"}, 200
