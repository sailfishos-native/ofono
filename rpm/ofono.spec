Name:       ofono
Summary:    Open Source Telephony
Version:    2.10
Release:    1
License:    GPLv2
URL:        https://github.com/sailfishos/ofono
Source:     %{name}-%{version}.tar.bz2

Patch0:     0001-Add-the-Sailfish-Bluetooth-plugin.patch
Patch1:     0002-Add-support-for-debug-notifications.patch
Patch2:     0003-Add-the-sailfish-access-plugin-and-required-infrastr.patch
Patch3:     0004-Add-cell-info-support.patch
Patch4:     0005-Add-sailfish-pushforwarder-plugin.patch
Patch5:     0006-Add-support-for-plugin-iteration-using-foreach.patch
Patch6:     0007-Add-sim-info-support-and-the-sailfish-watch-infrastr.patch
Patch7:     0008-Add-the-sailfish-slot-manager-and-dbus-interface.patch
Patch8:     0009-Initialise-the-slot-manager-on-startup.patch
Patch9:     0010-Add-slot-support-to-the-gobi-plugin.patch
Patch10:    0011-Add-sailfish-arguments-to-the-systemd-unit-and-start.patch
Patch11:    0012-Add-at-interface-to-qmidevice.patch
Patch12:    0013-fix-unit-test-ell-ld.patch
Patch13:    0015-voicecall-wakelock.patch
Patch14:    0016-udevng-wakelock.patch

%define libglibutil_version 1.0.51

# license macro requires rpm >= 4.11
# Recommends requires rpm >= 4.12
BuildRequires: pkgconfig(rpm)
%define license_support %(pkg-config --exists 'rpm >= 4.11'; echo $?)
%define can_recommend %(pkg-config --exists 'rpm >= 4.12'; echo $?)
%if %{can_recommend} == 0
%define recommend Recommends
%else
%define recommend Requires
%endif

Requires:   dbus
Requires:   systemd
Requires:   libglibutil >= %{libglibutil_version}
Requires:   ell
%{recommend}: mobile-broadband-provider-info
%{recommend}: ofono-configs
Requires(preun): systemd
Requires(post): systemd
Requires(postun): systemd

BuildRequires:  pkgconfig
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(dbus-glib-1)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(libudev) >= 145
BuildRequires:  pkgconfig(libwspcodec) >= 2.0
BuildRequires:  pkgconfig(libglibutil) >= %{libglibutil_version}
BuildRequires:  pkgconfig(libdbuslogserver-dbus)
BuildRequires:  pkgconfig(libdbusaccess)
BuildRequires:  pkgconfig(mobile-broadband-provider-info)
BuildRequires:  pkgconfig(systemd)
BuildRequires:  libtool
BuildRequires:  automake
BuildRequires:  autoconf
BuildRequires:  ell-devel >= 0.62.0

%description
Telephony stack

%package devel
Summary:    Headers for oFono
Requires:   %{name} = %{version}-%{release}

%description devel
Development headers and libraries for oFono

%package tests
Summary:    Test Scripts for oFono
Requires:   %{name} = %{version}-%{release}
Requires:   dbus-python3
Requires:   python3-gobject
Provides:   ofono-test >= 1.0
Obsoletes:  ofono-test < 1.0

%description tests
Scripts for testing oFono and its functionality

%package doc
Summary:   Documentation for %{name}
Requires:  %{name} = %{version}-%{release}

%description doc
Man pages for %{name}.

%prep
%autosetup -p1 -n %{name}-%{version}/upstream

./bootstrap

%build
autoreconf --force --install

%configure --disable-static \
    --enable-test \
    --enable-sailfish-slot \
    --enable-sailfish-bt \
    --enable-sailfish-pushforwarder \
    --enable-sailfish-access \
    --disable-rilmodem \
    --disable-isimodem \
    --enable-qmimodem \
    --with-systemdunitdir=%{_unitdir} \
    --enable-external-ell \
    --enable-debug=yes

make %{_smp_mflags}

%check
# run unit tests
make check

%install
export DONT_STRIP=1
rm -rf %{buildroot}
%make_install

mkdir -p %{buildroot}/%{_sysconfdir}/ofono/push_forwarder.d
mkdir -p %{buildroot}%{_unitdir}/network.target.wants
mkdir -p %{buildroot}/var/lib/ofono
ln -s ../ofono.service %{buildroot}%{_unitdir}/network.target.wants/ofono.service

mkdir -p %{buildroot}%{_docdir}/%{name}-%{version}
install -m0644 -t %{buildroot}%{_docdir}/%{name}-%{version} \
        ChangeLog AUTHORS README

%preun
if [ "$1" -eq 0 ]; then
systemctl stop ofono.service ||:
fi

%post
systemctl daemon-reload ||:
# Do not restart during update
# We don't want to break anything during update
# New daemon is taken in use after reboot
# systemctl reload-or-try-restart ofono.service ||:

%postun
systemctl daemon-reload ||:

%transfiletriggerin -- %{_libdir}/ofono/plugins
systemctl try-restart ofono.service ||:

%files
%defattr(-,root,root,-)
%config %{_sysconfdir}/dbus-1/system.d/*.conf
%{_sbindir}/*
%{_unitdir}/network.target.wants/ofono.service
%{_unitdir}/ofono.service
%dir %{_sysconfdir}/ofono/
%dir %{_sysconfdir}/ofono/push_forwarder.d
# This file is part of phonesim and not needed with ofono.
%exclude %{_sysconfdir}/ofono/phonesim.conf
%dir %attr(775,radio,radio) /var/lib/ofono
%if %{license_support} == 0
%license COPYING
%endif
%{_datadir}/ofono/provision.db

%files devel
%defattr(-,root,root,-)
%{_includedir}/ofono/
%{_libdir}/pkgconfig/ofono.pc

%files tests
%defattr(-,root,root,-)
%{_libdir}/%{name}/test/*

%files doc
%defattr(-,root,root,-)
%{_mandir}/man8/%{name}d.*
%{_docdir}/%{name}-%{version}
