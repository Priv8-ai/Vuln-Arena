FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --system --uid 10001 --create-home arena

COPY app.py metadata.py profiles.json experiences.json ./
COPY templates ./templates
COPY static ./static

RUN chown -R arena:arena /app
USER arena
EXPOSE 8080 8081
CMD ["python", "app.py"]
