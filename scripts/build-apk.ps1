param([switch]$SkipChecks, [string]$BuildFolder = '01-today-data-fix')
$ErrorActionPreference = 'Stop'
$pulseRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $pulseRoot
if ($BuildFolder -notmatch '^\d{2}-[a-z0-9-]+$') { throw 'BuildFolder must be a numbered folder name, such as 01-today-data-fix.' }
if (-not $env:JAVA_HOME) { throw 'Set JAVA_HOME to a JDK 17 or newer before building.' }
if (-not $env:ANDROID_HOME) { $env:ANDROID_HOME = Join-Path $env:LOCALAPPDATA 'Android\Sdk' }
$env:CI = '1'
$pulseBuildRoot = $pulseRoot

function Invoke-Checked([scriptblock]$Run) {
    & $Run
    if ($LASTEXITCODE -ne 0) { throw "Build step failed with exit code $LASTEXITCODE" }
}

Set-Content -LiteralPath 'expo-env.d.ts' -Value '/// <reference types="expo/types" />'
if (-not $SkipChecks) {
    Invoke-Checked { & '.\node_modules\.bin\tsc.cmd' --noEmit }
    Invoke-Checked { & '.\node_modules\.bin\eslint.cmd' . }
    Invoke-Checked { & '.\node_modules\.bin\vitest.cmd' run }
}
Invoke-Checked { python scripts/prepare-release-signing.py }
$pulseSigning = Get-Content -LiteralPath '.release-signing\signing.json' -Raw | ConvertFrom-Json
$env:PULSE_KEYSTORE_PATH = $pulseSigning.storeFile
$env:PULSE_KEYSTORE_PASSWORD = $pulseSigning.storePassword
$env:PULSE_KEY_ALIAS = $pulseSigning.keyAlias
$env:PULSE_KEY_PASSWORD = $pulseSigning.keyPassword
try {
    if ($env:OS -eq 'Windows_NT') {
        $pulseAppVersion = (Get-Content -LiteralPath (Join-Path $pulseRoot 'app.json') -Raw | ConvertFrom-Json).expo.version
        $pulseBuildRoot = Join-Path ([IO.Path]::GetTempPath()) ('monarch-build-' + $pulseAppVersion.Replace('.', ''))
        Invoke-Checked { python scripts/prepare-build-workspace.py --destination $pulseBuildRoot }
        Set-Location -LiteralPath $pulseBuildRoot
        Invoke-Checked { npm exec --yes --package=pnpm@11.17.0 -- pnpm install --frozen-lockfile }
    }
    Invoke-Checked { & '.\node_modules\.bin\expo.cmd' prebuild --platform android --no-install }
    $pulseWrapperPath = Join-Path $pulseBuildRoot 'android\gradle\wrapper\gradle-wrapper.properties'
    Invoke-Checked { python (Join-Path $pulseRoot 'scripts\prepare-gradle.py') --wrapper $pulseWrapperPath --destination (Join-Path $pulseRoot '.build-tools') }
    $pulseWrapper = Get-Content -LiteralPath $pulseWrapperPath -Raw
    $pulseVersion = [regex]::Match($pulseWrapper, 'gradle-([\d.]+)-bin.zip').Groups[1].Value
    $pulseGradle = Join-Path $pulseRoot ".build-tools\gradle-$pulseVersion\bin\gradle.bat"
    $pulseOut = Join-Path $pulseRoot "builds\$BuildFolder"
    New-Item -ItemType Directory -Force -Path $pulseOut | Out-Null
    $pulseLog = Join-Path $pulseOut 'logs'
    New-Item -ItemType Directory -Force -Path $pulseLog | Out-Null
    & $pulseGradle -p android :app:assembleRelease '-PreactNativeArchitectures=arm64-v8a' --max-workers=2 --console=plain *> (Join-Path $pulseLog 'android-build.log')
    $pulseBuildExit = $LASTEXITCODE
    Get-Content -LiteralPath (Join-Path $pulseLog 'android-build.log') -Tail 30
    if ($pulseBuildExit -ne 0) { throw "Android build failed; see $pulseLog\android-build.log" }
    $pulseAppVersion = (Get-Content -LiteralPath (Join-Path $pulseRoot 'app.json') -Raw | ConvertFrom-Json).expo.version
    $pulseApk = Join-Path $pulseOut "pulse-mobile-$pulseAppVersion-arm64.apk"
    Copy-Item -LiteralPath 'android\app\build\outputs\apk\release\app-release.apk' -Destination $pulseApk
    $pulseHash = (Get-FileHash -LiteralPath $pulseApk -Algorithm SHA256).Hash.ToLower()
    Set-Content -LiteralPath (Join-Path $pulseOut 'SHA256SUMS.txt') -Value "$pulseHash  pulse-mobile-$pulseAppVersion-arm64.apk"
    Write-Output "APK: $pulseApk"
} finally {
    Set-Location -LiteralPath $pulseRoot
    Remove-Item Env:PULSE_KEYSTORE_PATH,Env:PULSE_KEYSTORE_PASSWORD,Env:PULSE_KEY_ALIAS,Env:PULSE_KEY_PASSWORD -ErrorAction SilentlyContinue
}
