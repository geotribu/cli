FROM python:3.13-slim

# Avoid .pyc bytecode and ensure output is unbuffered for CLI responsiveness
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=2

# Add user's local bin directory to PATH for pip installed packages
ENV PATH="/home/geotribuser/.local/bin:$PATH"

# Set locale to French UTF-8
RUN apt update && \
    apt install -y --no-install-recommends locales && \
    echo "fr_FR.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

ENV LANG=fr_FR.UTF-8 \
    LANGUAGE=fr_FR:fr \
    LC_ALL=fr_FR.UTF-8

# Create non-root group and user dedicated to geotribu usage
RUN groupadd --system geotribu && \
    useradd -m -s /bin/bash -g geotribu geotribuser

USER geotribuser

# Set working directory and proper permissions
WORKDIR /home/geotribuser

# Custom CLI settings
ENV GEOTRIBU_CACHE_EXPIRATION_HOURS=240 \
    GEOTRIBU_COMMENTS_EXPIRATION_HOURS=240 \
    GEOTRIBU_RESULTATS_FORMAT=table \
    GEOTRIBU_RESULTATS_NOMBRE=20

COPY --chown=geotribuser:geotribu . .

RUN pip install --no-cache-dir .[all] \
    && rm -rf ~/.cache/pip \
    && geotribu sc --no-prompt "qgis" \
    && geotribu si --no-prompt "qgis" \
    && geotribu comments latest

ENTRYPOINT ["geotribu"]
CMD []
