{
  "title": "Migrating VMs to XCP-ng: A Tale of Trial and Error",
  "publishDate": "2026-03-04T09:00:00+09:00",
  "draft": false,
  "url": "/20260304/MigrateVMtoXCP.html",
  "params": {
    "legacy": true
  },
  "description": "I recently had hardware issues on one of my XCP‑ng hosts. Several VMs were lost and I had to rebuild the host from scratch. To rescue the remaining VMs I exported them to a new host I built recently."
}

**Migrate / Restore VMs with XCP-ng**

I recently had hardware issues on one of my XCP‑ng hosts. Several VMs were lost and I had to rebuild the host from scratch. To rescue the remaining VMs I exported them to a new host I built recently.

Because the host is reachable only remotely and is experiencing hardware failures, migration via the Xen Orchestra (XOA) integrated tool is not straightforward.

****Network difficulty**** – I managed to connect my local XOA instance to the remote host, but I cannot initiate a migration because the remote host lacks a network route to my local XCP‑ng host.

****Hardware difficulties**** – The host suffers from disk or back‑plane/controller problems, which complicates VM export; the CLI tools fail for several VMs.

Below are three methods I used to back up all VMs.

#### 1. xe vm‑export (CLI)

After installing XOA (Xen Orchestra), the simplest way to export a VM for migration is to use the *xe vm-export* command.

1.  ****Locate the VM**** – SSH into the XCP‑ng host and list all VMs, piping the output through *grep* to filter by the VM’s name:

*xe vm-list \| grep -C2 myvirtualmachine*

Example output (showing the UUID you need):

*uuid (RO) : b63b8285-94b5-3d26-9fe2-4be3ab046cd9*

*name-label (RW) : myvirtualmachine-1*

*power-state (RO) : halted*

2.  ****Export the VM**** – Using that UUID, export the VM to an XVA file:

    *xe vm-export vm=b63b8285-94b5-3d26-9fe2-4be3ab046cd9 \\*

    * filename=/run/sr-mount/a8f6df31-434f-d5e9-4163-99975b1df8ad/myvirtualmachine-1.xva*

    **Note:** An XVA is essentially a tarball containing the VHD (virtual hard disk) and an XML descriptor of the VM.

3.  ****Transfer the XVA**** – After the SCP transfer finishes (it can take many hours), import the XVA on the destination host:

    *xe vm-import filename=/run/sr-mount/SMB/Data/Backup/VirtualMachines/XCP-NG-NG/myvirtualmachine-1.xva \\*

    * sr-uuid=54b7eaaa-b873-410a-cef6-6be9999edfdd*

    Although XOA does not provide a UI import function for XVA, you can monitor the import job in XOA after invoking *vm-import* from the CLI.

#### 2. SystemRescueCD – Manual Disk Imaging

When network isolation makes XOA migration impossible and *xe vm-export* fails with I/O errors, I booted a SystemRescueCD live environment and created an image of the virtual disk for later import.

1.  ****Boot the failing VM with SystemRescueCD**** and mount a network share where the image will be saved. In my case I mounted the XCP‑ng host via *sshfs*:

    *sshfs backup@172.16.16.16:/run/sr-mount/a7f6df31-437e-dr88-4132-8af9999df8ad /mnt/sgxcp*

2.  ****Convert the raw block device to a VHD**** using *qemu-img*:

    *qemu-img convert -p -f raw -O vpc /dev/xvdb /mnt/sgxcp/mydifficultvm.vhd*

    Options:

    - *-p* – show progress
    - *-f raw* – input format is raw block device
    - *-O vpc* – output format is Microsoft VHD

3.  ****Create a VDI on the destination host**** (the VDI acts as a wrapper that XCP‑ng can attach to a VM). First retrieve the UUID of the storage repository (SR) where the VDI will reside:

    *xe sr-list*

    Sample output:

    *uuid (RO) : 54b98dd-b785-410a-cef6-6b999dfaa*

    *name-label (RW) : SR1*

    *name-description (RW): local storage on NVME1*

    *host (RO) : xcp*

    *type (RO) : ext*

    *content-type (RO) : user*

    Then create the VDI (choose a size equal to or larger than the source VHD):

    *xe vdi-create name-label=myvirtualmachine-1-xvda \\*

    * sr-uuid=54b98dd-b785-410a-cef6-6b999dfaa \\*

    * virtual-size=255GiB*

    The command returns a VDI UUID; keep note of it. If you missed it, retrieve it with:

    *xe vdi-list \| grep -C1 myvirtualmachine*

4.  ****Import the VHD into the newly created VDI****:

    *xe vdi-import filename=mydifficultvm.vhd \\*

    * format=vhd \\*

    * uuid=e0ae1995-4c6b-4a12-99a0-b70d3c9995ab \\*

    * progress=true*

5.  ****Create a VM that boots from the VDI****

    - In XOA, run the standard “Create VM” wizard (details omitted).
    - XOA requires a placeholder disk during VM creation; after the VM exists, delete the auto‑generated disk and attach the VDI you just created.

****Congratulations!**** You can now start the VM.

#### 3. Simple VHD Copy (Manual)

Another option I tried for a single VM when the previous methods failed was to copy the raw VHD file directly:

1.  Locate the VHD files on the source host (they live under the SR mount point; you can find the exact path with *df -h* after SSH’ing into the host).
2.  Copy the VHD to the new host via SCP or rsync.
3.  On the destination host, create a new VDI of the appropriate size (*xe vdi-create …*) and import the copied VHD into it (*xe vdi-import …*).
4.  Attach the VDI to a freshly created VM as described above.

This method worked intermittently; some copies still produced read errors.

#### 4. Windows Backup (Guest‑Side)

For one VM, none of the above worked. I attempted a guest‑side backup using Windows’ built‑in Backup utility, planning to:

1.  Back up the Windows VM internally.
2.  Recreate a new VM on the destination XCP‑ng host.
3.  Restore the backup after booting from a Windows ISO.

Unfortunately this method also failed.

#### 5. Manual Data Dump & Rebuild

The final approach involved manually dumping databases and files, then rebuilding the VM on the new host. I’m currently at this stage; it’s unrelated to XCP‑ng specifics, so I won’t elaborate further.

At this point only two VMs remain to be rebuilt.

### Closing Remarks

Repeating these procedures has allowed me to recover the majority of my workloads despite severe hardware failure and network isolation. The combination of:

- *xe vm-export*,
- SystemRescueCD imaging, and
- manual reconstruction

provides a flexible toolbox for any XCP‑ng disaster‑recovery scenario.

Doing and re‑doing is still working…
