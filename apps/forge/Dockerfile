FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi==0.111.0 uvicorn==0.30.1 httpx==0.27.0 python-multipart==0.0.9 jinja2==3.1.4
COPY main.py .
COPY static ./static
COPY pages ./pages
RUN mkdir -p /app/jobs && echo 'ARENA{forge_job_file}' > /app/jobs/private.env
EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
