# Multi-stage Dockerfile for ECU Log Visualizer
# Stage 1: Builder - Install dependencies
FROM python:3.12-slim as builder

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies to user directory
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime - Create minimal production image
FROM python:3.12-slim

WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /root/.local

# Add local bin to PATH
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/ ./src/
COPY frontend/ ./frontend/
COPY examples/ ./examples/
COPY run_server.py .

# Create uploads directory
RUN mkdir -p uploads

# Expose application port
EXPOSE 8000

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run application
CMD ["python", "run_server.py"]
