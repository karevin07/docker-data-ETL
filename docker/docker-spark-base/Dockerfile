FROM data-etl-base:latest

ARG SPARK_VERSION=3.2.1
ARG HADOOP_VERSION=3.2

WORKDIR ${WORKSPACE}


RUN curl https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz -o spark.tgz && \
    tar -xvf spark.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /usr/bin/ && \
    echo "alias pyspark=/usr/bin/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}/bin/pyspark" >> ~/.bashrc && \
    echo "alias spark-shell=/usr/bin/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}/bin/spark-shell" >> ~/.bashrc && \
    mkdir /usr/bin/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}/logs && \
    rm spark.tgz

ENV SPARK_HOME /usr/bin/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}
ENV SPARK_MASTER_HOST spark
ENV SPARK_MASTER_PORT 7077
ENV PYSPARK_PYTHON python3


WORKDIR ${SPARK_HOME}