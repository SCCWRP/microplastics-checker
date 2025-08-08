FROM python:3.11-slim-bullseye
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ libssl-dev libffi-dev libpq-dev \
    postgresql postgresql-contrib vim libpcre3 libpcre3-dev \
    cython3 r-base && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Python deps
RUN pip install --no-cache-dir \
    wheel psycopg2 uwsgi flask ipython xlrd flask_session flask_cors \
    Werkzeug "pandas<2.0.0" "sqlalchemy<2.0.0" xlsxwriter openpyxl \
    "numpy<1.24" matplotlib scipy geopy shareplum beautifulsoup4 \
    Flask-Dropzone Flask-WTF boto3

WORKDIR /var/www/checker

