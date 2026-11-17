FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY templates templates
COPY static static
RUN mkdir -p /app/data /app/uploads && echo 'ARENA{bazaar_local_file}' > /app/data/secret.txt
EXPOSE 80
CMD ["python", "app.py"]
