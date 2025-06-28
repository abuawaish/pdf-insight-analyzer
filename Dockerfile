# Use Python 3.11 base image (not 3.13)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set port (Render injects this at runtime)
ENV PORT=10000
EXPOSE 10000

# Start your Flask app with gunicorn (adjust if needed)
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]
