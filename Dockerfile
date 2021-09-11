FROM python:3.8-slim

RUN apt-get update \
&& apt-get install gcc ffmpeg -y \
&& apt-get clean

EXPOSE 8000
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
COPY . /app/
WORKDIR /app
RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
