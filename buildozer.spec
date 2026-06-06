[app]
# (str) Title of your application
title = YT-DLP Downloader Pro

# (str) Package name
package.name = ytdlppro

# (str) Package domain (needed for android packaging)
package.domain = org.test

# (str) Source code directory
source.dir = .

# (list) Source files to include (so extension must be included for ffmpeg.so)
source.include_exts = py,png,jpg,kv,atlas,so

# (str) Application versioning
version = 1.0

# (list) Application requirements
# Python core + UI + downloader dependencies + android bridge (pyjnius)
requirements = python3, kivy, yt-dlp, openssl, certifi, urllib3, pyjnius

# (str) Supported orientations
orientation = portrait

# (bool) Use fullscreen or not
fullscreen = 0

# ==============================================================================
# Android Specific Configurations
# ==============================================================================

# (list) Android permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API (API 33 is modern and stable)
android.api = 33

# (int) Minimum API supported (Android 5.0+)
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25.2.9519653

# (bool) Private storage (keeps app internal files private)
android.private_storage = True

# (bool) Copy library (.so) instead of loading directly (Recommended for Kivy)
android.copy_libs = 1

# (str) Logcat filters
android.logcat_filters = *:S python:D

# (bool) Request legacy external storage (Android 10 storage compatibility)
android.request_legacy_external_storage = True
