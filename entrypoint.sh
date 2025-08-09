#!/usr/bin/env bash
set -euo pipefail

# 1) GCPサービスアカウントJSONをファイル化
#   Renderの環境変数 GCP_SA_JSON に“JSON全文”を入れておく
mkdir -p /app/secrets
if [ -n "${GCP_SA_JSON:-}" ]; then
  echo "$GCP_SA_JSON" > /app/secrets/gcp-sa.json
  export GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/gcp-sa.json
fi

# 2) Uvicornを起動（Renderは $PORT を注入）
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8080}"
