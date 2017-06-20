#!/bin/sh
set -xe

V=${1-4.0.6}
R=${2:-2}
N=nagios-plugin-check_raid
PV=$N-$V
D="libmonitoring-plugin-perl, libmodule-pluggable-perl"

clean() {
	rm -rf nagios-plugin-check_raid-$V
}

rpm() {
	./builder -bb *.spec
}

unpack() {
	clean
	fakeroot alien --scripts -d -k ../RPMS/nagios-plugin-check_raid-$V-$R.noarch.rpm --generate
	cd nagios-plugin-check_raid-$V
	mv ./usr/share/perl5/vendor_perl/App ./usr/share/perl5/App
	rmdir ./usr/share/perl5/vendor_perl
	cd -
}

deb() {
	cd $PV
	sed -i -e "/Depends: / s/$/, $D/" debian/control
	fakeroot debian/rules binary
	cd -
}

rpm
unpack
deb
clean
