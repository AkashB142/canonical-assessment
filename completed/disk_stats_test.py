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
    #test_flow
    return 0

def main():
    """Use the first argument as the disk name, defaulting to sda."""
    disk = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else "sda"
    return test_disk(disk)


if __name__ == "__main__":
    sys.exit(main())