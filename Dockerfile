FROM python:3.12-slim

ARG TARGETARCH
ARG SUPABASE_VERSION=1.0.0

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl tar \
    && rm -rf /var/lib/apt/lists/*

RUN set -eu; \
    case "${TARGETARCH:-amd64}" in \
      amd64) SUPABASE_URL="https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20260422/lptmes/supabase_v${SUPABASE_VERSION}_linux_amd64.tar.gz" ;; \
      arm64) SUPABASE_URL="https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20260422/jtbcrh/supabase_v${SUPABASE_VERSION}_linux_arm64.tar.gz" ;; \
      *) echo "Unsupported architecture: ${TARGETARCH}"; exit 1 ;; \
    esac; \
    curl -fsSL "$SUPABASE_URL" -o /tmp/supabase.tar.gz; \
    tar -xzf /tmp/supabase.tar.gz -C /usr/local/bin; \
    chmod +x /usr/local/bin/supabase; \
    rm /tmp/supabase.tar.gz

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py ./

RUN mkdir -p /workspace

WORKDIR /workspace

ENTRYPOINT ["python", "/app/server.py"]
