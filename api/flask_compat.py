import inspect
import re
from functools import wraps
from types import UnionType
from typing import Any, Optional, Union, get_args, get_origin

from flask import Blueprint, Response as FlaskResponse, jsonify, request as flask_request
from pydantic import BaseModel, ValidationError

from database import jsonable


class HTTPException(Exception):
    def __init__(self, status_code: int, detail: Any = None):
        self.status_code = status_code
        self.detail = detail
        super().__init__(str(detail or status_code))


class Request:
    @property
    def headers(self):
        return flask_request.headers

    @property
    def query_params(self):
        return flask_request.args


class Response:
    def __init__(
        self,
        content: bytes | str = b"",
        media_type: Optional[str] = None,
        status_code: int = 200,
        headers: Optional[dict[str, str]] = None,
    ):
        self.content = content
        self.media_type = media_type
        self.status_code = status_code
        self.headers = headers or {}


class HeaderParam:
    def __init__(self, default: Any = None):
        self.default = default


def Header(default: Any = None) -> HeaderParam:
    return HeaderParam(default)


def _path_for_flask(path: str) -> str:
    return re.sub(r"{([a-zA-Z_][a-zA-Z0-9_]*)}", r"<\1>", path)


def _is_basemodel(annotation: Any) -> bool:
    try:
        return inspect.isclass(annotation) and issubclass(annotation, BaseModel)
    except TypeError:
        return False


def _unwrap_optional(annotation: Any) -> Any:
    origin = get_origin(annotation)
    if origin in (Union, UnionType):
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if len(args) == 1:
            return args[0]
    return annotation


def _convert_value(value: Any, annotation: Any) -> Any:
    if value is None:
        return None

    annotation = _unwrap_optional(annotation)
    if annotation in (inspect.Signature.empty, Any):
        return value
    if annotation is bool:
        if isinstance(value, bool):
            return value
        return str(value).lower() in {"1", "true", "yes", "on"}
    if annotation in (str, int, float):
        return annotation(value)
    return value


def _model_validate(model_cls: type[BaseModel], payload: dict[str, Any]) -> BaseModel:
    if hasattr(model_cls, "model_validate"):
        return model_cls.model_validate(payload)
    return model_cls(**payload)


def _json_response(payload: Any, status_code: int = 200):
    return jsonify(jsonable(payload)), status_code


class APIRouter:
    _counter = 0

    def __init__(self):
        APIRouter._counter += 1
        self.blueprint = Blueprint(f"api_router_{APIRouter._counter}", __name__)

    def get(self, path: str):
        return self._route(path, ["GET"])

    def post(self, path: str):
        return self._route(path, ["POST"])

    def put(self, path: str):
        return self._route(path, ["PUT"])

    def delete(self, path: str):
        return self._route(path, ["DELETE"])

    def _route(self, path: str, methods: list[str]):
        flask_path = _path_for_flask(path)

        def decorator(func):
            signature = inspect.signature(func)

            @wraps(func)
            def view(**path_kwargs):
                try:
                    kwargs = {}
                    body_cache: Optional[dict[str, Any]] = None

                    for name, param in signature.parameters.items():
                        annotation = param.annotation
                        default = param.default

                        if name in path_kwargs:
                            kwargs[name] = _convert_value(path_kwargs[name], annotation)
                            continue

                        if isinstance(default, HeaderParam):
                            header_name = name.replace("_", "-")
                            kwargs[name] = flask_request.headers.get(header_name, default.default)
                            continue

                        if annotation is Request:
                            kwargs[name] = Request()
                            continue

                        if _is_basemodel(annotation):
                            if body_cache is None:
                                body_cache = flask_request.get_json(silent=True) or {}
                            kwargs[name] = _model_validate(annotation, body_cache)
                            continue

                        query_value = flask_request.args.get(name)
                        if query_value is not None:
                            kwargs[name] = _convert_value(query_value, annotation)
                        elif default is not inspect.Signature.empty:
                            kwargs[name] = default
                        else:
                            raise HTTPException(
                                status_code=422,
                                detail=[{"loc": ["query", name], "msg": "Field required"}],
                            )

                    result = func(**kwargs)

                    if isinstance(result, Response):
                        return FlaskResponse(
                            result.content,
                            status=result.status_code,
                            content_type=result.media_type,
                            headers=result.headers,
                        )
                    if isinstance(result, FlaskResponse):
                        return result
                    if isinstance(result, (dict, list)):
                        return _json_response(result)
                    return result
                except ValidationError as exc:
                    try:
                        detail = exc.errors(include_url=False, include_context=False)
                    except TypeError:
                        detail = exc.errors()
                    return _json_response({"detail": detail}, 422)
                except HTTPException as exc:
                    return _json_response({"detail": exc.detail}, exc.status_code)

            endpoint = f"{func.__module__}_{func.__name__}".replace(".", "_")
            self.blueprint.add_url_rule(flask_path, endpoint, view, methods=methods)
            return func

        return decorator
