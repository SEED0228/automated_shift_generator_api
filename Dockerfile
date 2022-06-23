FROM python:3.8-slim-buster

WORKDIR /app
COPY ./src/ ./

COPY requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["python", "app.py"]