# RESTful API Service for instagrapi

Allows you to use the [private Instagram API](https://github.com/adw0rd/instagrapi) on any operating system from any programming language to automate the work of your accounts

[![Tests](https://github.com/adw0rd/instagrapi-rest/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/adw0rd/instagrapi-rest/actions/workflows/tests.yml)

# Installation

To run, you need to install Docker and clone the repository:

```
git clone https://github.com/adw0rd/instagrapi-rest.git
cd instagrapi-rest
```

Run docker container:

```
docker build -t instagrapi-rest_api .
docker run --rm -p 8000:8000 instagrapi-rest_api
```

Or you can use docker-compose:

```
docker-compose up -d
```

# Usage

Open in browser [http://localhost:8000/docs](http://localhost:8000/docs) and follow the instructions

# Testing

Tests can be run like this:

`docker run --rm -v $(pwd):/app instagrapi-rest_api pytest tests.py`
