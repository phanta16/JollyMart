FROM python:3.12

WORKDIR /app/services/user-service

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "-w", "8", "-b", "0.0.0.0:5003", "service:app"]