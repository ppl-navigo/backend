FROM python:3.9-alpine
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi uvicorn
ENTRYPOINT ["python", "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "80"]
EXPOSE 80