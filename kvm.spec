%bcond_with	patched_kernel
Summary:	Kernel-based Virtual Machine for Linux
Name:		kvm
Version:	10
Release:	0.1
License:	GPL
Group:		Applications/System
Source0:	http://dl.sourceforge.net/kvm/%{name}-%{version}.tar.gz
# Source0-md5:	41acb4a19818e70bf5833a2b1fa987a8
URL:		http://kvm.sourceforge.net/
BuildRequires:	bash
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
KVM (for Kernel-based Virtual Machine) is a full virtualization
solution for Linux on x86 hardware. It consists of a loadable kernel
module (kvm.ko) and a userspace component.

Using KVM, one can run multiple virtual machines running unmodified
Linux or Windows images. Each virtual machine has private virtualized
hardware: a network card, disk, graphics adapter, etc.

%prep
%setup -q

%build
# not ac stuff
./configure \
	%{?with_patched_kernel:--with-patched-kernel} \
	--prefix=%{_libdir}/kvm \
	--qemu-cc="%{__cc}"
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
