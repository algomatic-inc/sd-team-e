# ベースイメージ
FROM public.ecr.aws/lambda/python:3.10 AS base
ENV PYTHONPATH /var/task
COPY requirements.txt ./
RUN python -m pip install --upgrade pip
RUN python3.10 -m pip install -r requirements.txt -t .
COPY app.py ./
COPY app_utils/ ./app_utils/

# 本番用イメージ
FROM base AS prod
CMD ["app.lambda_handler"]

# 開発用イメージ
FROM base AS dev
RUN yum install -y tar gzip
CMD ["app.lambda_handler"]