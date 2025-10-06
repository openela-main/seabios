Name:           seabios
Version:        1.16.3
Release:        7%{?dist}
Summary:        Open-source legacy BIOS implementation

License:        LGPL-3.0-only
URL:            https://www.coreboot.org/SeaBIOS

Source0:        https://code.coreboot.org/p/seabios/downloads/get/seabios-1.16.3.tar.gz


Source10:       config.vga-cirrus
Source13:       config.vga-stdvga
Source18:       config.seabios-256k
Source19:       config.vga-virtio
Source20:       config.vga-ramfb
Source21:       config.vga-bochs-display

Patch1: 0001-add-hwerr_printf-function-for-threads.patch
Patch2: 0002-display-error-message-for-blocksizes-512.patch
# For RHEL-67847 - amdgpu failed to initialize when multiple AMD MI210 GPUs assigned and firmware is seabios [rhel-10]
Patch3: seabios-pciinit-don-t-misalign-large-BARs.patch

BuildRequires: make
BuildRequires: gcc
BuildRequires: python3

ExclusiveArch: x86_64

Requires: %{name}-bin = %{version}-%{release}
Requires: seavgabios-bin = %{version}-%{release}

# Seabios is noarch, but required on architectures which cannot build it.
# Disable debuginfo because it is of no use to us.
%global debug_package %{nil}

# Similarly, tell RPM to not complain about x86 roms being shipped noarch
%global _binaries_in_noarch_packages_terminate_build   0

# You can build a debugging version of the BIOS by setting this to a
# value > 1.  See src/config.h for possible values, but setting it to
# a number like 99 will enable all possible debugging.  Note that
# debugging goes to a special qemu port that you have to enable.  See
# the SeaBIOS top-level README file for the magic qemu invocation to
# enable this.
%global debug_level 1


%description
SeaBIOS is an open-source legacy BIOS implementation which can be used as
a coreboot payload. It implements the standard BIOS calling interfaces
that a typical x86 proprietary BIOS implements.


%package bin
Summary: Seabios for x86
Buildarch: noarch


%description bin
SeaBIOS is an open-source legacy BIOS implementation which can be used as
a coreboot payload. It implements the standard BIOS calling interfaces
that a typical x86 proprietary BIOS implements.


%package -n seavgabios-bin
Summary: Seavgabios for x86
Buildarch: noarch

%description -n seavgabios-bin
SeaVGABIOS is an open-source VGABIOS implementation.


%prep
%setup -q
%autopatch -p1

%build
%define _lto_cflags %{nil}
export CFLAGS="$RPM_OPT_FLAGS"
mkdir binaries

build_bios() {
    make PYTHON=%{__python3} clean distclean
    cp $1 .config
    echo "CONFIG_TCGBIOS=n" >> .config
    echo "CONFIG_DEBUG_LEVEL=%{debug_level}" >> .config
    make PYTHON=%{__python3} oldnoconfig V=1 EXTRAVERSION="-%release"

    make V=1 \
        EXTRAVERSION="-%{release}" \
        PYTHON=%{__python3} \
%if 0%{?cross:1}
        HOSTCC=gcc \
        CC=x86_64-linux-gnu-gcc \
        AS=x86_64-linux-gnu-as \
        LD=x86_64-linux-gnu-ld \
        OBJCOPY=x86_64-linux-gnu-objcopy \
        OBJDUMP=x86_64-linux-gnu-objdump \
        STRIP=x86_64-linux-gnu-strip \
%endif
        $4

    cp out/$2 binaries/$3
}

# seabios
build_bios %{_sourcedir}/config.seabios-256k bios.bin bios-256k.bin


# seavgabios
%global vgaconfigs cirrus stdvga virtio ramfb bochs-display
for config in %{vgaconfigs}; do
    build_bios %{_sourcedir}/config.vga-${config} \
               vgabios.bin vgabios-${config}.bin out/vgabios.bin
done


%install
mkdir -p $RPM_BUILD_ROOT%{_datadir}/seabios
mkdir -p $RPM_BUILD_ROOT%{_datadir}/seavgabios
install -m 0644 binaries/bios-256k.bin $RPM_BUILD_ROOT%{_datadir}/seabios/bios-256k.bin
install -m 0644 binaries/vgabios*.bin $RPM_BUILD_ROOT%{_datadir}/seavgabios


%files
%doc COPYING COPYING.LESSER README


%files bin
%dir %{_datadir}/seabios/
%{_datadir}/seabios/bios*.bin

%files -n seavgabios-bin
%dir %{_datadir}/seavgabios/
%{_datadir}/seavgabios/vgabios*.bin

%changelog
* Thu Nov 28 2024 Miroslav Rezanina <mrezanin@redhat.com> - 1.16.3-7
- seabios-Remove-iasl-from-BuildRequires.patch [RHEL-68975]
- Resolves: RHEL-68975
  (remove iasl build dependency)

* Tue Nov 26 2024 Miroslav Rezanina <mrezanin@redhat.com> - 1.16.3-6
- seabios-pciinit-don-t-misalign-large-BARs.patch [RHEL-67847]
- Resolves: RHEL-67847
  (amdgpu failed to initialize when multiple AMD MI210 GPUs assigned and firmware is seabios [rhel-10])

* Tue Oct 29 2024 Troy Dawson <tdawson@redhat.com> - 1.16.3-5
- Bump release for October 2024 mass rebuild:
  Resolves: RHEL-64018

* Mon Jun 24 2024 Troy Dawson <tdawson@redhat.com> - 1.16.3-4
- Bump release for June 2024 mass rebuild

* Thu Apr 04 2024 Miroslav Rezanina <mrezanin@redhat.com> - 1.16.3-3
- Import package from RHEL 9
- Resolves: RHEL-31220
  (Update seabios to RHEL structure)
