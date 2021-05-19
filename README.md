# RESTful API Service for instagrapi

[![Tests](https://github.com/adw0rd/instagrapi-rest/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/adw0rd/instagrapi-rest/actions/workflows/tests.yml)

Allows you to use the [Instagram Private API](https://github.com/adw0rd/instagrapi) on any operating system from any programming language to automate the work of your accounts

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
[![Donate](https://www.buymeacoffee.com/assets/img/custom_images/yellow_img.png)](https://www.buymeacoffee.com/adw0rd)


# Installation

To run, you need to install Docker and clone the repository:
```
git clone https://github.com/adw0rd/instagrapi-rest.git
cd instagrapi-rest
```

Run docker container:
```
docker pull adw0rd/instagrapi-rest:latest
docker run adw0rd/instagrapi-rest
```

Or you can build your image and run the container
```
docker build -t instagrapi-rest .
docker run -p 8000:8000 instagrapi-rest
```

Or you can use docker-compose:
```
docker-compose up -d
```

# Usage

Open in browser [http://localhost:8000/docs](http://localhost:8000/docs) and follow the instructions

![image](https://user-images.githubusercontent.com/546889/118844510-af160c00-b8d3-11eb-9f6b-e9773ab12028.png)


# Testing

Tests can be run like this:

`docker run --rm -v $(pwd):/app instagrapi-rest pytest tests.py`

# Development

For debugging:

`docker-compose run --service-ports api`
