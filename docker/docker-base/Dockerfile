ARG PYTHON_VERSION=3.7
FROM python:${PYTHON_VERSION}-stretch

ARG SCALA_VERSION=2.12.10
ARG WORKSPACE=/home/workspace

RUN mkdir -p ${WORKSPACE}

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    apt-get install -y gnupg2 && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EB9B1D8886F44E2A && \
    add-apt-repository "deb http://security.debian.org/debian-security stretch/updates main" && \
    apt-get update && \
    apt-get install -y openjdk-8-jdk && \
    pip freeze && \
    java -version $$ \
    javac -version

ENV JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64"
RUN export JAVA_HOME

RUN curl https://downloads.lightbend.com/scala/${SCALA_VERSION}/scala-${SCALA_VERSION}.deb -k -o scala.deb && \
    apt install -y ./scala.deb && \
    rm -rf scala.deb

ENV SCALA_HOME="/usr/bin/scala"
ENV PATH=${PATH}:${SCALA_HOME}/bin

ADD docker/docker-base/requirements.txt .
RUN pip install -r requirements.txt

WORKDIR ${WORKSPACE}
CMD ["bash"]