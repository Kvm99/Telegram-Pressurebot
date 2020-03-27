FROM python:3
LABEL maintainer="mary@filonova.dev"

WORKDIR /app
COPY . .
RUN cd /app

RUN pip install -r requirements.txt
CMD ["/bin/bash", "/app/server.sh"]
