#!/bin/sh
set -eu

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
AUDIT_DATE=${AUDIT_DATE:-2026-08-12}
BASE_IMAGE=${BASE_IMAGE:-debian:bookworm-slim}
CHECKER_COMMIT=2e3b2dc0ecf938addbd779d42877b6ed69d9a985
AUDIT_TMP=$(mktemp -d)
REPORT_NAME="drat_clean_environment_${AUDIT_DATE}.json"
LOG_NAME="drat_clean_environment_${AUDIT_DATE}.log"

cleanup() {
  rm -rf "$AUDIT_TMP"
}
trap cleanup EXIT INT TERM

docker pull "$BASE_IMAGE"
IMAGE_DIGEST=$(docker image inspect "$BASE_IMAGE" --format '{{index .RepoDigests 0}}')

{
  echo "HOST_COMMAND=scripts/run_clean_drat_audit.sh"
  echo "BASE_IMAGE=$BASE_IMAGE"
  echo "BASE_IMAGE_DIGEST=$IMAGE_DIGEST"
  docker run --rm \
    -v "$PROJECT_ROOT:/work:ro" \
    -v "$AUDIT_TMP:/audit" \
    -w /work \
    "$IMAGE_DIGEST" \
    sh -c '
      set -eu
      export DEBIAN_FRONTEND=noninteractive
      apt-get update
      apt-get install -y --no-install-recommends build-essential ca-certificates git python3
      git clone https://github.com/marijnheule/drat-trim.git /tmp/drat-trim
      git -C /tmp/drat-trim checkout --detach "$1"
      make -C /tmp/drat-trim drat-trim
      python3 /work/scripts/recheck_all_drat.py \
        --checker /tmp/drat-trim/drat-trim \
        --checker-source /tmp/drat-trim/drat-trim.c \
        --checker-commit "$1" \
        --environment-label "$2" \
        --report /audit/report.json
    ' audit "$CHECKER_COMMIT" "$IMAGE_DIGEST"
} 2>&1 | tee "$PROJECT_ROOT/artifacts/audit/$LOG_NAME"

cp "$AUDIT_TMP/report.json" "$PROJECT_ROOT/artifacts/audit/$REPORT_NAME"
sha256sum "$PROJECT_ROOT/artifacts/audit/$LOG_NAME" "$PROJECT_ROOT/artifacts/audit/$REPORT_NAME" 2>/dev/null || \
  shasum -a 256 "$PROJECT_ROOT/artifacts/audit/$LOG_NAME" "$PROJECT_ROOT/artifacts/audit/$REPORT_NAME"
