#!/bin/bash

# Ensure script is run with root privileges
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root: sudo bash setup_service.sh"
  exit 1
fi

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="/etc/systemd/system/infinitypi.service"

echo "Configuring InfinityPi startup service in: $PROJECT_DIR"

# Write systemd service file
cat <<EOF > $SERVICE_FILE
[Unit]
Description=InfinityPi Disney Infinity Base Emulator
After=network.target local-fs.target

[Service]
Type=simple
WorkingDirectory=$PROJECT_DIR
ExecStartPre=/sbin/modprobe libcomposite
ExecStartPre=/bin/bash $PROJECT_DIR/base_identity.sh
ExecStart=/usr/bin/python3 $PROJECT_DIR/infinity_pi.py
Restart=always
RestartSec=3
User=root

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd daemon, enable, and start service
systemctl daemon-reload
systemctl enable infinitypi.service
systemctl start infinitypi.service

echo "InfinityPi service successfully installed and started!"
echo "Check status anytime with: sudo systemctl status infinitypi.service"