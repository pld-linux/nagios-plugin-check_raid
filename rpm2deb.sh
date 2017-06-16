#!/bin/sh
set -xe

V=${1-4.0.6}
R=${2:-1}

./builder -bb *.spec
fakeroot alien --scripts -d -k ../RPMS/nagios-plugin-check_raid-$V-$R.noarch.rpm --generate
cd nagios-plugin-check_raid-$V
mv ./usr/share/perl5/vendor_perl/App ./usr/share/perl5/App
fakeroot debian/rules binary
cd ..
rm -rf nagios-plugin-check_raid-$V
