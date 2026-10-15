# Pull base image
FROM python:3.12-slim-bullseye

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /code

# Install dependencies
COPY ./requirements.txt .
RUN pip config --user set global.index-url http://nexus.prod.uci.cu/repository/pypi-proxy/simple/ \
 && pip config --user set global.trusted-host nexus.prod.uci.cu
RUN pip install \
    --timeout 120 \
    --retries 10 \
    --no-cache-dir \
    -r requirements.txt

# Copy project
COPY . .
