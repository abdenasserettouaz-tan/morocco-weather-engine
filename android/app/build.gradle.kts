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
        versionCode = 2
        versionName = "0.2.0"
        val weatherAppUrl = (project.findProperty("weatherAppUrl") as String?) ?: "https://abdenasserettouaz-tan.github.io/morocco-weather-engine/"
        buildConfigField("String", "WEATHER_APP_URL", "\"${weatherAppUrl}\"")
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures { buildConfig = true }
}
