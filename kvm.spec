# TODO:
# - doesn't build on ppc, fix this if possible
# - fix building with ALSA (not OSS)
#
%define		_enable_debug_packages	0
#
%define		rel	0.1
%define		pname	kvm
Summary:	KVM userspace tools
Summary(pl.UTF-8):	Narzędzia przestrzeni użytkownika dla KVM
Name:		%{pname}%{_alt_kernel}
Version:	72
Release:	%{rel}
License:	GPL v2
Group:		Applications/System
Source0:	http://dl.sourceforge.net/kvm/%{pname}-%{version}.tar.gz
# Source0-md5:	e4f99d05dee168200695850165cd760e
URL:		http://kvm.sourceforge.net/
BuildRequires:	bash
BuildRequires:	SDL-devel
BuildRequires:	alsa-lib-devel
BuildRequires:	zlib-devel
Conflicts:	qemu
# ppc broken?
ExclusiveArch:	%{ix86} %{x8664} ia64
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# some SPARC boot image in ELF format
%define         _noautostrip    .*%{_datadir}/qemu/openbios-sparc.*

%description
KVM (for Kernel-based Virtual Machine) is a full virtualization
solution for Linux on x86 hardware. It consists of a loadable kernel
module (kvm.ko) and a userspace component.

Using KVM, one can run multiple virtual machines running unmodified
Linux or Windows images. Each virtual machine has private virtualized
hardware: a network card, disk, graphics adapter, etc.

%description -l pl.UTF-8
KVM (Kernel-based Virtual Machine) to pełne rozwiązanie wirtualizacji
dla Linuksa na sprzęcie x86. Zawiera ładowalny moduł jądra (kvm.ko)
oraz komponent działający w przestrzeni użytkownika.

Przy użyciu KVM można uruchomić wiele maszyn wirtualnych z
działającymi niezmodyfikowanymi obrazami Linuksa i Windows. Kazda z
maszyn wirtualnych ma prywatny wirtualizowany sprzęt: kartę sieciową,
dysk, kartę graficzną itp.

%package udev
Summary:	kvm udev scripts
Summary(pl.UTF-8):	Skrypty udev dla kvm
Group:		Application/System

%description udev
kvm udev scripts.

%description udev -l pl.UTF-8
Skrypty udev dla kvm.

%prep
%setup -q -n %{pname}-%{version}

%build
# not ac stuff
./configure \
	--disable-gcc-check \
	--kerneldir=%{_kernelsrcdir} \
	--prefix=%{_prefix} \
	--kerneldir=$PWD/kernel \
	--qemu-cflags="%{rpmcflags}"

%{__make} qemu

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C qemu install \
	DESTDIR=$RPM_BUILD_ROOT

# removing files which are provided by required qemu package
#rm -rf $RPM_BUILD_ROOT%{_datadir}/qemu $RPM_BUILD_ROOT%{_mandir} $RPM_BUILD_ROOT%{_docdir}
#rm -f $RPM_BUILD_ROOT%{_bindir}/qemu-img

# changing binary name to avoid conflict with qemu
mv -f $RPM_BUILD_ROOT%{_bindir}/qemu-system-x86_64 $RPM_BUILD_ROOT%{_bindir}/%{pname}
install kvm_stat $RPM_BUILD_ROOT%{_bindir}

install -D scripts/65-kvm.rules $RPM_BUILD_ROOT/etc/udev/rules.d/kvm.rules

%pre
%groupadd -g 160 kvm

%postun
%groupremove kvm

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/*
%{_datadir}/qemu
%{_mandir}/man1/qemu.1*
%{_mandir}/man1/qemu-img.1*

%files udev
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) /etc/udev/rules.d/kvm.rules
