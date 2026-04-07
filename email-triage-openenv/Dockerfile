# Email Triage OpenEnv — Docker image
# Compatible with Hugging Face Spaces (Docker Space)

FROM python:3.11-slim

# HF Spaces requires running as non-root user
RUN useradd -m -u 1000 user
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=user:user . .

USER user

# HF Spaces exposes port 7860
EXPOSE 7860

ENV PORT=7860
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

CMD ["python", "app.py"]
