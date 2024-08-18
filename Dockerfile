FROM postgres:15

# Set environment variables from build arguments
ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_DB=${POSTGRES_DB}

# Install Python, pip, and other necessary tools
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    libpq-dev \
    python3-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy application files and install Python dependencies
COPY . /app
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy and set permissions for the initialization script
COPY init-db.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/init-db.sh

# Copy and set permissions for the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose PostgreSQL port for ease of development and testing
EXPOSE 5432

# Use the entrypoint script to handle logic and run the application
ENTRYPOINT ["/entrypoint.sh"]
