# Python 3.11 slim image for our base
FROM python:3.11-slim

# Set up working directory
WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

#Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code

COPY . .
# . = source (local dir)
# second . = destination (/app)

# Expose port 
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]