FROM data-etl-base:latest

ADD notebooks ./

# -- Layer: JupyterLab + Python kernel for PySpark

ARG JUPYTERLAB_VERSION=3.0.0
ARG SCALA_KERNEL_VERSION=0.9.0

RUN apt-get update -y && \
    pip install --upgrade pip && \
    pip install wget==3.2 jupyterlab==${JUPYTERLAB_VERSION}


RUN pip install matplotlib==3.5.1 && \
    pip install psycopg2==2.9.3

# -- Layer: Scala kernel for Spark

ARG SCALA_VERSION=2.12.10

RUN apt-get install -y ca-certificates-java --no-install-recommends && \
    curl -Lo coursier https://git.io/coursier-cli && \
    chmod +x coursier && \
    ./coursier launch --fork almond:${SCALA_KERNEL_VERSION} --scala ${SCALA_VERSION} -- --display-name "Scala ${SCALA_VERSION}" --install && \
    rm -f coursier

# -- Runtime

EXPOSE 8888

WORKDIR ${WORKSPACE}

CMD jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=