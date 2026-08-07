#!/bin/bash
# MUST BE RUN AS SUDO - RPCS3 DEVICE REPLICATION
GADGET_DIR="/sys/kernel/config/usb_gadget/dire_pi"

if [ -d "$GADGET_DIR" ]; then
    echo "" > "$GADGET_DIR/UDC"
    sleep 1
    find "$GADGET_DIR/configs/c.1" -maxdepth 1 -type l -delete
    rmdir "$GADGET_DIR/configs/c.1/strings/0x409"
    rmdir "$GADGET_DIR/configs/c.1"
    rmdir "$GADGET_DIR/functions/hid.usb0"
    rmdir "$GADGET_DIR/strings/0x409"
    rmdir "$GADGET_DIR"
fi

mkdir -p "$GADGET_DIR"
cd "$GADGET_DIR"
echo 0x0200 > bcdUSB
echo 0x00 > bDeviceClass
echo 0x00 > bDeviceSubClass
echo 0x00 > bDeviceProtocol
echo 0x40 > bMaxPacketSize0
echo 0x0e6f > idVendor
echo 0x0129 > idProduct
echo 0x0200 > bcdDevice 

mkdir -p strings/0x409
echo "000000000001" > strings/0x409/serialnumber
echo "Disney" > strings/0x409/manufacturer
echo "Disney Infinity Base" > strings/0x409/product

mkdir -p configs/c.1/strings/0x409
echo "Config 1" > configs/c.1/strings/0x409/configuration
echo 0x80 > configs/c.1/bmAttributes
echo 500 > configs/c.1/MaxPower

mkdir -p functions/hid.usb0
echo 0 > functions/hid.usb0/protocol
echo 0 > functions/hid.usb0/subclass
echo 32 > functions/hid.usb0/report_length
printf "\x06\x00\xff\x09\x01\xa1\x01\x19\x01\x29\x20\x15\x00\x26\xff\x00\x75\x08\x95\x20\x81\x00\x19\x01\x29\x20\x91\x00\xc0" > functions/hid.usb0/report_desc

ln -s functions/hid.usb0 configs/c.1/
ls /sys/class/udc > UDC