from dataclasses import asdict

from flask import Response, jsonify, request, url_for
from pydantic import ValidationError

from src import app, bp, celery_socketio, log_buffer, socketio
from src.repositories.processing_requests import ProcessingRequestRepository
from src.repositories.web_resources import WebResourceRepository
from src.service import exceptions, handlers
from src.service.web_resources import WebResourceService
from src.utils.helpers import convert_to_serializable, make_int
from src.web.app import db


@bp.route('/resources', methods=['GET'])
def get_resources():
    # extract query params
    domain_zone = request.args.get('domain_zone')
    resource_id = make_int(request.args.get('id'))
    uuid = request.args.get('uuid')
    availability = request.args.get('availability')
    page = make_int(request.args.get('page', default=1, type=int))
    per_page = make_int(request.args.get('per_page', default=10, type=int))

    response = handlers.handle_get_resources_with_filters(
        domain_zone=domain_zone,
        resource_id=resource_id,
        availability=availability,
        page=page,
        per_page=per_page,
        uuid=uuid,
    )

    return jsonify(response.dict())


@bp.route("/resources", methods=['POST'])
def create_url():
    """
    Router for proceeding single URL from body or multiple URLs from zip with csv file.
    Create celery task if zip file was uploaded.
    """
    if request.is_json:
        body = request.get_json()
        try:
            url = handlers.handle_post_url_json(body)
            app.logger.info(f"201 - User posted new URL on {url_for('.create_url')}")
            return Response(
                url.json(),
                status=201,
                mimetype='application/json',
            )
        except exceptions.AlreadyExistsError:
            return jsonify({'error': 'Web resource already exists'}), 409
        except ValidationError as e:
            app.logger.info(f"400 - User made bad request to {request.url}")
            errors = convert_to_serializable(e.errors())
            response = {
                'error': 'Validation error',
                'message': errors,
            }
            return jsonify(response), 400

    elif request.files:
        try:
            processing_request = handlers.handle_post_url_file(request.files)
            app.logger.info(
                f"201 - User posted ZIP archive with URLs on {url_for('.create_url')}"
            )
            return jsonify(asdict(processing_request)), 201
        except ValidationError as e:
            errors = convert_to_serializable(e.errors())
            response = {
                'error': 'Validation error',
                'message': errors,
            }
            return jsonify(response), 400

    else:
        app.logger.info(
            f"400 - User made bad request to {url_for('.create_url')}"
        )
        return jsonify(
            {"Error": "Invalid request format. Send URL via JSON or zip archive via multipart/form-data."}
        ), 400


@bp.route("/resources/<int:web_resource_id>", methods=['DELETE'])
def delete_web_resource(web_resource_id: int):
    web_resource_service = WebResourceService(
        WebResourceRepository(db.session),
        ProcessingRequestRepository(db.session),
    )
    try:
        web_resource_service.delete_resource(web_resource_id)
        app.logger.info(f"204 - Resource with ID={web_resource_id} was deleted.")
        return Response(status=204)
    except exceptions.ResourceNotFoundError:
        app.logger.info(f"404 - Attempt to delete resource with ID={web_resource_id} that does not exist.")
        return Response(status=404)


@bp.route("/processing-requests/<int:request_id>", methods=["GET"])
def get_status_of_processing_request(request_id: int):

    try:
        status_info = handlers.handle_get_request_status(
            request_id=request_id,
            storage_client=app.extensions["redis"],
        )
        return jsonify(status_info)

    except exceptions.ResourceNotFoundError:
        app.logger.info(f"404 - GET request to {request.url} with non-existing ID")
        return jsonify({"Error": "Request with the given ID was not found."}), 404


@bp.route("/resources/<uuid:resource_uuid>", methods=["POST"])
def post_image_for_resource(resource_uuid: str):
    """Router for posting images for resource with the given UUID."""

    if request.files:
        try:
            handlers.handle_add_image_for_web_resource(
                files=request.files,
                resource_uuid=resource_uuid,
            )
            return Response(status=201)
        except exceptions.ResourceNotFoundError:
            return jsonify({"Error": "Web resource with the givent UUID not found."}), 404
        except ValidationError as e:
            # app.logger.info(f""")
            errors = convert_to_serializable(e.errors())
            response = {
                'error': 'Validation error',
                'message': errors,
            }
            return jsonify(response), 400

    else:
        return jsonify({"Error": "Invalid request format"}), 400


# @bp.route("/resources/<uuid:resource_uuid>", methods=["GET"])
# def get_resource_page(resource_uuid):
#     try:
#         web_resource_data = handlers.handle_get_resource_data(resource_uuid)
#     except exceptions.NotFoundError:
#         return jsonify({"Error": "Resource with the given UUID not found."})

#     return jsonify(web_resource_data.dict())


# @bp.route("/logs", methods=["GET"])
# def get_logs():
#     log_response = schemes.LogListGetSchema(
#         logs=[schemes.LogRecordSchema(**log) for log in log_buffer]
#     )
#     return jsonify(log_response.dict())


@socketio.on("connect", namespace="/logs")
@celery_socketio.on("connect", namespace="/logs")
def connect():
    # app.logger.info("Websocket connection to /logs page")
    logs = log_buffer
    celery_socketio.emit(event="init_logs", data={"logs": logs}, namespace="/logs")
    socketio.emit(event="init_logs", data={"logs": logs}, namespace="/logs")
