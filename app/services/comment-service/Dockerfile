FROM python:3.12

WORKDIR /app/services/comment-service

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5002", "service:app"]