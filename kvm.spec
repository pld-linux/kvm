#
# Conditional build:
%bcond_without  dist_kernel             # without distribution kernel
%bcond_with     kernel                  # build for unpatched kernel (which doesn't provide kvm.ko already)
%bcond_without  smp                     # don't build SMP module
%bcond_without  userspace               # don't build userspace utilities

%define	no_install_post_strip	1

%define	_rel	0.1

Summary:	Kernel-based Virtual Machine for Linux
Summary(pl.UTF-8):	Oparta na jądrze maszyna wirtualna dla Linuksa
Name:		kvm
Version:	12
Release:	%{_rel}
License:	GPL
Group:		Applications/System
Source0:	http://dl.sourceforge.net/kvm/%{name}-%{version}.tar.gz
# Source0-md5:	c336921942daa096063bbb471ed6eecd
Patch0:         %{name}-headers.patch
URL:		http://kvm.sourceforge.net/
BuildRequires:	bash
%if %{with kernel} && %{with dist_kernel}
BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.7
BuildRequires:	rpmbuild(macros) >= 1.330
%endif
%if %{with userspace}
BuildRequires:	SDL-devel
BuildRequires:	alsa-lib-devel
BuildRequires:	gcc < 5:4.0
BuildRequires:	libuuid-devel
BuildRequires:	zlib-devel
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
%{?with_dist_kernel:%requires_releq_kernel_up}
License:	Free to use, non-distributable
Requires(post,postun):	/sbin/depmod
Requires:	module-init-tools >= 3.2.2-2

%description -n kernel%{_alt_kernel}-misc-kvm
kvm - Linux kernel module.

%description -n kernel%{_alt_kernel}-misc-kvm -l pl.UTF-8
kvm - moduł jądra Linuka.

%package -n kernel%{_alt_kernel}-smp-misc-kvm
Summary:	kvm - Linux SMP kernel module
Summary(pl.UTF-8):	kvm - moduł jądra Linuksa SMP
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
License:	Free to use, non-distributable
Requires(post,postun):	/sbin/depmod
Requires:	module-init-tools >= 3.2.2-2

%description -n kernel%{_alt_kernel}-smp-misc-kvm
kvm - Linux SMP kernel module.

%description -n kernel%{_alt_kernel}-smp-misc-kvm -l pl.UTF-8
kvm - moduł jądra Linuksa SMP.

%prep
%setup -q
%patch0 -p1

%build
# not ac stuff
./configure \
	%{!?with_kernel:--with-patched-kernel} \
	--prefix=%{_libdir}/kvm \
	--qemu-cc="%{__cc}"

%if %{with userspace}
# FIXME: no references to %{_kernelsrcdir} outside kernel allowed
%{__make} -C user KERNELDIR=%{_kernelsrcdir}
%{__make} -C qemu KERNELDIR=%{_kernelsrcdir}
%endif

%if %{with kernel}
cd kernel
mv include include-kvm
# kernel module(s)
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
		if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
				exit 1
		fi
		rm -rf include
		install -d include/{linux,config}
	cp include-kvm/linux/*.h include/linux/
		ln -sf %{_kernelsrcdir}/config-$cfg .config
		ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
		ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
		ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
	%if %{without dist_kernel}
	[ ! -x %{_kernelsrcdir}/scripts/kallsyms ] || ln -sf %{_kernelsrcdir}/scripts
	%endif
		touch include/config/MARKER
		%{__make} -C %{_kernelsrcdir} clean \
				RCS_FIND_IGNORE="-name '*.ko' -o" \
				M=$PWD O=$PWD \
				%{?with_verbose:V=1}
		%{__make} -C %{_kernelsrcdir} modules \
				M=$PWD O=$PWD \
				%{?with_verbose:V=1}
		mv kvm{,-$cfg}.ko
done
cd ..
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
%{__make} -C user install \
	DESTDIR=$RPM_BUILD_ROOT KERNELDIR=%{_kernelsrcdir}
%{__make} -C qemu install \
	DESTDIR=$RPM_BUILD_ROOT
%endif

%if %{with kernel}
%install_kernel_modules -m kernel/kvm -d misc
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post   -n kernel%{_alt_kernel}-misc-kvm
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-misc-kvm
%depmod %{_kernel_ver}

%post   -n kernel%{_alt_kernel}-smp-misc-kvm
%depmod %{_kernel_ver}smp

%postun -n kernel%{_alt_kernel}-smp-misc-kvm
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%dir %{_libdir}/kvm
%dir %{_libdir}/kvm/bin
%attr(755,root,root) %{_libdir}/kvm/bin/*
%{_libdir}/kvm/include
%{_libdir}/kvm/lib
%dir %{_libdir}/kvm/share
%{_libdir}/kvm/share/man
%{_libdir}/kvm/share/qemu
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-misc-kvm
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/kvm.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-misc-kvm
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/kvm.ko*
%endif
%endif
