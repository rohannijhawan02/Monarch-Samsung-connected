// Configure generated native code through Expo CNG. The private signing values arrive only at build time.
const { withAppBuildGradle } = require("expo/config-plugins");

module.exports = function withMonarchRelease(config) {
  return withAppBuildGradle(config, (mod) => {
    const marker = "// Monarch release signing";
    if (!mod.modResults.contents.includes(marker)) mod.modResults.contents += `
${marker}
def monarchStore = System.getenv('PULSE_KEYSTORE_PATH')
if (monarchStore) {
    android {
        signingConfigs {
            monarch {
                storeFile file(monarchStore)
                storePassword System.getenv('PULSE_KEYSTORE_PASSWORD')
                keyAlias System.getenv('PULSE_KEY_ALIAS')
                keyPassword System.getenv('PULSE_KEY_PASSWORD')
                storeType 'PKCS12'
            }
        }
        buildTypes.release.signingConfig = signingConfigs.monarch
    }
} else if (gradle.startParameter.taskNames.any { it.toLowerCase().contains('release') }) {
    throw new GradleException('Monarch release signing is missing. Run scripts/build-apk.ps1 or configure the release signing environment.')
}
`;
    return mod;
  });
};
