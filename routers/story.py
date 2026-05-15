from pathlib import Path
from typing import List, Optional

import requests
from aiograpi import Client
from aiograpi.types import (
    Story,
    StoryHashtag,
    StoryLink,
    StoryLocation,
    StoryMention,
    StorySticker,
)
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import FileResponse
from pydantic import AnyHttpUrl

from dependencies import ClientStorage, get_clients
from helpers import photo_upload_story_as_photo, photo_upload_story_as_video, video_upload_story

router = APIRouter(
    prefix="/story",
    tags=["Story"],
    responses={404: {"description": "Not found"}},
)


def _url_points_to_video(url: AnyHttpUrl) -> bool:
    path = str(url).lower().split("?", 1)[0]
    return path.endswith((".mp4", ".mov", ".m4v"))


async def _upload_story_content(cl, content, *, is_video, as_video, **kwargs):
    if is_video:
        return await video_upload_story(cl, content, **kwargs)
    if as_video:
        return await photo_upload_story_as_video(cl, content, **kwargs)
    return await photo_upload_story_as_photo(cl, content, **kwargs)


@router.post("/upload", response_model=Story)
async def story_upload(sessionid: str = Form(...),
                       file: UploadFile = File(...),
                       as_video: Optional[bool] = Form(False),
                       caption: Optional[str] = Form(""),
                       mentions: Optional[List[StoryMention]] = Form([]),
                       locations: Optional[List[StoryLocation]] = Form([]),
                       links: Optional[List[StoryLink]] = Form([]),
                       hashtags: Optional[List[StoryHashtag]] = Form([]),
                       stickers: Optional[List[StorySticker]] = Form([]),
                       clients: ClientStorage = Depends(get_clients)) -> Story:
    """Upload photo or video to story
    """
    cl = await clients.get(sessionid)
    content = await file.read()
    return await _upload_story_content(
        cl, content,
        is_video=(file.content_type or "").startswith("video/"),
        as_video=as_video,
        caption=caption,
        mentions=mentions,
        links=links,
        hashtags=hashtags,
        locations=locations,
        stickers=stickers)


@router.post("/upload/by/url", response_model=Story)
async def story_upload_by_url(sessionid: str = Form(...),
                              url: AnyHttpUrl = Form(...),
                              as_video: Optional[bool] = Form(False),
                              caption: Optional[str] = Form(""),
                              mentions: Optional[List[StoryMention]] = Form([]),
                              locations: Optional[List[StoryLocation]] = Form([]),
                              links: Optional[List[StoryLink]] = Form([]),
                              hashtags: Optional[List[StoryHashtag]] = Form([]),
                              stickers: Optional[List[StorySticker]] = Form([]),
                              clients: ClientStorage = Depends(get_clients)) -> Story:
    """Upload photo or video to story by URL
    """
    cl = await clients.get(sessionid)
    content = requests.get(url).content
    return await _upload_story_content(
        cl, content,
        is_video=_url_points_to_video(url),
        as_video=as_video,
        caption=caption,
        mentions=mentions,
        links=links,
        hashtags=hashtags,
        locations=locations,
        stickers=stickers)


@router.get("/user/stories", response_model=List[Story])
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


@router.get("/pk/from/url")
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


@router.get("/download/by/url")
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
