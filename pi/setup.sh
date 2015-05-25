#!/bin/sh

# Install all required packages
apt-get update
apt-get install git gpsd gpsd-clients python-gps python-serial

# Update boot settings
mv /boot/cmdline.txt /boot/cmdlinetxt_$(date +"%Y%m%d").bak
echo dwc_otg.lpm_enable=0console=tty1root=/dev/mmcblk0p2rootfstype=ext4elevator=deadlinerootwait > /boot/cmdline.txt

# Disable tty listener in /etc/inittab, bit crude, stop double # comments after
sed -e 's/T0/#T0/;s/##/#/' -i.bak /etc/inittab
# ADD COMMENT HASH TO THIS LINE - T0:23:respawn:/sbin/getty -L ttyAMA0 115200 vt100

# setup GPSD and make it start on reboot
mv /etc/default/gpsd /etc/default/gpsd__$(date +"%Y%m%d").bak
cp -f ./etc/default/gpsd /etc/default/gpsd
update-rc.d /etc/init.d/gpsd defaults 

# Make the application run on startup
mv /etc/rc.local /etc/rclocal__$(date +"%Y%m%d").bak
cp -f ./etc/rc.local /etc

sudo reboot