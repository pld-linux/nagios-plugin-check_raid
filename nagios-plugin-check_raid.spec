# TODO
# - see and adopt: http://gist.github.com/359890
%define		plugin	check_raid
%include	/usr/lib/rpm/macros.perl
Summary:	Nagios plugin to check current server's RAID status
Name:		nagios-plugin-%{plugin}
Version:	4.0.1
Release:	1
License:	GPL v2
Group:		Applications
Source0:	https://github.com/glensc/nagios-plugin-check_raid/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	f8ef0af7bbc15e8dcb65301648fc967f
URL:		https://github.com/glensc/nagios-plugin-check_raid
BuildRequires:	perl-ExtUtils-MakeMaker-CPANfile
BuildRequires:	perl-Module-Pluggable >= 5.1
BuildRequires:	perl-Monitoring-Plugin >= 0.37
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	rpmbuild(macros) >= 1.685
Requires:	grep
Requires:	nagios-common
Requires:	perl-base >= 1:5.8.0
Requires:	sed >= 4.0
Requires:	sudo >= 1:1.8.7-2
Suggests:	CmdTool2
Suggests:	arcconf
Suggests:	areca-cli
Suggests:	cciss_vol_status
Suggests:	hpacucli
Suggests:	lsscsi
Suggests:	megacli-sas
Suggests:	megarc-scsi
Suggests:	mpt-status
Suggests:	mvcli
Suggests:	smartmontools
Suggests:	tw_cli-9xxx
# cciss_vol_status 1.10 can process /dev/sdX instead of only /dev/sgX
Conflicts:	cciss_vol_status < 1.10
Conflicts:	nagios-nrpe < 2.15-5
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/nagios/plugins
%define		nrpeddir	/etc/nagios/nrpe.d
%define		plugindir	%{_prefix}/lib/nagios/plugins

%description
This plugin chekcs Check all RAID volumes (hardware and software) that
can be identified.

Supports:
- AIX software RAID via lsvg
- Adaptec AAC RAID via aaccli or afacli or arcconf
- Areca SATA RAID Support
- HP Smart Array (MSA1500) via serial line
- HP Smart Array Controllers and MSA Controllers via hpacucli (see
  hapacucli readme)
- HP/Compaq Smart Array via cciss_vol_status (hpsa supported too)
- LSI Logic MegaRAID SAS series via MegaCli
- LSI MegaRaid via lsraid
- Linux 3ware SATA RAID via tw_cli
- Linux DPT/I2O hardware RAID controllers via /proc/scsi/dpt_i2o
- Linux GDTH hardware RAID controllers via /proc/scsi/gdth
- Linux LSI MegaRaid hardware RAID via /proc/megaraid
- Linux LSI MegaRaid hardware RAID via CmdTool2
- Linux LSI MegaRaid hardware RAID via megarc
- Linux MPT hardware RAID via mpt-status
- Linux MegaIDE hardware RAID controllers via /proc/megaide
- Linux software RAID (md) via /proc/mdstat
- SAS2IRCU support
- Serveraid IPS via ipssend
- Solaris software RAID via metastat

%prep
%setup -qc
mv nagios-plugin-check_raid-*/* .

%build
# version check exits with "3", here's explanation:
# https://github.com/monitoring-plugins/monitoring-plugins/pull/1363
ver=$(./%{plugin}.sh -V || :)
test "$(echo "$ver" | awk '{print $NF}')" = %{version}

%{__perl} Makefile.PL \
	INSTALLVENDORSCRIPT=%{plugindir} \
	INSTALLDIRS=vendor
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{nrpeddir},%{plugindir},/etc/sudoers.d}
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

cp -p %{plugin}.cfg $RPM_BUILD_ROOT%{_sysconfdir}
touch $RPM_BUILD_ROOT%{nrpeddir}/%{plugin}.cfg
touch $RPM_BUILD_ROOT/etc/sudoers.d/check_raid

# remove .pl extension
mv $RPM_BUILD_ROOT%{plugindir}/%{plugin}{.pl,}

# cleanup
%{__rm} $RPM_BUILD_ROOT%{perl_archlib}/perllocal.pod
%{__rm} $RPM_BUILD_ROOT%{perl_vendorarch}/auto/App/Monitoring/Plugin/CheckRaid/.packlist

%clean
rm -rf $RPM_BUILD_ROOT

%post
# setup sudo rules:
# - on first install
# - if separate config file is used
grep -q '^#includedir /etc/sudoers\.d' /etc/sudoers && confd=1

if [ "$1" = 1 -o "$confd" = 1 ]; then
	%{plugindir}/%{plugin} -S || :
fi

%postun
if [ "$1" = 0 ]; then
	# remove all sudo rules related to us
	%{__sed} -i -e '/CHECK_RAID/d' /etc/sudoers
fi

%triggerpostun -- %{name} < 3.1.1-0.2, sudo < 1:1.8.7-2
if grep -q '^#includedir /etc/sudoers\.d' /etc/sudoers; then
	%{plugindir}/%{plugin} -S || :
fi
# remove CHECK_RAID rules from /etc/sudoers if separate config is in place
if [ -e /etc/sudoers.d/check_raid ]; then
	%{__sed} -i -e '/CHECK_RAID/d' /etc/sudoers
fi

%triggerin -- nagios-nrpe
%nagios_nrpe -a %{plugin} -f %{_sysconfdir}/%{plugin}.cfg

%triggerun -- nagios-nrpe
%nagios_nrpe -d %{plugin} -f %{_sysconfdir}/%{plugin}.cfg

%files
%defattr(644,root,root,755)
%attr(640,root,nagios) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{plugin}.cfg
%attr(755,root,root) %{plugindir}/%{plugin}
%ghost %{nrpeddir}/%{plugin}.cfg
%ghost /etc/sudoers.d/check_raid
%dir %{perl_vendorlib}/App/Monitoring
%dir %{perl_vendorlib}/App/Monitoring/Plugin
%{perl_vendorlib}/App/Monitoring/Plugin/CheckRaid.pm
%{perl_vendorlib}/App/Monitoring/Plugin/CheckRaid
