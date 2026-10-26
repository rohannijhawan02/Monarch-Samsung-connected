"""Publish this fork's APK through GitHub Releases, using the existing Git credential helper.

Credentials stay in memory; only public identifiers and download links are printed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

REPOSITORY = "rohannijhawan02/Monarch-Samsung-connected"
ROOT = Path(__file__).resolve().parents[1]

def credential():
    result = subprocess.run(["git", "credential", "fill"], input="protocol=https\nhost=github.com\n\n", text=True,
                            capture_output=True, check=True,
                            env={**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"})
    fields = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
    token = fields.get("password")
    if not token:
        raise RuntimeError("GitHub credentials are unavailable to Git's credential helper")
    return token

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--apk", type=Path)
    parser.add_argument("--notes", type=Path)
    parser.add_argument("--commit")
    parser.add_argument("--name", default="Monarch — phone-test candidate")
    arguments = parser.parse_args()
    token = credential()

    def api(path, body=None, binary=None, upload=False):
        base = "https://uploads.github.com" if upload else "https://api.github.com"
        request = Request(base + path, data=binary if binary is not None else (json.dumps(body).encode() if body is not None else None),
                          headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
                                   "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "Monarch-release-script",
                                   "Content-Type": "application/vnd.android.package-archive" if binary is not None else "application/json"})
        with urlopen(request, timeout=180) as response:
            return json.load(response)

    account = api("/user")
    if account["login"].lower() != "rohannijhawan02":
        raise RuntimeError("The local Git credential belongs to a different account; no write performed")
    repo = api("/repos/" + REPOSITORY)
    if not repo.get("permissions", {}).get("push"):
        raise RuntimeError("The GitHub credential cannot publish to this repository")
    if arguments.check:
        print(json.dumps({"account": account["login"], "repository": repo["html_url"], "can_push": True}))
        return
    if not arguments.apk or not arguments.notes or not arguments.commit:
        parser.error("--apk, --notes and --commit are required for publication")
    artifact = arguments.apk.resolve()
    if not artifact.is_relative_to((ROOT / "builds").resolve()) or not artifact.is_file():
        raise RuntimeError("APK must be an existing build artifact under builds/")
    version = json.loads((ROOT / "app.json").read_text())["expo"]["version"]
    tag = "v" + version
    source_commit = api(f"/repos/{REPOSITORY}/commits/{quote(arguments.commit, safe='')}")["sha"]
    try:
        reference = api(f"/repos/{REPOSITORY}/git/ref/tags/{quote(tag, safe='')}")["object"]
        for _ in range(5):
            if reference["type"] != "tag":
                break
            reference = api(f"/repos/{REPOSITORY}/git/tags/{reference['sha']}")["object"]
        if reference["type"] != "commit" or reference["sha"] != source_commit:
            raise RuntimeError("This version tag already points at a different commit; no release write performed")
    except HTTPError as error:
        if error.code != 404:
            raise
    try:
        release = api(f"/repos/{REPOSITORY}/releases/tags/{tag}")
    except HTTPError as error:
        if error.code != 404:
            raise
        release = api(f"/repos/{REPOSITORY}/releases", {"tag_name": tag, "target_commitish": source_commit,
                      "name": arguments.name, "body": arguments.notes.read_text(encoding="utf-8"),
                      "draft": False, "prerelease": True, "make_latest": "false"})
    content = artifact.read_bytes()
    digest = "sha256:" + hashlib.sha256(content).hexdigest()
    existing = next((a for a in release["assets"] if a["name"] == artifact.name), None)
    if existing:
        if existing.get("digest") != digest:
            raise RuntimeError("An asset with this name already exists with a different or unverified digest; no overwrite performed")
        asset = existing
    else:
        asset = api(f"/repos/{REPOSITORY}/releases/{release['id']}/assets?name={quote(artifact.name)}", binary=content, upload=True)
    verified = api(f"/repos/{REPOSITORY}/releases/{release['id']}")
    if not any(a["id"] == asset["id"] and a["size"] == len(content) and a.get("digest", digest) == digest for a in verified["assets"]):
        raise RuntimeError("Uploaded asset could not be verified")
    print(json.dumps({"release": verified["html_url"], "download": asset["browser_download_url"], "sha256": digest,
                      "release_id": release["id"], "asset_id": asset["id"]}))

if __name__ == "__main__":
    main()
