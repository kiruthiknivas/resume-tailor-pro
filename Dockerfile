FROM python:3.12-slim

# Prevent interactive prompts during apt install
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Install system dependencies: TeX Live for pdflatex compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    lmodern \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Ensure storage directories exist with write permissions
RUN mkdir -p output uploads profiles && chmod -R 777 output uploads profiles

# Expose default port
EXPOSE 5000

# Start Gunicorn WSGI server, dynamically binding to $PORT (Render/Hugging Face/Railway)
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 180 app:app"]
