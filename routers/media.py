from fastapi import APIRouter, Depends, Form

from typing import List, Dict, Optional

from instagrapi import Client
from instagrapi.types import Media, Usertag, Location, UserShort

from dependencies import ClientStorage, get_clients


router = APIRouter(
    prefix="/media",
    tags=["media"],
    responses={404: {"description": "Not found"}}
)


@router.get("/id")
async def media_id(media_pk: int) -> str:
    """Get full media id
    """
    return Client().media_id(media_pk)


@router.get("/pk")
async def media_pk(media_id: str) -> str:
    """Get short media id
    """
    return str(Client().media_pk(media_id))


@router.get("/pk_from_code")
async def media_pk_from_code(code: str) -> str:
    """Get media pk from code
    """
    return str(Client().media_pk_from_code(code))


@router.get("/pk_from_url")
async def media_pk_from_url(url: str) -> str:
    """Get Media PK from URL
    """
    return str(Client().media_pk_from_url(url))


@router.post("/info", response_model=Media)
async def media_info(sessionid: str = Form(...),
                     pk: int = Form(...),
                     use_cache: Optional[bool] = Form(True),
                     clients: ClientStorage = Depends(get_clients)) -> Media:
    """Get media info by pk
    """
    cl = clients.get(sessionid)
    return cl.media_info(pk, use_cache)


@router.post("/user_medias", response_model=List[Media])
async def user_medias(sessionid: str = Form(...),
                      user_id: int = Form(...),
                      amount: Optional[int] = Form(50),
                      clients: ClientStorage = Depends(get_clients)) -> List[Media]:
    """Get a user's media
    """
    cl = clients.get(sessionid)
    return cl.user_medias(user_id, amount)


@router.post("/usertag_medias", response_model=List[Media])
async def usertag_medias(sessionid: str = Form(...),
                         user_id: int = Form(...),
                         amount: Optional[int] = Form(50),
                         clients: ClientStorage = Depends(get_clients)) -> List[Media]:
    """Get medias where a user is tagged
    """
    cl = clients.get(sessionid)
    return cl.usertag_medias(user_id, amount)


@router.post("/delete", response_model=bool)
async def media_delete(sessionid: str = Form(...),
                       media_id: str = Form(...),
                       clients: ClientStorage = Depends(get_clients)) -> bool:
    """Delete media by Media ID
    """
    cl = clients.get(sessionid)
    return cl.media_delete(media_id)


@router.post("/edit", response_model=Dict)
async def media_edit(sessionid: str = Form(...),
                     media_id: str = Form(...),
                     caption: str = Form(...),
                     title: Optional[str] = Form(""),
                     usertags: Optional[List[Usertag]] = Form([]),
                     location: Optional[Location] = Form(None),
                     clients: ClientStorage = Depends(get_clients)) -> Dict:
    """Edit caption for media
    """
    cl = clients.get(sessionid)
    return cl.media_edit(media_id, caption, title, usertags, location)


@router.post("/user", response_model=UserShort)
async def media_user(sessionid: str = Form(...),
                     media_pk: int = Form(...),
                     clients: ClientStorage = Depends(get_clients)) -> UserShort:
    """Get author of the media
    """
    cl = clients.get(sessionid)
    return cl.media_user(media_pk)


@router.post("/oembed", response_model=Dict)
async def media_oembed(sessionid: str = Form(...),
                     url: str = Form(...),
                     clients: ClientStorage = Depends(get_clients)) -> Dict:
    """Return info about media and user from post URL
    """
    cl = clients.get(sessionid)
    return cl.media_oembed(url)


@router.post("/like", response_model=bool)
async def media_like(sessionid: str = Form(...),
                     media_id: str = Form(...),
                     revert: Optional[bool] = Form(False),
                     clients: ClientStorage = Depends(get_clients)) -> bool:
    """Like a media
    """
    cl = clients.get(sessionid)
    return cl.media_like(media_id, revert)


@router.post("/unlike", response_model=bool)
async def media_unlike(sessionid: str = Form(...),
                       media_id: str = Form(...),
                       clients: ClientStorage = Depends(get_clients)) -> bool:
    """Unlike a media
    """
    cl = clients.get(sessionid)
    return cl.media_unlike(media_id)


@router.post("/seen", response_model=bool)
async def media_seen(sessionid: str = Form(...),
                     media_ids: List[str] = Form(...),
                     skipped_media_ids: Optional[List[str]] = Form([]),
                     clients: ClientStorage = Depends(get_clients)) -> bool:
    """Mark a media as seen
    """
    cl = clients.get(sessionid)
    return cl.media_seen(media_ids, skipped_media_ids)


@router.post("/likers", response_model=List[UserShort])
async def media_likers(sessionid: str = Form(...),
                     media_id: str = Form(...),
                     clients: ClientStorage = Depends(get_clients)) -> List[UserShort]:
    """Get user's likers
    """
    cl = clients.get(sessionid)
    return cl.media_likers(media_id)


@router.post("/archive", response_model=bool)
async def media_archive(sessionid: str = Form(...),
                     media_id: str = Form(...),
                     revert: Optional[bool] = Form(False),
                     clients: ClientStorage = Depends(get_clients)) -> bool:
    """Archive a media
    """
    cl = clients.get(sessionid)
    return cl.media_archive(media_id, revert)


@router.post("/unarchive", response_model=bool)
async def media_unarchive(sessionid: str = Form(...),
                     media_id: str = Form(...),
                     clients: ClientStorage = Depends(get_clients)) -> bool:
    """Unarchive a media
    """
    cl = clients.get(sessionid)
    return cl.media_unarchive(media_id)
