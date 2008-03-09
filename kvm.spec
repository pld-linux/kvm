# TODO:
# - udev is optional, so separate udev stuff from kernel module
# - doesn't build on ppc, fix this if possible
#
# Conditional build:
%bcond_without  dist_kernel     	# allow non-distribution kernel
%bcond_without  kernel                  # build for unpatched kernel (which doesn't provide kvm.ko already)
%bcond_without  userspace               # don't build userspace utilities

%define		rel	1
Summary:	Kernel-based Virtual Machine for Linux
Summary(pl.UTF-8):	Oparta na jądrze maszyna wirtualna dla Linuksa
Name:		kvm
Version:	63
Release:	%{rel}
License:	GPL v2
Group:		Applications/System
Source0:	http://dl.sourceforge.net/kvm/%{name}-%{version}.tar.gz
# Source0-md5:	5df4eebff934f811821d2a2c40e38753
URL:		http://kvm.sourceforge.net/
BuildRequires:	bash
%if %{with kernel}
BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
%if %{with userspace}
BuildRequires:	SDL-devel
BuildRequires:	alsa-lib-devel
BuildRequires:	zlib-devel
Requires:	qemu
%endif
# ppc broken?
ExclusiveArch:	%{ix86} %{x8664} ia64
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
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel}
License:	GPL v2
Requires(post,postun):	/sbin/depmod
Requires(postun):	/usr/sbin/groupdel
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires:	module-init-tools >= 3.2.2-2

%description -n kernel%{_alt_kernel}-misc-kvm
kvm - Linux kernel module.

%description -n kernel%{_alt_kernel}-misc-kvm -l pl.UTF-8
kvm - moduł jądra Linuksa.

%prep
%setup -q

%build
# not ac stuff
./configure \
	%{!?with_kernel:--with-patched-kernel} \
	--disable-gcc-check \
	--kerneldir=%{_kernelsrcdir} \
	--prefix=%{_prefix} \
	--kerneldir=$PWD/kernel \
	--disable-gcc-check \
	--enable-alsa \
	--qemu-cc="%{__cc}"

%if %{with userspace}
%{__make} qemu
%endif

%if %{with kernel}
%build_kernel_modules -C kernel -m kvm,kvm-amd,kvm-intel
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
%{__make} -C qemu install \
	DESTDIR=$RPM_BUILD_ROOT

# removing files which are provided by required qemu package
rm -rf $RPM_BUILD_ROOT%{_datadir}/qemu $RPM_BUILD_ROOT%{_mandir} $RPM_BUILD_ROOT%{_docdir}
rm -f $RPM_BUILD_ROOT%{_bindir}/qemu-img

# changing binary name to avoid conflict with qemu
mv -f $RPM_BUILD_ROOT%{_bindir}/qemu-system-x86_64 $RPM_BUILD_ROOT%{_bindir}/%{name}
install kvm_stat $RPM_BUILD_ROOT%{_bindir}
%endif

%if %{with kernel}
install -D scripts/65-kvm.rules $RPM_BUILD_ROOT/etc/udev/rules.d/kvm.rules
%install_kernel_modules -m kernel/{kvm-amd,kvm,kvm-intel} -d misc
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%pre    -n kernel%{_alt_kernel}-misc-kvm
%groupadd -g 160 kvm

%post   -n kernel%{_alt_kernel}-misc-kvm
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-misc-kvm
%depmod %{_kernel_ver}
if [ "$1" = "0" ]; then
	%groupremove kvm
fi

%if %{with userspace}
%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{name}*
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-misc-kvm
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) /etc/udev/rules.d/kvm.rules
/lib/modules/%{_kernel_ver}/misc/kvm*
%endif
