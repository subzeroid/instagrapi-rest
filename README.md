## If you are tired of being blocked when receiving data from Instagram, I recommend using our service - [Lamadava SaaS](https://lamadava.com)

Features:

* Anonymous getting of user, posts, stories, highlights, followers and following users
* Anonymous getting an email and phone number, if the user specified them in his business profile
* Anonymous getting of post, story, album, Reels, IGTV data and the ability to download content
* Anonymous getting of hashtag and location data, as well as a list of posts for them
* Anonymous getting of all comments on a post and a list of users who liked it
* Management of proxy servers, mobile devices, solving captcha and challenge resolver
* Login by username and password, sessionid and support 2FA
* Managing messages and threads for Direct and attach files
* Download and upload a Photo, Video, IGTV, Reels, Albums and Stories
* Work with Users, Posts, Comments, Insights, Collections, Location and Hashtag
* Insights by account, posts and stories
* Like, following, commenting, editing account (Bio) and much more else

---

[![Tests](https://github.com/adw0rd/instagrapi-rest/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/adw0rd/instagrapi-rest/actions/workflows/tests.yml)

# RESTful API Service for [instagrapi](https://github.com/adw0rd/instagrapi)

Allows you to use the [Instagram Private API](https://github.com/adw0rd/instagrapi) on any operating system from any programming language (C++, C#, F#, D, [Golang](golang), Erlang, Elixir, Nim, Haskell, Lisp, Closure, Julia, R, Java, Kotlin, Scala, OCaml, JavaScript, Crystal, Ruby, Rust, [Swift](swift), Objective-C, Visual Basic, .NET, Pascal, Perl, Lua, PHP and others) to automate the work of your accounts. 

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
[![Donate](https://www.buymeacoffee.com/assets/img/custom_images/yellow_img.png)](https://www.buymeacoffee.com/adw0rd)

[Support Chat in Telegram](https://t.me/instagrapi)
![](https://gist.githubusercontent.com/m8rge/4c2b36369c9f936c02ee883ca8ec89f1/raw/c03fd44ee2b63d7a2a195ff44e9bb071e87b4a40/telegram-single-path-24px.svg)

# Features

1. Authorization: Login, support 2FA and manage settings
2. Media: info, delete, edit, like, archive and much more else
3. Video: download, upload to feed and story
4. Photo: download, upload to feed and story
5. IGTV: download, upload to feed and story
6. Clip (Reels): download, upload to feed and story
7. Album: download, upload to feed and story
8. Story: info, delete, seen, download and much more else
9. User: followers/following, info, follow/unfollow, remove_follower and much more else
10. Insights: media, account

# Installation

Install ImageMagick library:
```
sudo apt install imagemagick
```

...and comment the line with strict security policies of ImageMagick in `/etc/ImageMagick-6/policy.xml`:
```
<!--<policy domain="path" rights="none" pattern="@*"/>-->
```

Run docker container:
```
docker run adw0rd/instagrapi-rest
```

Or clone the repository:
```
git clone https://github.com/adw0rd/instagrapi-rest.git
cd instagrapi-rest
```

Build your image and run the container:
```
docker build -t instagrapi-rest .
docker run -p 8000:8000 instagrapi-rest
```

Or you can use docker-compose:
```
docker-compose up -d
```

Or manual installation and launch:

```
python3 -m venv .venv
. .venv/bin/activate
pip install -U wheel pip -Ur requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

# Usage

Open in browser [http://localhost:8000/docs](http://localhost:8000/docs) and follow the instructions

![swagger](https://user-images.githubusercontent.com/546889/126989357-8214aa5c-fe42-4be4-b118-bd3585cd3292.png)


Get sessionid:

```
curl -X 'GET' \
  'http://localhost:8000/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=<USERNAME>&password=<PASSWORD>&verification_code=<2FA CODE>'
```

Upload photo:

```
curl -X 'POST' \
  'http://localhost:8000/photo/upload_to_story' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'sessionid=<SESSIONID>' \
  -F 'file=@photo.jpeg;type=image/jpeg'
```

Upload photo by URL:

```
curl -X 'POST' \
  'https://localhost:8000/photo/upload_to_story/by_url' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'sessionid=<SESSIONID>&url=https%3A%2F%2Fapi.telegram.org%2Ffile%2Ftest.jpg'
```

Upload video:

```
curl -X 'POST' \
  'http://localhost:8000/video/upload_to_story' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'sessionid=<SESSIONID>' \
  -F 'file=@video.mp4;type=video/mp4'
```

Upload video by URL:

```
curl -X 'POST' \
  'https://localhost:8000/video/upload_to_story/by_url' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'sessionid=<SESSIONID>&url=https%3A%2F%2Fapi.telegram.org%2Ffile%2Ftest.MP4'
```

# Testing

Tests can be run like this:

`docker-compose run api pytest tests.py`

One test:

`docker-compose run api pytest tests.py::test_media_pk_from_code`

or without docker-compose:

`docker run --rm -v "$(pwd):/app" instagrapi-rest pytest tests.py`

# Development

For debugging:

`docker-compose run --service-ports api`
