from typing import List, Optional, Dict

import requests
from pydantic import HttpUrl
from fastapi import APIRouter, Form
from instagrapi.types import (
        User, UserShort
)

from helpers import photo_upload_story
from dependencies import ClientStorage, get_clients


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


@router.post("/user_followers", response_model=Dict[int, UserShort])
async def user_followers(sessionid: str = Form(...), user_id: str = Form(...), use_cache: Optional[bool] = Form(True), amount: Optional[int] = Form(0)) -> Dict[int, UserShort]:
    """Get user's followers
    """
    cl = clients.get(sessionid)
    return cl.user_followers(user_id, use_cache, amount)


@router.post("/user_following", response_model=Dict[int, UserShort])
async def user_following(sessionid: str = Form(...), user_id: str = Form(...), use_cache: Optional[bool] = Form(True), amount: Optional[int] = Form(0)) -> Dict[int, UserShort]:
    """Get user's followers information
    """
    cl = clients.get(sessionid)
    return cl.user_following(user_id, use_cache, amount)


@router.post("/user_info", response_model=User)
async def user_info(sessionid: str = Form(...), user_id: str = Form(...), use_cache: Optional[bool] = Form(True)) -> User:
    """Get user object from user id
    """
    cl = clients.get(sessionid)
    return cl.user_info(user_id, use_cache)


@router.post("/user_info_by_username", response_model=User)
async def user_info_by_username(sessionid: str = Form(...), username: str = Form(...), use_cache: Optional[bool] = Form(True)) -> User:
    """Get user object from username
    """
    cl = clients.get(sessionid)
    return cl.user_info_by_username(username, use_cache)


@router.post("/user_follow", response_model=bool)
async def user_follow(sessionid: str = Form(...), user_id: int = Form(...)) -> bool:
    """Follow a user
    """
    cl = clients.get(sessionid)
    return cl.user_follow(user_id)


@router.post("/user_unfollow", response_model=bool)
async def user_unfollow(sessionid: str = Form(...), user_id: int = Form(...)) -> bool:
    """Unfollow a user
    """
    cl = clients.get(sessionid)
    return cl.user_unfollow(user_id)


@router.post("/user_id_from_username", response_model=int)
async def user_id_from_username(sessionid: str = Form(...), username: str = Form(...)) -> int:
    """Get user id from username
    """
    cl = clients.get(sessionid)
    return cl.user_id_from_username(username)


@router.post("/username_from_user_id", response_model=str)
async def username_from_user_id(sessionid: str = Form(...), user_id: int = Form(...)) -> str:
    """Get username from user id
    """
    cl = clients.get(sessionid)
    return cl.username_from_user_id(user_id)


@router.post("/user_remove_follower", response_model=bool)
async def user_remove_follower(sessionid: str = Form(...), user_id: int = Form(...)) -> bool:
    """Remove a follower
    """
    cl = clients.get(sessionid)
    return cl.user_remove_follower(user_id)


@router.post("/mute_posts_from_follow", response_model=bool)
async def mute_posts_from_follow(sessionid: str = Form(...), user_id: int = Form(...), revert: Optional[bool] = Form(False)) -> bool:
    """Mute posts from following user
    """
    cl = clients.get(sessionid)
    return cl.mute_posts_from_follow(user_id, revert)


@router.post("/unmute_posts_from_follow", response_model=bool)
async def unmute_posts_from_follow(sessionid: str = Form(...), user_id: int = Form(...)) -> bool:
    """Unmute posts from following user
    """
    cl = clients.get(sessionid)
    return cl.unmute_posts_from_follow(user_id)


@router.post("/mute_stories_from_follow", response_model=bool)
async def mute_stories_from_follow(sessionid: str = Form(...), user_id: int = Form(...), revert: Optional[bool] = Form(False)) -> bool:
    """Mute stories from following user
    """
    cl = clients.get(sessionid)
    return cl.mute_stories_from_follow(user_id, revert)


@router.post("/unmute_stories_from_follow", response_model=bool)
async def unmute_stories_from_follow(sessionid: str = Form(...), user_id: int = Form(...)) -> bool:
    """Unmute stories from following user
    """
    cl = clients.get(sessionid)
    return cl.unmute_stories_from_follow(user_id)
