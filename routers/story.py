from pathlib import Path
from typing import List, Optional

from aiograpi import Client
from aiograpi.types import Story
from fastapi import APIRouter, Depends, Form, Query
from fastapi.responses import FileResponse

from dependencies import ClientStorage, get_clients

router = APIRouter(
    prefix="/story",
    tags=["story"],
    responses={404: {"description": "Not found"}},
)


@router.get("/user_stories", response_model=List[Story])
async def story_user_stories(sessionid: str = Query(...),
                            user_id: str = Query(...),
                            amount: Optional[int] = Query(None),
                            clients: ClientStorage = Depends(get_clients)) -> List[Story]:
    """Get a user's stories
    """
    cl = await clients.get(sessionid)
    return await cl.user_stories(user_id, amount)


@router.get("/info", response_model=Story)
async def story_info(sessionid: str = Query(...),
                     story_pk: int = Query(...),
                     use_cache: Optional[bool] = Query(True),
                     clients: ClientStorage = Depends(get_clients)) -> Story:
    """Get Story by pk or id
    """
    cl = await clients.get(sessionid)
    return await cl.story_info(story_pk, use_cache)


@router.delete("/delete", response_model=bool)
async def story_delete(sessionid: str = Query(...),
                       story_pk: int = Query(...),
                       clients: ClientStorage = Depends(get_clients)) -> bool:
    """Delete story
    """
    cl = await clients.get(sessionid)
    return await cl.story_delete(story_pk)


@router.patch("/seen", response_model=bool)
async def story_seen(sessionid: str = Form(...),
                     story_pks: List[int] = Form(...),
                     skipped_story_pks: Optional[List[int]] = Form([]),
                     clients: ClientStorage = Depends(get_clients)) -> bool:
    """Mark a media as seen
    """
    cl = await clients.get(sessionid)
    return await cl.story_seen(story_pks, skipped_story_pks)

@router.post("/like", response_model=bool)
async def story_like(sessionid: str = Form(...),
                     story_id: str = Form(...),
                     revert: Optional[bool] = Form(False),
                     clients: ClientStorage = Depends(get_clients)) -> bool:
    """Like a Story
    """
    cl = await clients.get(sessionid)
    return await cl.story_like(story_id, revert)

@router.delete("/unlike", response_model=bool)
async def story_unlike(sessionid: str = Query(...),
                     story_id: str = Query(...),
                     clients: ClientStorage = Depends(get_clients)) -> bool:
    """Unlike a Story
    """
    cl = await clients.get(sessionid)
    return await cl.story_unlike(story_id)


@router.get("/pk_from_url")
async def story_pk_from_url(url: str) -> int:
    """Get Story (media) PK from URL
    """
    return Client().story_pk_from_url(url)


@router.get("/download")
async def story_download(sessionid: str = Query(...),
                         story_pk: int = Query(...),
                         filename: Optional[str] = Query(""),
                         folder: Optional[Path] = Query(""),
                         returnFile: Optional[bool] = Query(True),
                         clients: ClientStorage = Depends(get_clients)):
    """Download story media by media_type
    """
    cl = await clients.get(sessionid)
    result = await cl.story_download(story_pk, filename, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@router.get("/download/by_url")
async def story_download_by_url(sessionid: str = Query(...),
                                url: str = Query(...),
                                filename: Optional[str] = Query(""),
                                folder: Optional[Path] = Query(""),
                                returnFile: Optional[bool] = Query(True),
                                clients: ClientStorage = Depends(get_clients)):
    """Download story media using URL
    """
    cl = await clients.get(sessionid)
    result = await cl.story_download_by_url(url, filename, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result
