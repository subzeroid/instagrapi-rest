import tempfile

from instagrapi.story import StoryBuilder


async def photo_upload_story(cl, content, caption, **kwargs):
    with tempfile.NamedTemporaryFile(suffix='.jpg') as fp:
        fp.write(content)
        mentions = kwargs.get('mentions') or []
        video = StoryBuilder(fp.name, caption, mentions).photo(15)
        return cl.video_upload_to_story(video.path, caption, **kwargs)


async def video_upload_story(cl, content, caption, **kwargs):
    with tempfile.NamedTemporaryFile(suffix='.mp4') as fp:
        fp.write(content)
        mentions = kwargs.get('mentions') or []
        video = StoryBuilder(fp.name, caption, mentions).video(15)
        return cl.video_upload_to_story(video.path, caption, **kwargs)
