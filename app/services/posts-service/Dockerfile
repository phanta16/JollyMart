FROM python:3.12

WORKDIR /app/services/posts-service

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5009", "service:app"]