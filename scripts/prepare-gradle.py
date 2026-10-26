"""Download and verify the Gradle version pinned by Expo's generated wrapper."""
from pathlib import Path
import argparse
import hashlib
import re
from urllib.request import urlopen
from zipfile import ZipFile

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--wrapper", type=Path, default=root / "android/gradle/wrapper/gradle-wrapper.properties")
parser.add_argument("--destination", type=Path, default=root / ".build-tools")
args = parser.parse_args()
properties = args.wrapper.read_text()
version = re.search(r"gradle-([\d.]+)-bin.zip", properties).group(1)
destination = args.destination.resolve()
destination.mkdir(parents=True, exist_ok=True)
if not (destination / f"gradle-{version}/bin/gradle.bat").exists():
    base = f"https://downloads.gradle.org/distributions/gradle-{version}-bin.zip"
    with urlopen(base + ".sha256", timeout=60) as response:
        expected = response.read().decode().strip().split()[0]
    archive = destination / f"gradle-{version}-bin.zip"
    digest = hashlib.sha256()
    with urlopen(base, timeout=120) as response, archive.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            digest.update(chunk)
            output.write(chunk)
    if digest.hexdigest() != expected:
        raise RuntimeError("Gradle checksum mismatch")
    with ZipFile(archive) as package:
        for entry in package.infolist():
            if not (destination / entry.filename).resolve().is_relative_to(destination.resolve()):
                raise RuntimeError("Archive path escapes destination")
        package.extractall(destination)
    print(f"Downloaded Gradle {version}; official SHA-256 verified")
else:
    print(f"Gradle {version} already available")
