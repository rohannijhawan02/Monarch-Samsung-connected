"""Copy public source into a short Windows build path; private files and generated output stay excluded."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--destination", required=True, type=Path)
args = parser.parse_args()
destination = args.destination.resolve()
temporary = Path(tempfile.gettempdir()).resolve()
if not destination.is_relative_to(temporary) or not destination.name.startswith("monarch-build-"):
    raise RuntimeError("Build workspace must be a monarch-build-* directory within the user's temporary folder")
if " " in str(destination):
    raise RuntimeError("The build workspace path must not contain spaces")
marker = destination / ".monarch-build-source.json"
if destination.exists() and any(destination.iterdir()) and not marker.exists():
    raise RuntimeError("Refusing to modify a nonempty directory that was not created by this build helper")
if marker.exists() and json.loads(marker.read_text())["source"] != str(root):
    raise RuntimeError("Build workspace belongs to another source directory")
destination.mkdir(parents=True, exist_ok=True)
files = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root).split(b"\0")
digests = {}
for entry in files:
    if not entry:
        continue
    relative = entry.decode("utf-8")
    if relative.startswith((".release-signing/", ".git/", ".research/", "node_modules/")):
        continue
    source = root / relative
    target = (destination / relative).resolve()
    if not target.is_relative_to(destination):
        raise RuntimeError("Source path escapes build workspace")
    if not source.is_file():
        continue
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    digests[relative] = hashlib.sha256(source.read_bytes()).hexdigest()
# pnpm 11 reads dependency-layout settings from pnpm-workspace.yaml, not .npmrc.
workspace_settings = destination / "pnpm-workspace.yaml"
settings = workspace_settings.read_text(encoding="utf-8")
settings += "\nnodeLinker: hoisted\n"
workspace_settings.write_text(settings, encoding="utf-8")
(destination / "expo-env.d.ts").write_text('/// <reference types="expo/types" />\n', encoding="utf-8")
marker.write_text(json.dumps({"source": str(root), "files": digests}, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"build_workspace": str(destination), "source_files": len(digests), "private_files_copied": False}))
