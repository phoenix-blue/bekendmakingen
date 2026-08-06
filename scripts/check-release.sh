#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
cd "$PROJECT_DIR"

VERSION=$(tr -d '[:space:]' <version.txt)
EXPECTED=${1:-$VERSION}

fail() {
    echo "releasecontrole mislukt: $*" >&2
    exit 1
}

[ "$VERSION" = "$EXPECTED" ] || fail "version.txt bevat $VERSION, verwacht $EXPECTED"
grep -q "^version=$EXPECTED$" toonstore.cfg || fail "toonstore.cfg-versie wijkt af"
grep -q "<version>$EXPECTED</version>" ToonRepo-entry.xml || fail "ToonRepo-entry.xml-versie wijkt af"
grep -q "version[[:space:]]*= \"$EXPECTED\"" daemon/main.go || fail "daemonversie wijkt af"
grep -q "<toon2only>yes</toon2only>" ToonRepo-entry.xml || fail "app is niet als Toon 2-only gemarkeerd"

for path in \
    BekendmakingenApp.qml BekendmakingenTile.qml BekendmakingenScreen.qml \
    BekendmakingenDetail.qml BekendmakingenSettings.qml BekendmakingenPopup.qml \
    qmldir toonstore.cfg ToonRepo-entry.xml bekendmakingen.json version.txt \
    bekendmakingen.sh bekendmakingen-service.sh S98bekendmakingen.sh toon2_bekendmakingen \
    description/description.txt drawables/BekendmakingenIcon.svg \
    drawables/InstitutionIcon.svg drawables/LocationIcon.svg \
    README.md LICENSE PRIVACY.md SECURITY.md Changelog.txt THIRD_PARTY_NOTICES.md \
    docs/ARCHITECTURE.md docs/INSTALLATIE.md \
    store/bekendmakingen_screenshot_1.png store/bekendmakingen_screenshot_2.png \
    store/bekendmakingen_screenshot_3.png
do
    [ -s "$path" ] || fail "vereist bestand ontbreekt of is leeg: $path"
done

grep -q "<screenshots>3</screenshots>" ToonRepo-entry.xml || \
    fail "ToonRepo-entry.xml verwacht drie Store-afbeeldingen"

for image in store/bekendmakingen_screenshot_1.png \
             store/bekendmakingen_screenshot_2.png \
             store/bekendmakingen_screenshot_3.png
do
    IMAGE_INFO=$(file "$image")
    case "$IMAGE_INFO" in
        *"PNG image data"*"800 x 480"*) ;;
        *) fail "$image moet een PNG van 800x480 zijn: $IMAGE_INFO" ;;
    esac
done

[ -x toon2_bekendmakingen ] || fail "daemonbinary is niet uitvoerbaar"
[ -x bekendmakingen.sh ] || fail "installatiescript is niet uitvoerbaar"

FILE_INFO=$(file toon2_bekendmakingen)
case "$FILE_INFO" in
    *"ELF 32-bit"*"ARM"*"statically linked"*) ;;
    *) fail "binary is geen statische 32-bit ARM-binary: $FILE_INFO" ;;
esac

echo "release $EXPECTED is intern consistent"
