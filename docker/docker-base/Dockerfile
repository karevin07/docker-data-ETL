FROM openjdk:8-jre-slim

ARG scala_version=2.12.10
ARG shared_workspace=/home/workspace

RUN mkdir -p ${shared_workspace} && \
    apt-get update -y && \
    apt-get install -y curl python3 r-base && \
    ln -s /usr/bin/python3 /usr/bin/python \

RUN curl https://downloads.lightbend.com/scala/${scala_version}/scala-${scala_version}.deb -k -o scala.deb && \
    apt install -y ./scala.deb && \
    rm -rf scala.deb

ENV SCALA_HOME="/usr/bin/scala"
ENV PATH=${PATH}:${SCALA_HOME}/bin

WORKDIR ${shared_workspace}
CMD ["bash"]