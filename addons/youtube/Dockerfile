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
    ffmpeg \
    curl \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Deno for yt-dlp JavaScript challenge execution
RUN curl -fsSL https://deno.land/install.sh | sh
ENV DENO_INSTALL=/root/.deno
ENV PATH=$DENO_INSTALL/bin:$PATH

ARG BOT_REPO=deltachat_yt
ARG BOT_REF=v1.6.54
RUN (git clone --depth 1 -b ${BOT_REF} https://github.com/mrgluek/${BOT_REPO}.git /app 2>/dev/null || \
     git clone --depth 1 -b ${BOT_REF} https://git.gluek.info/gluek/${BOT_REPO}.git /app 2>/dev/null || \
     git clone --depth 1 https://github.com/mrgluek/${BOT_REPO}.git /app || \
     git clone --depth 1 https://git.gluek.info/gluek/${BOT_REPO}.git /app)

RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY run.sh /run.sh
RUN chmod a+x /run.sh

VOLUME ["/data"]
ENV DC_DB_DIR=/data \
    DB_PATH=/data/ytbot.db

CMD [ "/run.sh" ]
