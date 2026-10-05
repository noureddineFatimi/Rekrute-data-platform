FROM apache/airflow:3.3.2

USER airflow
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

USER root
RUN playwright install-deps chromium

USER airflow
RUN playwright install chromium

COPY dags/ /opt/airflow/dags/
COPY db/ /opt/airflow/db/
COPY services/ /opt/airflow/services/
COPY sources/ /opt/airflow/sources/
COPY config.py /opt/airflow/config.py

ENV PYTHONPATH="/opt/airflow"