FROM python:3.12-slim as base

RUN apt-get update && apt-get install -y 
    
RUN pip install --upgrade pip

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt

RUN pip install --trusted-host pypi.python.org --no-cache-dir -r requirements.txt 

COPY . .

ENV SERVICE=financial-loan

ENV HOST=0.0.0.0
ENV WORKERS=4

EXPOSE 8080

####################### DEBUG ###############################
FROM base as debug
RUN pip install debugpy -t /tmp

####################### PRODUCTION ###############################
FROM base as production
ENTRYPOINT ["uvicorn",  "main:app", "--host", "0.0.0.0", "--port", "8080"]
