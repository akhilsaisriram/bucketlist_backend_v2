    # FROM python:3.12-slim
    # ENV PYTHONUNBUFFERED=1

    # # Install system dependencies
    # RUN apt-get update && apt-get install -y \
    #     binutils \
    #     gdal-bin \
    #     libproj-dev \
    #     libgdal-dev \
    #     postgresql-client \
    #     postgis \
    #     && rm -rf /var/lib/apt/lists/*

    # # Set environment variables for GDAL
    # ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
    # ENV C_INCLUDE_PATH=/usr/include/gdal
    # WORKDIR /app

    # COPY requirements.txt /app/requirements.txt
    # RUN pip install -r requirements.txt

    # COPY . /app
    # # CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


# # Stage 1: Build Stage
# FROM python:3.12-slim AS build

# # Set environment variables
# ENV PYTHONUNBUFFERED=1
# ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
# ENV C_INCLUDE_PATH=/usr/include/gdal

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     binutils \
#     gdal-bin \
#     libproj-dev \
#     libgdal-dev \
#     postgresql-client \
#     postgis \
#     && rm -rf /var/lib/apt/lists/*

# # Set working directory
# WORKDIR /app

# # Copy requirements and install Python dependencies
# COPY requirements.txt /app/requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# # Stage 2: Final Stage
# FROM python:3.12-slim

# # Set environment variables
# ENV PYTHONUNBUFFERED=1
# ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
# ENV C_INCLUDE_PATH=/usr/include/gdal

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     binutils \
#     gdal-bin \
#     libproj-dev \
#     libgdal-dev \
#     postgresql-client \
#     postgis \
#     && rm -rf /var/lib/apt/lists/*

# # Set working directory
# WORKDIR /app

# # Copy installed Python packages from the build stage
# COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# # Copy application code
# COPY . /app

# # Expose the application port
# EXPOSE 8000

# # Command to run the application using Gunicorn
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]

# Stage 1: Build Stage (Base dependencies)
FROM python:3.12-slim AS build

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Install required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    libgdal-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final Image (Minimal Django)
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Install only necessary runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only the installed dependencies from the build stage
COPY --from=build /install /usr/local

# Copy application code
COPY . /app

# Expose the application port
EXPOSE 8000

# Command to run the application using Gunicorn
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
