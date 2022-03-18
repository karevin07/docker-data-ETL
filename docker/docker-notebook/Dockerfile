FROM data-etl-base:latest

ADD notebooks ./

# -- Layer: JupyterLab + Python kernel for PySpark

ARG jupyterlab_version=3.0.0
ARG scala_kernel_version=0.9.0

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev && \
    pip3 install --upgrade pip && \
    pip3 install wget==3.2 jupyterlab==${jupyterlab_version}

# -- Layer: Scala kernel for Spark

ARG scala_version=2.12.10

RUN apt-get install -y ca-certificates-java --no-install-recommends && \
    curl -Lo coursier https://git.io/coursier-cli && \
    chmod +x coursier && \
    ./coursier launch --fork almond:${scala_kernel_version} --scala ${scala_version} -- --display-name "Scala ${scala_version}" --install && \
    rm -f coursier

# -- Runtime

EXPOSE 8888

WORKDIR ${WORKSPACE}

CMD jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=