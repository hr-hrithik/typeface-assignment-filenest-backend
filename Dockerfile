# Stage 1: Build stage
FROM python:3.12-slim AS builder

# Install build dependencies
RUN apt-get update  
RUN apt-get install -y gcc 
        
# Create a virtual environment
RUN python -m venv /opt/venv

# Set the path to the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install the required packages
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Stage 2: Final stage
FROM python:3.12-slim

# Set environment variables
# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1

# Install runtime dependencies
RUN apt-get update
RUN apt-get clean all

# Copy the virtual environment from the build stage
COPY --from=builder /opt/venv /opt/venv

# Set the path to the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Set the working directory
WORKDIR /

# Copy the application code
COPY . .

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--env-file", "prod.env", "--workers", "2"]
