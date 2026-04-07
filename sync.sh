#!/bin/bash

HOST="ftp.grandwarninglights.in"
USER="ljcsvbmk"
PASS="Grandwarning@1234@"
REMOTE="/public_html"
LOCAL="$(dirname "$0")"

# Files/dirs to exclude
EXCLUDES=(".git" ".vscode" ".claude" "sync.sh" "node_modules" ".DS_Store" "CLAUDE.md" ".catalogue-pages" ".catalogue-preview" ".swift-cache")

echo "Syncing to $HOST$REMOTE..."

find "$LOCAL" -type f | while read -r file; do
    # Get relative path
    rel="${file#$LOCAL/}"

    # Skip excluded paths
    skip=false
    for ex in "${EXCLUDES[@]}"; do
        if [[ "$rel" == "$ex"* ]]; then
            skip=true
            break
        fi
    done
    [[ "$(basename "$rel")" == ".DS_Store" ]] && skip=true
    $skip && continue

    remote_path="ftp://$HOST$REMOTE/$rel"
    echo "Uploading: $rel"
    curl -s --ftp-pasv -u "$USER:$PASS" -T "$file" "$remote_path" --ftp-create-dirs
done

echo "Done."
