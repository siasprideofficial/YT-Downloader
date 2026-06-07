[app]
# (str) Title of your application
title = YT-DLP Downloader Pro

# (str) Package name
package.name = ytdlppro

# (str) Package domain (needed for android packaging)
package.domain = org.test

# (str) Source code directory
source.dir = .

# (list) Source files to include (using so extension)
source.include_exts = py,png,jpg,kv,atlas,so

# (str) Application versioning
version = 1.0

# (list) Application requirements
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

# (int) Target Android API
android.api = 33

# (int) Minimum API supported (Android 5.0+)
android.minapi = 21

# (bool) Private storage
android.private_storage = True

# (bool) Copy library (.so) instead of loading directly (Recommended for Kivy)
android.copy_libs = 1

# (str) Logcat filters
android.logcat_filters = *:S python:D

# (bool) Request legacy external storage (Android 10 storage compatibility)
android.request_legacy_external_storage = True
