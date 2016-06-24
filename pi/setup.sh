#!/bin/sh
set -e

# Install all required packages
This is a bit risky - apt-get update
apt-get install gpsd gpsd-clients python-gps python-serial

# Update boot settings
mv /boot/cmdline.txt /boot/cmdlinetxt_$(date +"%Y%m%d").bak
echo dwc_otg.lpm_enable=0 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline rootwait > /boot/cmdline.txt

# Disable tty listener in /etc/inittab, bit crude, stop double # comments after
sed -e 's/T0/#T0/;s/##/#/' -i.bak /etc/inittab
# ADD COMMENT HASH TO THIS LINE - T0:23:respawn:/sbin/getty -L ttyAMA0 115200 vt100

# setup GPSD and make it start on reboot
mv /etc/default/gpsd /etc/default/gpsd__$(date +"%Y%m%d").bak
cp -f ./etc/default/gpsd /etc/default/gpsd
update-rc.d /etc/init.d/gpsd defaults

# Make the application run on startup
# Old Wheezy script
# mv /etc/rc.local /etc/rclocal__$(date +"%Y%m%d").bak
# cp -f ./etc/rc.local /etc

# Systemd
cp -f ./lib/systemd/system/pi-nav.service /lib/systemd/system
sudo chmod 644 /lib/systemd/system/pi-nav.service
sudo systemctl daemon-reload
sudo systemctl enable pi-nav.service

echo 'if there were no errors, reboot to finish set up'
