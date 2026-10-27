{
  "title": "XCP-ng Community Edition: Streamlining XOA Setup",
  "publishDate": "2026-04-01T09:00:00+09:00",
  "draft": false,
  "url": "/20260401/XCP-ngCommunityEdition.html",
  "params": {
    "legacy": true
  },
  "description": "A community-built ISO of XCP-ng that removes the friction of initial setup by pointing XO Lite's deployment flow to a self-hosted XOA image."
}

## XCP-ng **Community** Edition

A community-built ISO of XCP-ng that removes the friction of initial setup by pointing XO Lite's deployment flow to a self-hosted XOA image.

Status: Active development Platform: GitHub Actions Base: XCP-ng 8.x April 2026

01 — Background

### Why this exists

XCP-ng ships with XO Lite, a lightweight management SPA served directly from XAPI. When a fresh host is installed and opened in a browser, XO Lite offers a button to deploy XOA — Xen Orchestra Appliance, the full management interface. Out of the box, that button points to a Vates-hosted image.

For home labbers who want to get into XCP-ng the build from source while being incredibley simplified now by Ronivay’s work \[ <https://github.com/ronivay/XenOrchestraInstallerUpdater>\] this is unnecessary friction.

*The goal is to get it’s XCP-ng with XOA up and running as simply as possible with the community version ( build from source ) of XOA.*

02 — Architecture

### What the build changes

The project is intentionally minimal: one fork and one ISO builder repository, with no scheduled jobs, no cross-repo dispatches, and no GitHub Pages infrastructure.

Single Repo

Fork of ****vatesfr/xen-orchestra****. Contains a patch to **xoa-deploy.vue** that rewrites the XVA download URL from the Vates appliance to a community-hosted image.

ISO builder with a single GitHub Actions workflow. Pulls the upstream XCP-ng ISO, patches the XO Lite RPM in place, rebuilds the ISO with correct hybrid boot flags, and uploads the artifact.

#### The two patch targets

XO Lite has a two-layer loading model. The outer index.html contains a try/catch block that load lite.xen-orchestra.com to fetch the latest build before falling back to the locally bundled xolite.html. The patched build removes that block entirely. The XVA download URL lives inside the compiled JS of xoa-deploy.vue and is rewritten via sed to a community URL at this stage it’s only on my local network :D

03 — Build pipeline

### How the ISO is assembled

#### RPM built from source

A first approach of patching compiled assets with rpmrebuild was discarded in favour of a full source build. The core problem with the binary-patch approach was Vite's content-hashed output filenames — XoaDeployView-Dn74Z1bd.js changes on every upstream rebuild, requiring manual re-discovery of the new filename with each XCP-ng ISO update. Anyway this was not a reliable option in the long run.

The current pipeline builds the RPM from source: clone the repo, apply a single git-format patch to the TypeScript source, compile with yarn/Vite, assemble a tarball, and run rpmbuild with a minimally modified community spec. The patch lives at the correct abstraction level and is designed to survives upstream filename changes automatically.

The patch file is the only artifact that encodes the community customization — everything else is standard plumbing that follows the upstream spec unchanged.

#### Build sequence

A

****Detect version from the ISO.**** Query the XO Lite RPM already present in the extracted ISO to get the exact version string, rather than hardcoding it.

XO_LITE_RPM=\$(find iso-work/Packages/ -name "xo-lite\*.rpm" \| head -1) XO_VERSION=\$(rpm -qp --queryformat '%{VERSION}' "\$XO_LITE_RPM")

B

****C****lone the**** xen-orchestra**** repo****.

git clone https://github.com/vatesfr/xen-orchestra.git

C

****Apply the community patch.**** A standard git diff-format patch targeting @xen-orchestra/lite/src/views/deploy-xoa/DeployXoaView.vue. It replaces the hardcoded Vates XVA URL with a new URL, inserted before the existing XAPI import call.

git apply patches/community-xoa-deploy.patch

D

****Install dependencies and build.**** Uses the repo's turbo pipeline.

yarn build:xo-lite

E

****Assemble the source tarball.**** The spec's %autosetup expects a top-level directory named xo-lite-{VERSION}/ containing the Vite dist/ output with the patched index.html, the LICENSE and CHANGELOG.md.

TARBALL_DIR="xo-lite-\${XO_VERSION}" tar -czf "xo-lite-\${XO_VERSION}.tar.gz" "\${TARBALL_DIR}/"

F

****Build the RPM with rpmbuild.**** The community spec is the upstream spec with two changes only: Source0 points to the local tarball, and the Release field gets a community.1 suffix.

mkdir -p ~/rpmbuild/{SOURCES,SPECS,RPMS,SRPMS,BUILD} cp "xo-lite-\${XO_VERSION}.tar.gz" ~/rpmbuild/SOURCES/ cp SPECS/xo-lite-community.spec ~/rpmbuild/SPECS/ rpmbuild -ba ~/rpmbuild/SPECS/xo-lite-community.spec \\ --define "\_topdir \$HOME/rpmbuild"

G

****Swap the RPM into the ISO.**** Remove the original, drop in the new one, and let createrepo_c --update rebuild the repo metadata.

rm -f "\$XO_LITE_RPM" cp ~/rpmbuild/RPMS/noarch/xo-lite-\*.rpm iso-work/Packages/

#### ISO repack with hybrid boot support

Early test I used genisoimage, but couldn’t get it boot on a physical machine. The current pipeline uses xorriso -as mkisofs for the ISO, followed by a mandatory isohybrid --uefi post-processing step from syslinux-utils to stamp the full partition table. This is now working and I have both legacy Bios or UEFI boot mode.

#### Answerfile via isolinux.cfg

Replacing the signed XO Lite RPM invalidates repomd.xml.asc, which would cause the installer to abort with a GPG verification failure. The answerfile is served externally over HTTP and the installer is pointed to it via a kernel parameter injected directly into isolinux.cfg.

The build step patches the boot configuration with a single sed in-place substitution:

sed -i \\ 's\|--- /install.img\|answerfile=http://192.168.0.1:3000/answerfile.xml install --- /install.img\|' \\ iso-work/boot/isolinux/isolinux.cfg

At install time the host-installer fetches the answerfile from that URL. The answerfile itself carries the GPG bypass directives and any other unattended installation parameters.

This is a workaround for now as the ISO rebuild is breaking the GPG check, an issue that needs to be investigated to fix in the future, sooner than later.

04 — Lessons learned

### Lot’s of learning !

GPG attrs

##### Two independent attributes, not one

gpgcheck and repo_gpgcheck are separate. Couldn’t find documentation about it but the XCP-ng forum was helpful as well as the installer source at answerfile.py.

Network

##### VIF network selection bug

filteredNetworks in xoa-deploy.vue seems to sorts alphabetically, time to time auto-selecting "Host internal management network" over the correct VIF linked to the Eth. A fix would requires filtering networks with VIF associations, or forcing explicit user selection.

PS: This is currently an issue because my XOA image is not using the configuration

provided by XO-lite.

05 — Remaining work

### What comes next

\- Support GPG check in the ISO build to remove the Answerfile workaround

\- Find a way to set user/pass, NIC, XOA, ssh pass to the image provided by Ronivay.

*- Build a middleware that support HTTPS and gunzip format and re-stream seemlessly to xapi VM.import which doesn’t support HTTPS and gunzip format.*
