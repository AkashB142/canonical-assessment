import glob
import subprocess
import sys
import time
from pathlib import Path


class TestStatus:
    """Report failures and stores the first nonzero exit status."""

    def __init__(self):
        self.code = 0

    def check(self, code, message, *output):
        if code == 0:
            return
        print(f"ERROR: retval {code} : {message}", file=sys.stderr)
        if self.code == 0:
            self.code = code
        for item in output:
            print(f"output: {item}")


def run_command(*args, stdout=None, stderr=None):
    """Run a system command and return its shell style status and output"""
    try:
        result = subprocess.run(
            args, stdout=stdout, stderr=stderr, text=True, check=False
        )
    except OSError as error:
        if stderr != subprocess.DEVNULL:
            print(f"{args[0]}: {error}", file=sys.stderr)
        return (127 if isinstance(error, FileNotFoundError) else 126), ""

    code = result.returncode
    if code < 0:
        code = 128 - code    # Convert signal return codes to Bash exit statuses
    return code, (result.stdout or "").rstrip("\n")   # Return the captured output for the before-and-after comparison



def test_disk(disk):
    if "pmem" in disk:
        print(f"Disk {disk} appears to be an NVDIMM, skipping")
        return 0

    status = TestStatus()

    code, _ = run_command("grep", "-w", "-q", disk, "/proc/partitions")
    status.check(code, f"Disk {disk} not found in /proc/partitions")

    code, _ = run_command("grep", "-w", "-q", "-m", "1", disk, "/proc/diskstats")
    status.check(code, f"Disk {disk} not found in /proc/diskstats")

    block_pattern = f"/sys/block/*{glob.escape(disk)}*"  # Match any entry in /sys/block that contains the disk name.
    code, _ = run_command("ls", *(glob.glob(block_pattern) or [f"/sys/block/*{disk}*"]),
                          # Pass the unmatched pattern to ls so it reports an error instead of listing the current directory.
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL, )  # Use ls here because the disk name is a folder entry in /sys/block.
    status.check(code, f"Disk {disk} not found in /sys/block")

    return 0

def main():
    """Use the first argument as the disk name, defaulting to sda."""
    disk = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else "sda"
    return test_disk(disk)


if __name__ == "__main__":
    sys.exit(main())