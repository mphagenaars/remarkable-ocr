#!/bin/bash

# Remarkable OCR - systemd deployment helper
# Usage:
#   ./deploy-systemd.sh            # install + enable + start (default)
#   ./deploy-systemd.sh install    # install + enable + start
#   ./deploy-systemd.sh uninstall  # stop + disable + remove unit
#   ./deploy-systemd.sh start|stop|restart|status|logs

set -euo pipefail

SERVICE_NAME="remarkable-ocr"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UNIT_PATH="/etc/systemd/system/${SERVICE_NAME}.service"

if [[ "${EUID}" -ne 0 ]]; then
    exec sudo "$0" "$@"
fi

SERVICE_USER="${SUDO_USER:-${USER}}"
SERVICE_GROUP="$(id -gn "${SERVICE_USER}")"

resolve_python() {
    if [[ -x "${SCRIPT_DIR}/.venv/bin/python" ]]; then
        echo "${SCRIPT_DIR}/.venv/bin/python"
        return
    fi
    if command -v python3 &> /dev/null; then
        command -v python3
        return
    fi
    echo "❌ Geen python3 gevonden in PATH en geen .venv aanwezig." >&2
    exit 1
}

ensure_data_dir() {
    mkdir -p "${SCRIPT_DIR}/data"
    chown "${SERVICE_USER}:${SERVICE_GROUP}" "${SCRIPT_DIR}/data"
}

write_unit() {
    local python_bin
    python_bin="$(resolve_python)"
    cat > "${UNIT_PATH}" <<EOF
[Unit]
Description=Remarkable OCR
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_GROUP}
WorkingDirectory=${SCRIPT_DIR}
Environment=PYTHONUNBUFFERED=1
EnvironmentFile=-${SCRIPT_DIR}/.env
ExecStart=${python_bin} ${SCRIPT_DIR}/app.py
Restart=on-failure
RestartSec=5
TimeoutStopSec=20

[Install]
WantedBy=multi-user.target
EOF
}

install_service() {
    ensure_data_dir
    write_unit
    systemctl daemon-reload
    systemctl enable --now "${SERVICE_NAME}.service"
    systemctl status "${SERVICE_NAME}.service" --no-pager
}

uninstall_service() {
    systemctl disable --now "${SERVICE_NAME}.service" || true
    rm -f "${UNIT_PATH}"
    systemctl daemon-reload
}

case "${1:-install}" in
    install)
        install_service
        ;;
    uninstall)
        uninstall_service
        ;;
    start)
        systemctl start "${SERVICE_NAME}.service"
        ;;
    stop)
        systemctl stop "${SERVICE_NAME}.service"
        ;;
    restart)
        systemctl restart "${SERVICE_NAME}.service"
        ;;
    status)
        systemctl status "${SERVICE_NAME}.service" --no-pager
        ;;
    logs)
        journalctl -u "${SERVICE_NAME}.service" -f
        ;;
    *)
        echo "Usage: $0 {install|uninstall|start|stop|restart|status|logs}"
        exit 1
        ;;
esac
