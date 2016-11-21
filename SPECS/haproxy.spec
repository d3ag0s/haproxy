%define base_version 1.6
%define version      %{base_version}.9
%define systemctl    /bin/systemctl

Summary:        HA-Proxy is a TCP/HTTP reverse proxy for high availability environments
Name:           haproxy
Version:        %{version}
Release:        2
License:        GPL
Group:          System Environment/Daemons
URL:            http://haproxy.org/
Source0:        http://haproxy.org/download/%{base_version}/src/%{name}-%{version}.tar.gz
Source1:        haproxy.service.in
BuildRoot:      %{_tmppath}/%{name}-%{version}-root
BuildRequires:  pcre-devel autoconf
Requires:       %{systemctl}

%description
HA-Proxy is a TCP/HTTP reverse proxy which is particularly suited for high
availability environments. Indeed, it can:
- route HTTP requests depending on statically assigned cookies
- spread the load among several servers while assuring server persistence
  through the use of HTTP cookies
- switch to backup servers in the event a main one fails
- accept connections to special ports dedicated to service monitoring
- stop accepting connections without breaking existing ones
- add/modify/delete HTTP headers both ways
- block requests matching a particular pattern

It needs very little resource. Its event-driven architecture allows it to easily
handle thousands of simultaneous connections on hundreds of instances without
risking the system's stability.

%prep
%setup -q

# We don't want any perl dependecies in this RPM:
%define __perl_requires /bin/true

%build
%{__make} USE_PCRE=1 DEBUG="" ARCH=%{_target_cpu} TARGET=linux26 USE_LINUX_TPROXY=1

%install
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}

%{__install} -d %{buildroot}%{_sbindir}
%{__install} -d %{buildroot}%{_mandir}/man1/
%{__install} -d %{buildroot}%{_unitdir}

%{__install} -s %{name} %{buildroot}%{_sbindir}/
%{__install} -s %{name}-systemd-wrapper %{buildroot}%{_sbindir}/
%{__install} -m 755 doc/%{name}.1 %{buildroot}%{_mandir}/man1/
%{__install} -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service

%clean
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}

%post
%{systemctl} daemon-reload >/dev/null 2>&1
%{systemctl} enable %{name}

%preun
%{systemctl} --no-reload disable %{name}
%{systemctl} stop %{name} >/dev/null 2>&1

%postun
%{systemctl} daemon-reload >/dev/null 2>&1

%files
%defattr(-,root,root)
%doc %{_mandir}/man1/%{name}.1*
%attr(0755,root,root) %{_sbindir}/%{name}
%attr(0755,root,root) %{_sbindir}/%{name}-systemd-wrapper
%attr(0644,root,root) %{_unitdir}/%{name}.service

%changelog
* Thu Nov 17 2016 Gabriel Paiu <gabriel.paiu@gmail.com>
- initial build with TPROXY enabled
