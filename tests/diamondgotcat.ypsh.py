import os
import sys
import zipfile
import requests
import platform
import subprocess
from pathlib import Path
from typing import Tuple

def get_os_arch() -> Tuple[str, str]:
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system.startswith("darwin"):
        osname = "macos"
    elif system.startswith("windows"):
        osname = "windows"
    elif system.startswith("linux"):
        osname = "linux"
    else:
        osname = system

    if machine in ("x86_64", "amd64"):
        arch = "amd64"
    elif machine in ("arm64", "aarch64"):
        arch = "arm64"
    else:
        arch = machine

    return osname, arch

def download_and_extract(stableTag: str, osname: str, arch: str):
    script_dir = Path(__file__).resolve().parent
    tmp_dir = (script_dir / ".." / "tmp").resolve()
    tmp_dir.mkdir(parents=True, exist_ok=True)

    url = f"https://github.com/YPSH-DGC/YPSH/releases/download/{stableTag}/YPSH-{osname}-{arch}.zip"
    zip_path = tmp_dir / f"YPSH-{osname}-{arch}.zip"

    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(tmp_dir)

    if platform.system().lower().startswith("windows"):
        execFileName = f"YPSH-{osname}-{arch}.exe"
    else:
        execFileName = f"YPSH-{osname}-{arch}"
    return Path.joinpath(tmp_dir, execFileName)

def runWithStdin(path: Path, content: str, errorOnNonZero: bool = True):
    result = subprocess.run(
        [str(path)], 
        input=content.encode("utf-8"),
        capture_output=True,
        text=True,
        check=errorOnNonZero
    )
    return str(result.stdout)

TestCase1 = """
print(ypsh.version)
"""

TestCase2 = """
import("stdmath")
for i in range(1,1000) {
    print(i)
}
"""

def main():
    osname, arch = get_os_arch()
    stableTag = requests.get("https://ypsh-dgc.github.io/YPSH/channels/stable.txt").text.strip()
    execFilePath = download_and_extract(stableTag, osname, arch)

    print("Test Case 1: print the 'ypsh.version'")
    print(runWithStdin(execFilePath, TestCase1))

    print("Test Case 2: 'for' Syntax")
    print(runWithStdin(execFilePath, TestCase2))

if __name__ == "__main__":
    main()
