%define		mod_name	mod_gss
Summary:	mod_gss module for proftpd
Summary(pl.UTF-8):	Moduł mod_gss dla proftpd
Name:		proftpd-%{mod_name}
Version:	1.3.3
Release:	0.1
License:	GPL v2+
Group:		Daemons
Source0:	http://dl.sourceforge.net/gssmod/%{mod_name}-%{version}.tar.gz
# Source0-md5:	dc44e44193f943387763bd7fb363a0e9
Source1:	%{mod_name}.conf
Patch0:		%{name}-heimdal.patch
URL:		http://gssmod.sourceforge.net/
BuildRequires:	heimdal-devel
BuildRequires:	proftpd-devel >= 1:1.3.1
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,postun):	grep
Requires:	proftpd >= 1:1.3.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir		/etc/ftpd
%define		_libexecdir		%{_prefix}/%{_lib}/proftpd

%description
This module provides support for the GSSAPI security mechanism,
as described in RFC2228.

%prep
%setup -q -n %{mod_name}-%{version}
%patch0 -p1

%build
%configure \
	--enable-heimdal

%{__cc} %{rpmcflags} -fPIC -I/usr/include/proftpd \
	-shared -lgssapi -lkrb5 -lcom_err -lasn1 -lroken \
	%{rpmldflags} \
	mod_auth_gss.c -o mod_auth_gss.so

%{__cc} %{rpmcflags} -fPIC -I/usr/include/proftpd \
	-shared -lgssapi -lkrb5 -lcom_err -lasn1 -lroken \
	%{rpmldflags} \
	mod_gss.c -o mod_gss.so

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libexecdir},%{_sysconfdir}/conf.d}

install mod_auth_gss.so $RPM_BUILD_ROOT%{_libexecdir}
install mod_gss.so $RPM_BUILD_ROOT%{_libexecdir}
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/conf.d/%{mod_name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
if grep -iEqs "^ServerType[[:space:]]+inetd" %{_sysconfdir}/proftpd.conf; then
	%service -q rc-inetd reload
elif grep -iEqs "^ServerType[[:space:]]+standalone" %{_sysconfdir}/proftpd.conf; then
	%service -q proftpd restart
fi

%postun
if [ "$1" = "0" ]; then
	if grep -iEqs "^ServerType[[:space:]]+inetd" %{_sysconfdir}/proftpd.conf; then
		%service -q rc-inetd reload
	elif grep -iEqs "^ServerType[[:space:]]+standalone" %{_sysconfdir}/proftpd.conf; then
		%service -q proftpd restart
	fi
fi

%files
%defattr(644,root,root,755)
%doc README.* mod_gss.html rfc*.txt
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/conf.d/%{mod_name}.conf
%attr(755,root,root) %{_libexecdir}/mod_*gss.so
