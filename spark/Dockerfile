ARG OPENJDK_TAG=8u292
FROM openjdk:${OPENJDK_TAG}

ARG SBT_VERSION=1.4.9

# Install sbt
RUN \
    mkdir /working/ && \
    cd /working/ && \
    curl -L -o sbt-$SBT_VERSION.deb https://repo.scala-sbt.org/scalasbt/debian/sbt-$SBT_VERSION.deb && \
    dpkg -i sbt-$SBT_VERSION.deb && \
    rm sbt-$SBT_VERSION.deb && \
    apt-get update && \
    apt-get install sbt && \
    cd && \
    rm -r /working/ && \
    sbt sbtVersion


WORKDIR /app

COPY data-etl /app

# sbt 
RUN sbt update
RUN sbt clean
RUN sbt test
RUN sbt assembly

CMD ["bash"]
