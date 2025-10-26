# devika-sajeesh/devpulse/Dockerfile (Updated)

# --- 1. Build Stage (Node.js for Frontend) ---
# Use a minimal Node image for building the React app
FROM node:18-alpine AS frontend_builder

WORKDIR /app/frontend

# Copy package files and install dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy source code and build the React app
COPY frontend/src ./src
COPY frontend/public ./public
RUN npm run build 
# The build output (static files) will be in /app/frontend/build


# --- 2. Runtime Stage (Python for FastAPI/ML/Backend) ---
# Use a slim Python base image
FROM python:3.11-slim AS runtime

# Set environment variables for non-interactive commands
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

# Install system dependencies needed for Git and Uvicorn
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python dependencies and install them
COPY requirements.txt .
# Install Python dependencies including gitpython, scikit-learn
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install radon


# Copy ML model and backend code
COPY ml ./ml
COPY backend ./backend
COPY devpulse.db .
COPY .env .

# Copy the built frontend static files from the build stage
COPY --from=frontend_builder /app/frontend/build /app/frontend/build

# Define the command to train the model on container startup (if not already done)
# and then run Uvicorn, serving the FastAPI app.
# We modify the startup command to check for model existence and load it.
CMD ["sh", "-c", "python -c \"from backend.services.predictor import load_ml_model; load_ml_model()\" && uvicorn backend.main:app --host 0.0.0.0 --port 8000"]