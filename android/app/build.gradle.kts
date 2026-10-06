plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}
android {
    namespace = "ma.weather.morocco"
    compileSdk = 35
    defaultConfig {
        applicationId = "ma.weather.morocco"
        minSdk = 23
        targetSdk = 35
        versionCode = 1
        versionName = "0.1.0"
        val weatherAppUrl = (project.findProperty("weatherAppUrl") as String?) ?: "https://weather.example.invalid/mobile-ui/"
        buildConfigField("String", "WEATHER_APP_URL", "\\\"${weatherAppUrl}\\\"")
    }
    buildFeatures { buildConfig = true }
}
