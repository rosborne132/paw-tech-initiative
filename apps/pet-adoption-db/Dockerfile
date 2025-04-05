FROM apache/airflow:2.7.2

# Set environment variables for Airflow
ENV AIRFLOW_HOME=/opt/airflow
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False

# Copy custom DAGs into the container
COPY dags/ $AIRFLOW_HOME/dags/

# Install additional Python dependencies (if needed)
# RUN pip install <your-dependencies>

# Set the entrypoint to Airflow standalone mode
ENTRYPOINT ["airflow", "standalone"]
