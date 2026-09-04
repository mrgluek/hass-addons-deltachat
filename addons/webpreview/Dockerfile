ARG BUILD_FROM=ghcr.io/home-assistant/base-debian:bookworm
FROM ${BUILD_FROM}

ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ARG TARGETARCH
RUN case "${TARGETARCH}" in \
        "amd64") ARCH="x86_64" ;; \
        "arm64") ARCH="aarch64" ;; \
        *) ARCH="x86_64" ;; \
    esac && \
    curl -sSL -o /usr/local/bin/monolith "https://github.com/Y2Z/monolith/releases/download/v2.10.1/monolith-gnu-linux-${ARCH}" && \
    chmod +x /usr/local/bin/monolith

ARG BOT_REPO=deltachat_webpreview
ARG BOT_REF=v2.9.6
RUN (git clone --depth 1 -b ${BOT_REF} https://github.com/mrgluek/${BOT_REPO}.git /app 2>/dev/null || \
     git clone --depth 1 -b ${BOT_REF} https://git.gluek.info/gluek/${BOT_REPO}.git /app 2>/dev/null || \
     git clone --depth 1 https://github.com/mrgluek/${BOT_REPO}.git /app || \
     git clone --depth 1 https://git.gluek.info/gluek/${BOT_REPO}.git /app)

RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY run.sh /run.sh
RUN chmod a+x /run.sh

VOLUME ["/data"]
ENV DC_DB_DIR=/data \
    DB_PATH=/data/webpreview.db

CMD [ "/run.sh" ]
