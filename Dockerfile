FROM python:3.12

WORKDIR /usr/src/app

# ENV
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Ports
EXPOSE 8000:8000/tcp

# Install requirements
RUN apt update
RUN apt install python3-dev -y

# Install app requirements
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copy sources
COPY . .
