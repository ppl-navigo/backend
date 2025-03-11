FROM python:3.9-alpine
RUN addgroup -S nonroot \
    && adduser -S nonroot -G nonroot

USER nonroot
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi uvicorn
ENTRYPOINT ["python", "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "80", "--env-file", ".env"]
EXPOSE 80