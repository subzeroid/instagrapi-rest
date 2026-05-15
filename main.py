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
OPENAPI_DESCRIPTION = """
RESTful HTTP service for `aiograpi`, the async Instagram Private API wrapper.

- [GitHub repository](https://github.com/subzeroid/aiograpi-rest)
- [HikerAPI with 100 free requests](https://hikerapi.com/p/7RAo9ACK)
""".strip()
OPENAPI_TAGS = [
    {"name": "System", "description": "Service metadata and documentation redirects."},
    {"name": "Auth", "description": "Login, session settings, and relogin operations."},
    {"name": "User", "description": "Profile lookup and user relationship operations."},
    {"name": "Media", "description": "Generic media lookup, edits, and interactions."},
    {"name": "Photo", "description": "Feed photo download and upload operations."},
    {"name": "Video", "description": "Feed video download and upload operations."},
    {"name": "Clip (Reels)", "description": "Instagram Reels clip download and upload operations."},
    {"name": "Album (Carousel)", "description": "Carousel album download and upload operations."},
    {"name": "Story", "description": "Story lookup, upload, download, and interactions."},
    {"name": "IGTV (Legacy)", "description": "Legacy IGTV operations still exposed by aiograpi."},
    {"name": "Insights", "description": "Account and media insights."},
]
OPERATION_SUMMARIES = {
    "postAuthLogin": "Log in with username and password",
    "postAuthLoginBySessionId": "Create a session from an existing session ID",
    "patchAuthRelogin": "Refresh the current login session",
    "getAuthSettings": "Get saved auth settings",
    "patchAuthSettings": "Save auth settings",
    "getAuthTimelineFeed": "Get authenticated timeline feed",
    "getMediaId": "Build a media ID from media PK",
    "getMediaPk": "Extract media PK from media ID",
    "getMediaPkFromCode": "Get media PK from shortcode",
    "getMediaPkFromUrl": "Get media PK from URL",
    "getMediaInfo": "Get media details",
    "getMediaUserMedias": "List user media",
    "getMediaUsertagMedias": "List media where a user is tagged",
    "deleteMediaDelete": "Delete media",
    "patchMediaEdit": "Edit media caption",
    "getMediaUser": "Get media author",
    "getMediaOembed": "Get media oEmbed data",
    "postMediaLike": "Like media",
    "deleteMediaUnlike": "Unlike media",
    "patchMediaSeen": "Mark media as seen",
    "getMediaLikers": "List media likers",
    "patchMediaArchive": "Archive media",
    "patchMediaUnarchive": "Unarchive media",
    "getPhotoDownload": "Download feed photo",
    "getPhotoDownloadByUrl": "Download feed photo from a URL",
    "postPhotoUpload": "Upload a feed photo",
    "postPhotoUploadByUrl": "Upload a feed photo from a URL",
    "getVideoDownload": "Download feed video",
    "getVideoDownloadByUrl": "Download feed video from a URL",
    "postVideoUpload": "Upload a feed video",
    "postVideoUploadByUrl": "Upload a feed video from a URL",
    "getIgtvDownload": "Download legacy IGTV video",
    "getIgtvDownloadByUrl": "Download legacy IGTV video from a URL",
    "postIgtvUpload": "Upload legacy IGTV video",
    "postIgtvUploadByUrl": "Upload legacy IGTV video from a URL",
    "getClipDownload": "Download a Reel",
    "getClipDownloadByUrl": "Download a Reel from a URL",
    "postClipUpload": "Upload a Reel",
    "postClipUploadByUrl": "Upload a Reel from a URL",
    "getAlbumDownload": "Download carousel album media",
    "getAlbumDownloadByUrls": "Download carousel album media from URLs",
    "postAlbumUpload": "Upload a carousel album",
    "postStoryUpload": "Upload a story",
    "postStoryUploadByUrl": "Upload a story from a URL",
    "getStoryUserStories": "List user stories",
    "getStoryInfo": "Get story details",
    "deleteStoryDelete": "Delete a story",
    "patchStorySeen": "Mark stories as seen",
    "postStoryLike": "Like a story",
    "deleteStoryUnlike": "Unlike a story",
    "getStoryPkFromUrl": "Get story PK from URL",
    "getStoryDownload": "Download story media",
    "getStoryDownloadByUrl": "Download story media from a URL",
    "getUserFollowers": "List user followers",
    "getUserFollowing": "List accounts a user follows",
    "getUserInfo": "Get user profile by ID",
    "getUserInfoByUsername": "Get user profile by username",
    "getUserAbout": "Get user about details",
    "postUserFollow": "Follow a user",
    "deleteUserUnfollow": "Unfollow a user",
    "getUserIdFromUsername": "Get user ID from username",
    "getUserUsernameFromId": "Get username from user ID",
    "deleteUserRemoveFollower": "Remove a follower",
    "patchUserMutePostsFromFollow": "Mute posts from a followed user",
    "patchUserUnmutePostsFromFollow": "Unmute posts from a followed user",
    "patchUserMuteStoriesFromFollow": "Mute stories from a followed user",
    "patchUserUnmuteStoriesFromFollow": "Unmute stories from a followed user",
    "getInsightsMediaFeedAll": "Get account media insights feed",
    "getInsightsAccount": "Get account insights",
    "getInsightsMedia": "Get media insights",
    "getRoot": "Open Swagger UI",
    "getVersion": "Get dependency versions",
}


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


def _polish_operation_summaries(openapi_schema: dict[str, Any]) -> None:
    for methods in openapi_schema.get("paths", {}).values():
        for operation in methods.values():
            summary = OPERATION_SUMMARIES.get(operation.get("operationId"))
            if summary:
                operation["summary"] = summary


app = FastAPI(
    generate_unique_id_function=generate_operation_id,
    openapi_tags=OPENAPI_TAGS,
)
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


@app.get("/", tags=["System"], summary="Redirect to /docs")
async def root():
    """Redirect to /docs
    """
    return RedirectResponse(url="/docs")


@app.get("/version", tags=["System"], summary="Get dependency versions")
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
        title="aiograpi-rest",
        version="1.0.2",
        description=OPENAPI_DESCRIPTION,
        routes=app.routes,
        tags=OPENAPI_TAGS,
        external_docs={
            "description": "GitHub repository",
            "url": "https://github.com/subzeroid/aiograpi-rest",
        },
    )
    _rename_generated_body_schemas(openapi_schema)
    _polish_operation_summaries(openapi_schema)
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
