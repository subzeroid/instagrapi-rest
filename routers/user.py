from typing import Optional, Dict

from fastapi import APIRouter, Depends, Form
from instagrapi.types import (
        User, UserShort
)

from dependencies import ClientStorage, get_clients


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


@router.post("/followers", response_model=Dict[int, UserShort])
async def user_followers(sessionid: str = Form(...), 
                         user_id: str = Form(...), 
                         use_cache: Optional[bool] = Form(True), 
                         amount: Optional[int] = Form(0), 
                         clients: ClientStorage = Depends(get_clients)) -> Dict[int, UserShort]:
    """Get user's followers
    """
    cl = clients.get(sessionid)
    return cl.user_followers(user_id, use_cache, amount)


@router.post("/following", response_model=Dict[int, UserShort])
async def user_following(sessionid: str = Form(...), 
                         user_id: str = Form(...), 
                         use_cache: Optional[bool] = Form(True), 
                         amount: Optional[int] = Form(0), 
                         clients: ClientStorage = Depends(get_clients)) -> Dict[int, UserShort]:
    """Get user's followers information
    """
    cl = clients.get(sessionid)
    return cl.user_following(user_id, use_cache, amount)


@router.post("/info", response_model=User)
async def user_info(sessionid: str = Form(...), 
                    user_id: str = Form(...), 
                    use_cache: Optional[bool] = Form(True), 
                    clients: ClientStorage = Depends(get_clients)) -> User:
    """Get user object from user id
    """
    cl = clients.get(sessionid)
    return cl.user_info(user_id, use_cache)


@router.post("/info_by_username", response_model=User)
async def user_info_by_username(sessionid: str = Form(...), 
                                username: str = Form(...), 
                                use_cache: Optional[bool] = Form(True), 
                                clients: ClientStorage = Depends(get_clients)) -> User:
    """Get user object from username
    """
    cl = clients.get(sessionid)
    return cl.user_info_by_username(username, use_cache)


@router.post("/follow", response_model=bool)
async def user_follow(sessionid: str = Form(...), 
                      user_id: int = Form(...), 
                      clients: ClientStorage = Depends(get_clients)) -> bool:
    """Follow a user
    """
    cl = clients.get(sessionid)
    return cl.user_follow(user_id)


@router.post("/unfollow", response_model=bool)
async def user_unfollow(sessionid: str = Form(...), 
                        user_id: int = Form(...), 
                        clients: ClientStorage = Depends(get_clients)) -> bool:
    """Unfollow a user
    """
    cl = clients.get(sessionid)
    return cl.user_unfollow(user_id)


@router.post("/id_from_username", response_model=int)
async def user_id_from_username(sessionid: str = Form(...), 
                                username: str = Form(...), 
                                clients: ClientStorage = Depends(get_clients)) -> int:
    """Get user id from username
    """
    cl = clients.get(sessionid)
    return cl.user_id_from_username(username)


@router.post("/username_from_id", response_model=str)
async def username_from_user_id(sessionid: str = Form(...), 
                                user_id: int = Form(...), 
                                clients: ClientStorage = Depends(get_clients)) -> str:
    """Get username from user id
    """
    cl = clients.get(sessionid)
    return cl.username_from_user_id(user_id)


@router.post("/remove_follower", response_model=bool)
async def user_remove_follower(sessionid: str = Form(...), 
                               user_id: int = Form(...), 
                               clients: ClientStorage = Depends(get_clients)) -> bool:
    """Remove a follower
    """
    cl = clients.get(sessionid)
    return cl.user_remove_follower(user_id)


@router.post("/mute_posts_from_follow", response_model=bool)
async def mute_posts_from_follow(sessionid: str = Form(...), 
                                 user_id: int = Form(...), 
                                 revert: Optional[bool] = Form(False), 
                                 clients: ClientStorage = Depends(get_clients)) -> bool:
    """Mute posts from following user
    """
    cl = clients.get(sessionid)
    return cl.mute_posts_from_follow(user_id, revert)


@router.post("/unmute_posts_from_follow", response_model=bool)
async def unmute_posts_from_follow(sessionid: str = Form(...), 
                                   user_id: int = Form(...), 
                                   clients: ClientStorage = Depends(get_clients)) -> bool:
    """Unmute posts from following user
    """
    cl = clients.get(sessionid)
    return cl.unmute_posts_from_follow(user_id)


@router.post("/mute_stories_from_follow", response_model=bool)
async def mute_stories_from_follow(sessionid: str = Form(...), 
                                   user_id: int = Form(...), 
                                   revert: Optional[bool] = Form(False), 
                                   clients: ClientStorage = Depends(get_clients)) -> bool:
    """Mute stories from following user
    """
    cl = clients.get(sessionid)
    return cl.mute_stories_from_follow(user_id, revert)


@router.post("/unmute_stories_from_follow", response_model=bool)
async def unmute_stories_from_follow(sessionid: str = Form(...), 
                                     user_id: int = Form(...), 
                                     clients: ClientStorage = Depends(get_clients)) -> bool:
    """Unmute stories from following user
    """
    cl = clients.get(sessionid)
    return cl.unmute_stories_from_follow(user_id)
