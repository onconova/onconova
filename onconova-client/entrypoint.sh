#!/bin/sh
set -e

ENVIRONMENT_FILES=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --files)
      shift
      if [ -z "$1" ]; then
        echo "Error: --files requires a file path"
        exit 1
      fi
      ENVIRONMENT_FILES="$ENVIRONMENT_FILES $1"
      shift
      ;;
    *)
      break
      ;;
  esac
done

for ENVIRONMENT_FILE in $ENVIRONMENT_FILES; do
  if [ ! -f "$ENVIRONMENT_FILE" ]; then
    echo "Warning: Template file '$ENVIRONMENT_FILE' not found! Skipping."
    continue
  fi

  TEMP_FILE="${ENVIRONMENT_FILE}.tmp"
  echo "Substituting env vars in '$ENVIRONMENT_FILE' -> '$TEMP_FILE'"
  envsubst < "$ENVIRONMENT_FILE" > "$TEMP_FILE" && mv "$TEMP_FILE" "$ENVIRONMENT_FILE"
done

echo "Executing command: $*"
exec "$@"