FROM python:3.12

WORKDIR /app/services/media-service

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "service.py"]