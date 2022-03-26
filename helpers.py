import tempfile
import os
from instagrapi.story import StoryBuilder


async def photo_upload_story_as_video(cl, content, **kwargs):
    with tempfile.NamedTemporaryFile(suffix='.jpg') as fp:
        fp.write(content)
        mentions = kwargs.get('mentions') or []
        caption = kwargs.get('caption') or ''
        video = StoryBuilder(fp.name, caption, mentions).photo(15)
        return cl.video_upload_to_story(video.path, **kwargs)


async def photo_upload_story_as_photo(cl, content, **kwargs):
    with tempfile.NamedTemporaryFile(suffix='.jpg') as fp:
        fp.write(content)
        return cl.photo_upload_to_story(fp.name, **kwargs)


async def video_upload_story(cl, content, **kwargs):
    with tempfile.NamedTemporaryFile(suffix='.mp4') as fp:
        fp.write(content)
        mentions = kwargs.get('mentions') or []
        caption = kwargs.get('caption') or ''
        video = StoryBuilder(fp.name, caption, mentions).video(15)
        return cl.video_upload_to_story(video.path, **kwargs)


async def photo_upload_post(cl, content, **kwargs):
    with tempfile.NamedTemporaryFile(suffix='.jpg') as fp:
        fp.write(content)
        return cl.photo_upload(fp.name, **kwargs)


async def video_upload_post(cl, content, **kwargs):
    with tempfile.NamedTemporaryFile(suffix='.mp4') as fp:
        fp.write(content)
        return cl.video_upload(fp.name, **kwargs)


async def album_upload_post(cl, files, **kwargs):
    with tempfile.TemporaryDirectory() as td:
        paths = []
        for i in range(len(files)):
            filename, ext = os.path.splitext(files[i].filename)
            fp = tempfile.NamedTemporaryFile(suffix=ext, delete=False, dir=td)
            fp.write(await files[i].read())
            fp.close()
            paths.append(fp.name)
        return cl.album_upload(paths, **kwargs)


async def igtv_upload_post(cl, content, **kwargs):
    with tempfile.NamedTemporaryFile(suffix='.mp4') as fp:
        fp.write(content)
        return cl.igtv_upload(fp.name, **kwargs)


async def clip_upload_post(cl, content, **kwargs):
    with tempfile.NamedTemporaryFile(suffix='.mp4') as fp:
        fp.write(content)
        return cl.clip_upload(fp.name, **kwargs)
