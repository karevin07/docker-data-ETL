FROM bitnami/spark:3.1.1

WORKDIR ${SHARED_WORKSPACE}
USER root

ADD docker/docker-airflow/requirements.txt .

RUN pip install -r requirements.txt




