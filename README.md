# RESTful API Service for instagrapi

[![Tests](https://github.com/adw0rd/instagrapi-rest/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/adw0rd/instagrapi-rest/actions/workflows/tests.yml)

Allows you to use the [Instagram Private API](https://github.com/adw0rd/instagrapi) on any operating system from any programming language (C++, C#, F#, D, Golang, Erlang, Elixir, Nim, Haskell, Lisp, Julia, R, Java, Kotlin, Scala, OCaml, JavaScript, Ruby, Rust, Swift, Objective-C, Visual Basic, .NET, Pascal, Perl, Lua, PHP and others) to automate the work of your accounts. 

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
[![Donate](https://www.buymeacoffee.com/assets/img/custom_images/yellow_img.png)](https://www.buymeacoffee.com/adw0rd)


# Installation

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

![image](https://user-images.githubusercontent.com/546889/118844510-af160c00-b8d3-11eb-9f6b-e9773ab12028.png)


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

`docker run --rm -v $(pwd):/app instagrapi-rest pytest tests.py`

# Development

For debugging:

`docker-compose run --service-ports api`
