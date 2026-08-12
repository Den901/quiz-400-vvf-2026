FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    Q400_ENV=production

WORKDIR /srv/quiz400

RUN addgroup --system --gid 10001 quiz400 && adduser --system --uid 10001 --ingroup quiz400 quiz400

COPY cloud/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY cloud ./cloud
COPY app.js data.js index.html manifest.webmanifest sw.js version.json ./
COPY styles.css styles-extra.css styles-guided.css styles-official.css styles-cloud.css styles-theme.css ./
COPY logo-vvf.jpg logo-vvf.png quiz-dataset.json quiz-images.json ./
COPY quiz-images ./quiz-images

RUN chown -R quiz400:quiz400 /srv/quiz400
USER quiz400

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)"

CMD ["sh", "-c", "alembic -c cloud/alembic.ini upgrade head && exec uvicorn cloud.app:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips '*'"]
