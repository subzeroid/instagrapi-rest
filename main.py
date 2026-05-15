import re
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from starlette.responses import JSONResponse, RedirectResponse

from routers import album, auth, clip, igtv, insights, media, photo, story, user, video

_TOKEN_OVERRIDES = {
    "id": "Id",
    "igtv": "Igtv",
    "pk": "Pk",
    "sessionid": "SessionId",
    "url": "Url",
}
_HTTP_METHOD_PREFIXES = {"delete", "get", "patch", "post", "put"}


def _word_to_pascal(word: str) -> str:
    return _TOKEN_OVERRIDES.get(word, word[:1].upper() + word[1:])


def _path_words(path: str) -> list[str]:
    words: list[str] = []
    for segment in path.strip("/").split("/"):
        segment = segment.strip("{}")
        words.extend(word for word in re.split(r"[_-]+", segment.lower()) if word)
    return words or ["root"]


def _to_pascal(words: list[str]) -> str:
    return "".join(_word_to_pascal(word) for word in words)


def _to_lower_camel(words: list[str]) -> str:
    pascal = _to_pascal(words)
    return pascal[:1].lower() + pascal[1:]


def generate_operation_id(route: APIRoute) -> str:
    assert route.methods
    method = sorted(route.methods)[0].lower()
    return _to_lower_camel([method, *_path_words(route.path_format)])


def _operation_id_words(operation_id: str) -> list[str]:
    words = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", operation_id).split()
    return [word.lower() for word in words]


def _request_schema_name(body_schema_name: str) -> str:
    words = _operation_id_words(body_schema_name.removeprefix("Body_"))
    if words and words[0] in _HTTP_METHOD_PREFIXES:
        words = words[1:]
    return f"{_to_pascal(words)}Request"


def _replace_schema_refs(value: Any, ref_replacements: dict[str, str]) -> None:
    if isinstance(value, dict):
        ref = value.get("$ref")
        if ref in ref_replacements:
            value["$ref"] = ref_replacements[ref]
        for child in value.values():
            _replace_schema_refs(child, ref_replacements)
    elif isinstance(value, list):
        for item in value:
            _replace_schema_refs(item, ref_replacements)


def _rename_generated_body_schemas(openapi_schema: dict[str, Any]) -> None:
    schemas = openapi_schema.get("components", {}).get("schemas", {})
    ref_replacements: dict[str, str] = {}
    for old_name in list(schemas):
        if not old_name.startswith("Body_"):
            continue
        new_name = _request_schema_name(old_name)
        schemas[new_name] = schemas.pop(old_name)
        schemas[new_name]["title"] = new_name
        ref_replacements[f"#/components/schemas/{old_name}"] = f"#/components/schemas/{new_name}"
    _replace_schema_refs(openapi_schema, ref_replacements)


app = FastAPI(generate_unique_id_function=generate_operation_id)
app.include_router(auth.router)
app.include_router(media.router)
app.include_router(video.router)
app.include_router(photo.router)
app.include_router(user.router)
app.include_router(igtv.router)
app.include_router(clip.router)
app.include_router(album.router)
app.include_router(story.router)
app.include_router(insights.router)


@app.get("/", tags=["system"], summary="Redirect to /docs")
async def root():
    """Redirect to /docs
    """
    return RedirectResponse(url="/docs")


@app.get("/version", tags=["system"], summary="Get dependency versions")
async def version():
    """Get dependency versions
    """
    versions = {}
    for name in ('aiograpi',):
        try:
            versions[name] = package_version(name)
        except PackageNotFoundError:
            versions[name] = None
    return versions


@app.exception_handler(Exception)
async def handle_exception(request, exc: Exception):
    return JSONResponse({
        "detail": str(exc),
        "exc_type": str(type(exc).__name__)
    }, status_code=500)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    # for route in app.routes:
    #     body_field = getattr(route, 'body_field', None)
    #     if body_field:
    #         body_field.type_.__name__ = 'name'
    openapi_schema = get_openapi(
        title="instagrapi-rest",
        version="3.1.0",
        description="RESTful API Service for aiograpi",
        routes=app.routes,
    )
    _rename_generated_body_schemas(openapi_schema)
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
