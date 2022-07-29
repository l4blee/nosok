# syntax=docker/dockerfile:1

FROM jrottenberg/ffmpeg:3.3-ubuntu AS ffmpeg
FROM python:3.9.6-slim-bullseye AS python

# Move ffmpeg
COPY --from=ffmpeg /usr/local /usr/local

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install essential packages as using -slim pckg
RUN apt update -y && apt upgrade -y
RUN apt install git -y
RUN apt install g++ -y

# Cleaning
RUN apt clean && apt autoremove -y && rm -rf /var/lib/apt/lists/*

WORKDIR /nosok/

# Install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy directories with actual code
COPY bot/ ./bot
COPY backend/ ./backend
COPY frontend/ ./frontend

CMD python backend/asgi.py