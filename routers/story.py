from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, Depends, Form
from fastapi.responses import FileResponse
from instagrapi import Client
from instagrapi.types import Story

from dependencies import ClientStorage, get_clients


router = APIRouter(
    prefix="/story",
    tags=["story"],
    responses={404: {"description": "Not found"}},
)


@router.post("/user_stories", response_model=List[Story])
async def story_user_stories(sessionid: str = Form(...), 
                            user_id: str = Form(...), 
                            amount: Optional[int] = Form(None), 
                            clients: ClientStorage = Depends(get_clients)) -> List[Story]:
    """Get a user's stories
    """
    cl = clients.get(sessionid)
    return cl.user_stories(user_id, amount)


@router.post("/info", response_model=Story)
async def story_info(sessionid: str = Form(...), 
                     story_pk: int = Form(...), 
                     use_cache: Optional[bool] = Form(True), 
                     clients: ClientStorage = Depends(get_clients)) -> Story:
    """Get Story by pk or id
    """
    cl = clients.get(sessionid)
    return cl.story_info(story_pk, use_cache)


@router.post("/delete", response_model=bool)
async def story_delete(sessionid: str = Form(...), 
                       story_pk: int = Form(...), 
                       clients: ClientStorage = Depends(get_clients)) -> bool:
    """Delete story
    """
    cl = clients.get(sessionid)
    return cl.story_delete(story_pk)


@router.post("/seen", response_model=bool)
async def story_seen(sessionid: str = Form(...),
                     story_pks: List[int] = Form(...),
                     skipped_story_pks: Optional[List[int]] = Form([]),
                     clients: ClientStorage = Depends(get_clients)) -> bool:
    """Mark a media as seen
    """
    cl = clients.get(sessionid)
    return cl.story_seen(story_pks, skipped_story_pks)

@router.post("/like", response_model=bool)
async def story_like(sessionid: str = Form(...),
                     story_id: str = Form(...),
                     revert: Optional[bool] = Form(False),
                     clients: ClientStorage = Depends(get_clients)) -> bool:
    """Like a Story
    """
    cl = clients.get(sessionid)
    return cl.story_like(story_id, revert)

@router.post("/unlike", response_model=bool)
async def story_unlike(sessionid: str = Form(...),
                     story_id: str = Form(...),
                     clients: ClientStorage = Depends(get_clients)) -> bool:
    """Unlike a Story
    """
    cl = clients.get(sessionid)
    return cl.story_unlike(story_pks)


@router.get("/pk_from_url")
async def story_pk_from_url(url: str) -> int:
    """Get Story (media) PK from URL
    """
    return Client().story_pk_from_url(url)


@router.post("/download")
async def story_download(sessionid: str = Form(...),
                         story_pk: int = Form(...),
                         filename: Optional[str] = Form(""),
                         folder: Optional[Path] = Form(""),
                         returnFile: Optional[bool] = Form(True),
                         clients: ClientStorage = Depends(get_clients)):
    """Download story media by media_type
    """
    cl = clients.get(sessionid)
    result = cl.story_download(story_pk, filename, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@router.post("/download/by_url")
async def story_download_by_url(sessionid: str = Form(...),
                                url: str = Form(...),
                                filename: Optional[str] = Form(""),
                                folder: Optional[Path] = Form(""),
                                returnFile: Optional[bool] = Form(True),
                                clients: ClientStorage = Depends(get_clients)):
    """Download story media using URL
    """
    cl = clients.get(sessionid)
    result = cl.story_download_by_url(url, filename, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result
