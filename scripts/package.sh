#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
VERSION=$(tr -d '[:space:]' <"$PROJECT_DIR/version.txt")
DIST_DIR="$PROJECT_DIR/dist"
STAGING_DIR=$(mktemp -d "${TMPDIR:-/tmp}/bekendmakingen-package.XXXXXX")
trap 'rm -rf "$STAGING_DIR"' EXIT HUP INT TERM

"$PROJECT_DIR/scripts/check-release.sh" "$VERSION"

APP_DIR="$STAGING_DIR/bekendmakingen"
mkdir -p "$APP_DIR/description" "$APP_DIR/drawables" "$APP_DIR/docs" "$DIST_DIR"

cp \
    "$PROJECT_DIR/BekendmakingenApp.qml" \
    "$PROJECT_DIR/BekendmakingenTile.qml" \
    "$PROJECT_DIR/BekendmakingenScreen.qml" \
    "$PROJECT_DIR/BekendmakingenDetail.qml" \
    "$PROJECT_DIR/BekendmakingenSettings.qml" \
    "$PROJECT_DIR/BekendmakingenPopup.qml" \
    "$PROJECT_DIR/qmldir" \
    "$PROJECT_DIR/toonstore.cfg" \
    "$PROJECT_DIR/ToonRepo-entry.xml" \
    "$PROJECT_DIR/bekendmakingen.json" \
    "$PROJECT_DIR/version.txt" \
    "$PROJECT_DIR/bekendmakingen.sh" \
    "$PROJECT_DIR/bekendmakingen-service.sh" \
    "$PROJECT_DIR/S98bekendmakingen.sh" \
    "$PROJECT_DIR/toon2_bekendmakingen" \
    "$PROJECT_DIR/README.md" \
    "$PROJECT_DIR/LICENSE" \
    "$PROJECT_DIR/PRIVACY.md" \
    "$PROJECT_DIR/SECURITY.md" \
    "$PROJECT_DIR/Changelog.txt" \
    "$PROJECT_DIR/THIRD_PARTY_NOTICES.md" \
    "$APP_DIR/"

cp "$PROJECT_DIR/description/description.txt" "$APP_DIR/description/"
cp "$PROJECT_DIR/drawables/BekendmakingenIcon.svg" \
    "$PROJECT_DIR/drawables/InstitutionIcon.svg" \
    "$PROJECT_DIR/drawables/LocationIcon.svg" \
    "$APP_DIR/drawables/"
cp "$PROJECT_DIR/docs/ARCHITECTURE.md" "$PROJECT_DIR/docs/INSTALLATIE.md" "$APP_DIR/docs/"

chmod 755 "$APP_DIR/toon2_bekendmakingen" "$APP_DIR/bekendmakingen.sh" \
    "$APP_DIR/bekendmakingen-service.sh" "$APP_DIR/S98bekendmakingen.sh"

ARCHIVE="$DIST_DIR/bekendmakingen-$VERSION.tar.gz"
COPYFILE_DISABLE=1 tar -C "$STAGING_DIR" -czf "$ARCHIVE" bekendmakingen

echo "$ARCHIVE"
sha256sum "$ARCHIVE" 2>/dev/null || shasum -a 256 "$ARCHIVE"
