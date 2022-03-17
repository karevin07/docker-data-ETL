FROM bitnami/spark:3.1.1

WORKDIR /home/workspace
USER root

ADD docker/docker-spark/jars/*.jar .
ADD docker/docker-airflow/requirements.txt .


RUN pip install -r requirements.txt

#CMD ["bash"]