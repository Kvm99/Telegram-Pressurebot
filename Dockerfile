FROM python:3
LABEL maintainer="mary@filonova.dev"

WORKDIR /app
COPY . .
RUN cd /app

RUN pip install -r requirements.txt
CMD ["python3", "/app/telegram_pressure_bot.py"]
