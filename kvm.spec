# TODO:
# - consider moving kvm groupadd/remove from -udev and kernel package to main package (why?)
# - kernel part - doesn't build now, but should we care in the HEAD?
#   btw. with kernel bcond we require >= 3:2.6.28 kernels which
#   could have the kvm stuff on its own
# NOTE:
# - as of 86 the source structure have changed comparing to 75 or 81
#   it looks like kvm is going to be merged with qemu, so in this
#   release the kvm is a subdirectory of the main qemu stuff
# - for 2.6.28.10+ kernels one could build the recent qemu (0.10.5)
#   with a KVM support - the presence of the support depends on the
#   contents of the <linux/kvm.h> header files checked by configure
#   at buildtime.
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_with	kernel		# build for unpatched kernel (which doesn't provide kvm.ko already)
%bcond_without	userspace	# don't build userspace utilities
%bcond_with	verbose		# verbose kernel module build
%bcond_with	internal_qemu	# use internal qemu
%bcond_with	alt_kernel_userspace # allow building userspace with alt_kernel set
#
%if %{without kernel}
%undefine	with_dist_kernel
%endif
%if %{without alt_kernel_userspace}
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif
%endif
%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		rel	3
%define		pname	kvm
Summary:	Kernel-based Virtual Machine for Linux
Summary(pl.UTF-8):	Oparta na jądrze maszyna wirtualna dla Linuksa
Name:		%{pname}%{_alt_kernel}
# http://www.linux-kvm.org/page/Choose_the_right_kvm_%26_kernel_version
Version:	88
Release:	%{rel}
License:	GPL v2
Group:		Applications/System
Source0:	http://dl.sourceforge.net/kvm/%{pname}-%{version}.tar.gz
# Source0-md5:	02371948fcee1fa2a77e7a457384d71c
Patch0:		%{pname}-fixes.patch
Patch1:		%{pname}-kernel-release.patch
Patch2:		%{pname}-ncurses.patch
URL:		http://www.linux-kvm.org/
BuildRequires:	bash
BuildRequires:	kernel%{_alt_kernel}-headers >= 3:2.6.28
BuildRequires:	sed >= 4.0
%if %{with kernel}
BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.28
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
%if %{with userspace}
BuildRequires:	SDL-devel
BuildRequires:	alsa-lib-devel
BuildRequires:	bluez-libs-devel
BuildRequires:	curl-devel
BuildRequires:	ncurses-devel
BuildRequires:	pciutils-devel
BuildRequires:	perl-Encode
BuildRequires:	perl-tools-pod
BuildRequires:	pkgconfig
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.202
BuildRequires:	tetex
BuildRequires:	texi2html
BuildRequires:	which
BuildRequires:	zlib-devel
Requires(postun):	/usr/sbin/groupdel
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Provides:	group(kvm)
%if %{with internal_qemu}
Conflicts:	qemu
%else
Requires:	qemu
%endif
%endif
# noone to test ppc
ExclusiveArch:	%{ix86} %{x8664} ia64
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# some SPARC (and PPC) boot image in ELF format
%define         _noautostrip .*%{_datadir}/qemu/openbios-.*

%ifarch %{ix86}
%define carch i386
%define karch x86
%define qemuarch x86_64
%endif
%ifarch %{x8664}
%define carch x86_64
%define karch x86
%define qemuarch x86_64
%endif
%ifarch ia64
%define carch ia64
%define karch ia64
%define qemuarch ia64
%endif
%ifarch ppc
%define carch powerpc
%define karch powerpc
%define qemuarch ppcemb
%endif

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
Group:		Applications/System
Requires:	group(kvm)

%description udev
kvm udev scripts.

%description udev -l pl.UTF-8
Skrypty udev dla kvm.

%package -n kernel%{_alt_kernel}-misc-kvm
Summary:	kvm - Linux kernel module
Summary(pl.UTF-8):	kvm - moduł jądra Linuksa
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel}
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
%setup -q -n %{pname}-%{version}
#patch0 -p1
%patch1 -p1
%patch2 -p1

sed -i 's#header-sync-$(if $(WANT_MODULE),n,y)#header-sync-n#g' Makefile
sed -i 's#^depmod_version=$#depmod_version=%{_kernel_ver}#' configure

%build
%if %{without kernel}
# qemu/configure uses linux/kvm.h to detect available features (KVM_CAP_* defs).
rm -r kvm/kernel/include/*
ln -s %{_kernelsrcdir}/include/linux kvm/kernel/include
ln -s %{_kernelsrcdir}/arch/%{karch}/include/asm kvm/kernel/include
%endif

# we build kernel modules with build_kernel_modules macro
mv -f kvm/kernel/configure kvm/kernel/configure_kvm

# not ac stuff
./configure \
	%{!?with_userspace:--disable-sdl} \
	%{!?with_userspace:--disable-gfx-check} \
	--audio-drv-list=oss,alsa \
	--cc="%{__cc}" \
	--extra-cflags="%{rpmcflags} -I/usr/include/ncurses" \
	--extra-ldflags="%{rpmldflags}" \
	--enable-mixemu \
	--disable-werror \
	--prefix=%{_prefix}

%if %{with kernel}
cd kvm/kernel
./configure_kvm \
	--arch=%{carch} \
	--kerneldir=%{_kernelsrcdir}
cd ../..
%endif

echo "CFLAGS=%{rpmcflags}" >> kvm/user/config.mak

%if %{with userspace}
%{__make} \
	CC="%{__cc}"
%endif

%if %{with kernel}
%build_kernel_modules -C kvm/kernel -m kvm,kvm-amd,kvm-intel
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%if %{without internal_qemu}
# removing files which are provided by required qemu package
rm -rf $RPM_BUILD_ROOT%{_datadir}/qemu $RPM_BUILD_ROOT%{_mandir} $RPM_BUILD_ROOT%{_docdir}
rm -f $RPM_BUILD_ROOT%{_bindir}/qemu-img
rm -f $RPM_BUILD_ROOT%{_bindir}/qemu-nbd
rm -f $RPM_BUILD_ROOT%{_bindir}/qemu-io
%endif

# changing binary name to avoid conflict with qemu
mv -f $RPM_BUILD_ROOT%{_bindir}/qemu-system-%{qemuarch} $RPM_BUILD_ROOT%{_bindir}/%{pname}
install -p kvm/kvm_stat $RPM_BUILD_ROOT%{_bindir}
install -p -D kvm/scripts/65-kvm.rules $RPM_BUILD_ROOT/etc/udev/rules.d/kvm.rules
%endif

%if %{with kernel}
%install_kernel_modules -m kvm/kernel/{kvm-amd,kvm,kvm-intel} -d misc
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 160 kvm

%postun
if [ "$1" = "0" ]; then
	%groupremove kvm
fi

%post   -n kernel%{_alt_kernel}-misc-kvm
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-misc-kvm
%depmod %{_kernel_ver}

%if %{with userspace}
%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/kvm*
%if %{with internal_qemu}
%attr(755,root,root) %{_bindir}/qemu-nbd
%attr(755,root,root) %{_bindir}/qemu-img
%attr(755,root,root) %{_bindir}/qemu-io
%{_datadir}/qemu
%{_docdir}/qemu
%{_mandir}/man1/qemu.1*
%{_mandir}/man1/qemu-img.1*
%{_mandir}/man8/qemu-nbd.8*
%endif

%files udev
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) /etc/udev/rules.d/kvm.rules
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-misc-kvm
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/kvm*
%endif
