FROM python:3.11-slim

# Install OS deps and Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Entrypoint
CMD ["gunicorn", "api.wsgi:application", "--bind", "0.0.0.0:8000"]
