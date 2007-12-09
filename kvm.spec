#
# Conditional build:
%bcond_without  dist_kernel     	# allow non-distribution kernel
%bcond_without  kernel                  # build for unpatched kernel (which doesn't provide kvm.ko already)
%bcond_without  userspace               # don't build userspace utilities

%define	no_install_post_strip	1

%define	_rel	0.1

Summary:	Kernel-based Virtual Machine for Linux
Summary(pl.UTF-8):	Oparta na jądrze maszyna wirtualna dla Linuksa
Name:		kvm
Version:	55
Release:	%{_rel}
License:	GPL
Group:		Applications/System
Source0:	http://dl.sourceforge.net/kvm/%{name}-%{version}.tar.gz
# Source0-md5:	9fdc16aff50fe5ecd7d9b121958cd19b
URL:		http://kvm.sourceforge.net/
BuildRequires:	bash
%if %{with kernel}
BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
%if %{with userspace}
BuildRequires:	SDL-devel
BuildRequires:	alsa-lib-devel
BuildRequires:	libuuid-devel
BuildRequires:	zlib-devel
BuildRequires:	perl-tools-pod
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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

%package -n kernel%{_alt_kernel}-misc-kvm
Summary:	kvm - Linux kernel module
Summary(pl.UTF-8):	kvm - moduł jądra Linuksa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel}
License:	Free to use, non-distributable
Requires(post,postun):	/sbin/depmod
Requires:	module-init-tools >= 3.2.2-2

%description -n kernel%{_alt_kernel}-misc-kvm
kvm - Linux kernel module.

%description -n kernel%{_alt_kernel}-misc-kvm -l pl.UTF-8
kvm - moduł jądra Linuka.

%prep
%setup -q

%build
# not ac stuff
./configure \
	%{!?with_kernel:--with-patched-kernel} \
	--disable-gcc-check \
	--kerneldir=%{_kernelsrcdir} \
	--prefix=%{_libdir}/kvm \
	--kerneldir=$PWD/kernel \
	--disable-gcc-check \
	--qemu-cc="%{__cc}"

%if %{with userspace}
# build bios or use binary one?
#%{__make} bios
%{__make} libkvm
%{__make} user
%{__make} qemu
%endif

%if %{with kernel}
%build_kernel_modules -C kernel -m kvm,kvm-amd,kvm-intel
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
%{__make} -C libkvm install \
	DESTDIR=$RPM_BUILD_ROOT
# KERNELDIR=%{_kernelsrcdir}
%{__make} -C qemu install \
	DESTDIR=$RPM_BUILD_ROOT
%endif

%if %{with kernel}
%install_kernel_modules -m kernel/{kvm-amd,kvm,kvm-intel} -d misc
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post   -n kernel%{_alt_kernel}-misc-kvm
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-misc-kvm
%depmod %{_kernel_ver}

%if %{with userspace}
%files
%defattr(644,root,root,755)
%dir %{_libdir}/kvm
%dir %{_libdir}/kvm/bin
%attr(755,root,root) %{_libdir}/kvm/bin/*
%{_libdir}/kvm/include
%{_libdir}/kvm/%{_lib}
%dir %{_libdir}/kvm/share
%{_libdir}/kvm/share/qemu
%{_mandir}/man1/qemu*.1*
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-misc-kvm
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/kvm*
%endif
