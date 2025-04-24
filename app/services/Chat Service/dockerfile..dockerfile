FROM python:3.12

WORKDIR /app/services/Chat Service

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "service.py"]