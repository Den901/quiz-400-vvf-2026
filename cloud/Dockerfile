FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    Q400_ENV=production

WORKDIR /srv/quiz400

RUN addgroup --system --gid 10001 quiz400 && adduser --system --uid 10001 --ingroup quiz400 quiz400

COPY cloud/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY --chown=quiz400:quiz400 cloud ./cloud
COPY --chown=quiz400:quiz400 app.js challenge-reminders.js logic-topics.js subject-topics.js tutor.js notes-ui.js study-notes.js practice-notes.js study-paths.js study-paths-ui.js study-content-ui.js study-checkpoint.js element-properties.js quiz-selection.js data.js index.html manifest.webmanifest sw.js version.json release-notes.json ./
COPY --chown=quiz400:quiz400 styles.css styles-extra.css styles-guided.css styles-official.css styles-cloud.css styles-theme.css styles-notes.css styles-study-paths.css ./
COPY --chown=quiz400:quiz400 logo-vvf.jpg logo-vvf.png quiz-dataset.json quiz-images.json ./
COPY --chown=quiz400:quiz400 quiz-images ./quiz-images
COPY --chown=quiz400:quiz400 study-materials/images ./study-materials/images
COPY --chown=quiz400:quiz400 study-content ./study-content

USER quiz400

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)"

CMD ["sh", "-c", "alembic -c cloud/alembic.ini upgrade head && exec uvicorn cloud.app:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips '*'"]
