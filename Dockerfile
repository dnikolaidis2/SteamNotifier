FROM python:3.8

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir db

COPY main.py .
COPY steam_notifier/ ./steam_notifier

CMD ["python", "main.py"]