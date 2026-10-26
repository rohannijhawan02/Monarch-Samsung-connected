"""Create this fork's persistent local release key. Never print or commit its credentials."""
import json
import os
from pathlib import Path
import secrets
import subprocess

root = Path(__file__).resolve().parents[1]
directory = root / ".release-signing"
directory.mkdir(exist_ok=True)
config = directory / "signing.json"
keystore = directory / "monarch-release.p12"
if config.exists() and keystore.exists():
    print("Existing Monarch release signing key retained")
elif config.exists() or keystore.exists():
    raise RuntimeError("Incomplete signing setup; refusing to overwrite either existing file")
else:
    password = secrets.token_urlsafe(48)
    tool = Path(os.environ["JAVA_HOME"]) / "bin" / ("keytool.exe" if os.name == "nt" else "keytool")
    environment = {**os.environ, "PULSE_SIGNING_PASSWORD": password}
    subprocess.run([str(tool), "-genkeypair", "-keystore", str(keystore), "-storetype", "PKCS12",
                    "-alias", "monarch", "-keyalg", "RSA", "-keysize", "3072", "-validity", "10000",
                    "-storepass:env", "PULSE_SIGNING_PASSWORD", "-keypass:env", "PULSE_SIGNING_PASSWORD",
                    "-dname", "CN=Monarch, OU=Personal App, O=Monarch, C=IN"],
                   env=environment, check=True, capture_output=True)
    config.write_text(json.dumps({"storeFile": str(keystore), "storePassword": password,
                                  "keyAlias": "monarch", "keyPassword": password}) + "\n", encoding="utf-8")
    print("Created Monarch release signing key in the git-ignored .release-signing folder")
