FROM ubuntu:22.04

ARG WORKSPACE=/home/workspace
ARG PYTHON_VERSION=3.9.17
ENV SCALA_VERSION="2.12.10"
ENV SCALA_HOME="${WORKSPACE}/scala"

# Setup python and java and base system
ENV DEBIAN_FRONTEND noninteractive
ENV LANG=en_US.UTF-8

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -q -y openjdk-8-jdk \
    libsnappy-dev \
    language-pack-en \
    supervisor \
    libsqlite3-dev \
    gcc \
    make \
    git \
    wget \
    zlib1g-dev \
    libffi-dev \
    openssl \
    libssl-dev \
    libbz2-dev \
    musl-dev \
    bzip2 \
    curl


# --- Set environment variables
ENV HOME /app
ENV PYENV_ROOT $HOME/.pyenv
ENV PATH $PYENV_ROOT/shims:$PATH:$PYENV_ROOT/bin
ENV CRYPTOGRAPHY_DONT_BUILD_RUST 1

# ---- Install pyenv
RUN curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer \
    -o pyenv-installer && \
    /bin/sh pyenv-installer && \
    rm pyenv-installer

# ---- Install Python
RUN pyenv install $PYTHON_VERSION
RUN pyenv global $PYTHON_VERSION
RUN pyenv rehash

# ---- Install Scala

RUN cd "/tmp" && \
    wget "https://downloads.typesafe.com/scala/${SCALA_VERSION}/scala-${SCALA_VERSION}.tgz" && \
    tar xzf "scala-${SCALA_VERSION}.tgz" && \
    mkdir -p "${SCALA_HOME}" && \
    rm "/tmp/scala-${SCALA_VERSION}/bin/"*.bat && \
    mv "/tmp/scala-${SCALA_VERSION}/bin" "/tmp/scala-${SCALA_VERSION}/lib" "${SCALA_HOME}" && \
    ln -s "${SCALA_HOME}/bin/"* "/usr/bin/"

ENV PATH=${PATH}:${SCALA_HOME}/bin

# ---- Poetry install

ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN python -c 'from urllib.request import urlopen; print(urlopen("https://install.python-poetry.org").read().decode())' | python -
RUN pip install --upgrade pip

ENV PATH="/.venv/bin:$PATH"
COPY pyproject.toml ./
RUN poetry install --only main --no-root
RUN rm -f ./pyproject.toml && rm -f ./poetry.lock

WORKDIR ${WORKSPACE}

CMD ["bash"]