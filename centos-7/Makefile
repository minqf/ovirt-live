all:		\
		prereq \
		packages \
		livecd \
		$(NULL)

clean:
	rm -fr downloads/*.tmp
	rm -fr *.tmp
	rm -f kickstart/ovirt-live-ovirt-custom.ks
	rm -rf oVirtLiveFiles/iso

dist-clean:	clean

maintainer-clean:	dist-clean
	rm -fr downloads

prereq:
	if [ $$(id -u) != 0 ]; then echo "You must be root"; exit 1; fi

download: 	\
		downloads/TinyCore-current.iso \
		$(NULL)

_download:
	mkdir -p downloads
	rm -f "downloads/$(OUT)"
	curl "$(URL)" > "downloads/$(OUT).tmp"
	mv "downloads/$(OUT).tmp" "downloads/$(OUT)"

downloads/TinyCore-current.iso:
	$(MAKE) _download URL="http://distro.ibiblio.org/tinycorelinux/7.x/x86/release/TinyCore-current.iso" OUT="TinyCore-current.iso"

packages:
	rpm -ql livecd-tools > /dev/null 2>&1 || \
		yum install -y \
		http://mirror.centos.org/centos-7/7/extras/x86_64/Packages/livecd-tools-21.4-2.el7.x86_64.rpm \
		http://mirror.centos.org/centos-7/7/extras/x86_64/Packages/python-imgcreate-21.4-2.el7.x86_64.rpm \
		http://mirror.centos.org/centos-7/7/extras/x86_64/Packages/hfsplus-tools-540.1.linux3-4.el7.x86_64.rpm


.SUFFIXES:
.SUFFIXES: .in
.in:
	sed \
		-e "s#@PATH@#$$(pwd)#g" \
		"$<" > "$@"

livecd:		\
		downloads/TinyCore-current.iso \
		kickstart/ovirt-live-ovirt-custom.ks \
		$(NULL)
	mkdir -p oVirtLiveFiles/iso
	cp downloads/TinyCore-current.iso oVirtLiveFiles/iso/
	livecd-creator -d -v -p --config=kickstart/ovirt-live-ovirt-custom.ks --fslabel=ovirt-live-master.$(shell date -u +%y%m%d%H%M) 2>&1 | tee iso.log
