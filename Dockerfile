FROM python:3.9-alpine
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi uvicorn
EXPOSE 8000
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]