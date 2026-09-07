#!/usr/bin/env bash
# =============================================================================
# Fetch third-party JARs for the Spark cluster
# =============================================================================
# Downloads the JARs that the Spark jobs need at runtime into spark/jars/.
# The directory is bind-mounted into every Spark/Airflow container at
# /home/workspace/jars (see docker-compose.yml). JARs are git-ignored, so
# this script has to run once after cloning and whenever a version changes.
#
# Every download is verified against a pinned SHA-256 checksum.
#
# Usage:
#   bash scripts/fetch-jars.sh          # download missing / outdated JARs
#   bash scripts/fetch-jars.sh --force  # re-download even if already present
# =============================================================================

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

info()    { echo -e "${BLUE}ℹ️  $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warn()    { echo -e "${YELLOW}⚠️  $1${NC}"; }
error()   { echo -e "${RED}❌ $1${NC}"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
JARS_DIR="${PROJECT_DIR}/spark/jars"

FORCE=0
[ "${1:-}" = "--force" ] && FORCE=1

# -----------------------------------------------------------------------------
# JAR registry: "url|filename|sha256"
# Keep the PostgreSQL JDBC version in sync with dags/pkg/settings/setting.py
# (SPARK_EXTRA_PATH).
# -----------------------------------------------------------------------------
JARS=(
  "https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.13/postgresql-42.7.13.jar|postgresql-42.7.13.jar|6e0e4cc2d8cae902084f8a2b18728b073a6fd9d1f87c9d8bff8f298c18185b93"
)

verify() {
  # verify <file> <expected-sha256> -> 0 if match
  local file="$1" expected="$2" actual
  actual="$(sha256sum "$file" | awk '{print $1}')"
  [ "$actual" = "$expected" ]
}

mkdir -p "$JARS_DIR"

for entry in "${JARS[@]}"; do
  IFS='|' read -r url filename sha256 <<< "$entry"
  dest="${JARS_DIR}/${filename}"

  if [ -f "$dest" ] && [ "$FORCE" -eq 0 ]; then
    if verify "$dest" "$sha256"; then
      success "${filename} already present and verified"
      continue
    fi
    warn "${filename} present but checksum mismatch - re-downloading"
  fi

  info "Downloading ${filename} ..."
  tmp="$(mktemp)"
  if ! curl -fSL --retry 3 --retry-delay 2 "$url" -o "$tmp"; then
    error "Download failed: ${url}"
    rm -f "$tmp"
    exit 1
  fi

  if ! verify "$tmp" "$sha256"; then
    error "Checksum verification failed for ${filename}"
    error "  expected: ${sha256}"
    error "  actual:   $(sha256sum "$tmp" | awk '{print $1}')"
    rm -f "$tmp"
    exit 1
  fi

  mv "$tmp" "$dest"
  chmod 0644 "$dest"
  success "${filename} downloaded and verified"
done

success "All JARs ready in spark/jars/"
