#!/bin/sh
set -eu


GRAPHDB_URL="${GRAPHDB_URL:-http://graphdb:7200}"
REPO_ID="${GRAPHDB_REPO_ID:-archimate_phase1}"
IMPORT_FILE="${IMPORT_FILE:-/init/archimate.ttl}"

ASK_BASE_QUERY='
PREFIX archimate: <https://purl.org/archimate#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
ASK {
  archimate:ApplicationComponent a owl:Class .
}
'

echo "Waiting for GraphDB at $GRAPHDB_URL ..."
until curl -fsS "$GRAPHDB_URL/rest/repositories" >/dev/null; do
  sleep 2
done

echo "GraphDB is reachable."

if curl -fsS "$GRAPHDB_URL/rest/repositories" -H "Accept: application/json" | grep -q "\"id\":\"$REPO_ID\""; then
  echo "Repository '$REPO_ID' already exists."
else
  echo "Creating repository '$REPO_ID' ..."
  curl -fsS -X POST \
    "$GRAPHDB_URL/rest/repositories" \
    -H "Content-Type: multipart/form-data" \
    -F "config=@/init/repo-config.ttl"
fi

if [ -f "$IMPORT_FILE" ]; then
  echo "Checking whether Mendoza base is already present in repository '$REPO_ID' ..."

  ASK_RESPONSE="$(curl -fsS -X POST \
    "$GRAPHDB_URL/repositories/$REPO_ID" \
    -H "Accept: application/sparql-results+json" \
    --data-urlencode "query=$ASK_BASE_QUERY")"

  if echo "$ASK_RESPONSE" | grep -q '"boolean"[[:space:]]*:[[:space:]]*true'; then
    echo "Mendoza base already present. Skipping initial import."
  else
    echo "Uploading initial base file: $IMPORT_FILE"
    curl -fsS -X POST \
      "$GRAPHDB_URL/repositories/$REPO_ID/statements" \
      -H "Content-Type: text/turtle; charset=utf-8" \
      --data-binary @"$IMPORT_FILE"
  fi
else
  echo "No initial import file found at $IMPORT_FILE. Skipping import."
fi

echo "GraphDB init complete."