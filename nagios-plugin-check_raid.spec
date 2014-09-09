# TODO
# - see and adopt: http://gist.github.com/359890
%define		plugin	check_raid
Summary:	Nagios plugin to check current server's RAID status
Name:		nagios-plugin-%{plugin}
Version:	3.1.0
Release:	1
License:	GPL v2
Group:		Networking
Source0:	https://github.com/glensc/nagios-plugin-check_raid/archive/%{version}/%{plugin}-%{version}.tar.gz
# Source0-md5:	51e1bdabc9642b68a53ac2ca5b9961c4
URL:		https://github.com/glensc/nagios-plugin-check_raid
Requires:	nagios-common
Requires:	perl-base >= 1:5.8.0
Requires:	sudo
Suggests:	CmdTool2
Suggests:	arcconf
Suggests:	areca-cli
Suggests:	cciss_vol_status
Suggests:	hpacucli
Suggests:	megacli-sas
Suggests:	megarc-scsi
Suggests:	mpt-status
Suggests:	smartmontools
Suggests:	tw_cli-9xxx
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/nagios/plugins
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
%setup -q

%build
ver=$(./%{plugin}.pl -V)
test "$(echo "$ver" | awk '{print $NF}')" = %{version}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{plugindir}}
install -p %{plugin}.pl $RPM_BUILD_ROOT%{plugindir}/%{plugin}
cp -p %{plugin}.cfg $RPM_BUILD_ROOT%{_sysconfdir}/%{plugin}.cfg

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ "$1" = 1 ]; then
	# setup sudo rules on first install
	%{plugindir}/%{plugin} -S || :
fi

%postun
if [ "$1" = 0 ]; then
	# remove all sudo rules related to us
	%{__sed} -i -e '/CHECK_RAID/d' /etc/sudoers
fi

%triggerin -- nagios-nrpe
%nagios_nrpe -a %{plugin} -f %{_sysconfdir}/%{plugin}.cfg

%triggerun -- nagios-nrpe
%nagios_nrpe -d %{plugin} -f %{_sysconfdir}/%{plugin}.cfg

%files
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{plugin}.cfg
%attr(755,root,root) %{plugindir}/%{plugin}
