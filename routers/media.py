from fastapi import APIRouter, Depends, Form

from instagrapi import Client
from instagrapi.types import Media

from dependencies import ClientStorage, get_clients


router = APIRouter(
    prefix="/media",
    tags=["media"],
    responses={404: {"description": "Not found"}}
)

@router.get("/pk_from_code")
async def media_pk_from_code(code: str) -> int:
    """Get media pk from code
    """
    return Client().media_pk_from_code(code)


@router.get("/info", response_model=Media)
async def media_info(sessionid: str = Form(...),
                     pk: int = Form(...),
                     clients: ClientStorage = Depends(get_clients)) -> Media:
    """Get media info by pk
    """
    cl = clients.get(sessionid)
    return cl.media_info(pk)
