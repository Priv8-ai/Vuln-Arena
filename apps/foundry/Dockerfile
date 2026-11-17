FROM python:3.12-slim
WORKDIR /app
COPY apps/foundry/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY apps/foundry/ .
COPY shared/ui/chrome.css ./static/chrome.css
COPY shared/ui/chrome.js ./static/chrome.js
RUN mkdir -p /app/exports /app/private \
 && printf 'Build 7201\nstatus=passed\n' > /app/exports/sample.log \
 && printf 'queue_scope=kilnworks-worker\n' > /app/private/worker.conf \
 && useradd --system --uid 10001 --create-home arena \
 && chown -R arena:arena /app
USER arena
EXPOSE 8080
CMD ["gunicorn", "foundry.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--timeout", "15"]
