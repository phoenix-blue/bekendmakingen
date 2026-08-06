#!/bin/sh

APP_DIR=/qmf/qml/apps/bekendmakingen
CONFIG=/mnt/data/tsc/bekendmakingen.json
SERVICE_LINK=/qmf/bin/bekendmakingen-service.sh
BINARY_LINK=/qmf/bin/toon2_bekendmakingen
BOOT_LINK=/etc/rc5.d/S98bekendmakingen

install_app() {
    mkdir -p /mnt/data/tsc /var/volatile/log

    if [ -x "$SERVICE_LINK" ]; then
        "$SERVICE_LINK" stop >/dev/null 2>&1
    fi

    if [ ! -s "$CONFIG" ]; then
        cp "$APP_DIR/bekendmakingen.json" "$CONFIG"
    fi
    chmod 600 "$CONFIG"

    chmod 755 "$APP_DIR/toon2_bekendmakingen"
    chmod 755 "$APP_DIR/bekendmakingen-service.sh"
    chmod 755 "$APP_DIR/S98bekendmakingen.sh"
    chmod 755 "$APP_DIR/bekendmakingen.sh"

    ln -sf "$APP_DIR/toon2_bekendmakingen" "$BINARY_LINK"
    ln -sf "$APP_DIR/bekendmakingen-service.sh" "$SERVICE_LINK"
    ln -sf "$APP_DIR/S98bekendmakingen.sh" "$BOOT_LINK"

    "$SERVICE_LINK" start
}

uninstall_app() {
    if [ -x "$SERVICE_LINK" ]; then
        "$SERVICE_LINK" stop >/dev/null 2>&1
    fi
    rm -f "$BINARY_LINK" "$SERVICE_LINK" "$BOOT_LINK"
}

case "$1" in
    uninstall) uninstall_app ;;
    *) install_app ;;
esac
