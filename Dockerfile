# Data Analysis Dashboard
# Python-based analytics application with streamlit frontend
# 
# Builds a containerized environment for running data analysis dashboards
# with all dependencies isolated in a virtual environment

FROM python:3.12-slim

WORKDIR /app

# Dependencies installation
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Application directory structure
RUN mkdir -p dashboards data

# Application files
COPY dashboards/dashboard.py dashboards/
COPY dashboards/merged_dataset.csv dashboards/
COPY data/hourly_data_cleaned.csv data/

# Network configuration
EXPOSE 8501

# Application startup
CMD ["streamlit", "run", "dashboards/dashboard.py", "--server.address=0.0.0.0", "--server.port=8501"]