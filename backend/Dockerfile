# Official Playwright image ships Chromium and its OS-level dependencies
# preinstalled and version-matched, avoiding apt package drift on generic
# base images (e.g. python:3.11-slim on Debian trixie lacks some packages
# `playwright install --with-deps` expects).
FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
