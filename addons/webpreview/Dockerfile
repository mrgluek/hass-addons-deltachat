# Stage 1: Build monolith CLI
FROM rust:slim-bookworm AS builder
RUN apt-get update && apt-get install -y --no-install-recommends pkg-config libssl-dev git make && rm -rf /var/lib/apt/lists/*
RUN cargo install monolith

# Stage 2: Runtime
ARG BUILD_FROM=ghcr.io/home-assistant/base-debian:bookworm
FROM ${BUILD_FROM}

ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

COPY --from=builder /usr/local/cargo/bin/monolith /usr/local/bin/monolith

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

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
    DB_PATH=/data/webpreview.db \
    PORT=8080

EXPOSE 8080
CMD [ "/run.sh" ]
