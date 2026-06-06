import os
import sys
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.uix.image import AsyncImage
from kivy.core.clipboard import Clipboard
from kivy.utils import platform
from kivy.clock import mainthread

# Console bypass stream
class SafeStream:
    def write(self, data): pass
    def flush(self): pass

# Dummy logger
class MyLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

class DownloaderApp(App):
    def build(self):
        self.title = "YT-DLP Downloader Pro"
        
        # 1. Root ScrollView
        root_scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        
        # 2. Main Content Layout
        content_layout = BoxLayout(
            orientation='vertical', 
            spacing=15, 
            size_hint_x=1,
            size_hint_y=None,
            padding=[20, 30, 20, 30]
        )
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Title Label
        self.label = Label(
            text="YT-DLP Downloader Pro", 
            font_size='20sp', 
            bold=True,
            size_hint_y=None, 
            height=50,
            color=(0.12, 0.53, 0.9, 1),
            halign="center"
        )
        self.label.bind(size=self.label.setter('text_size'))
        content_layout.add_widget(self.label)
        
        # Thumbnail Preview
        self.thumbnail = AsyncImage(
            source="",
            size_hint_y=None,
            height=0,
            allow_stretch=True
        )
        content_layout.add_widget(self.thumbnail)
        
        # URL Input Row (Icons replaced with Clean Text to avoid [] boxes)
        url_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=55, spacing=5)
        
        self.url_input = TextInput(
            hint_text="Video URL paste karein...", 
            multiline=False, 
            font_size='15sp',
            padding=[12, 15, 12, 15],
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1),
            size_hint_x=0.6
        )
        url_row.add_widget(self.url_input)
        
        # Clear Button
        clear_btn = Button(
            text="Clear", 
            size_hint_x=0.2,
            font_size='14sp',
            background_normal='',
            background_color=(0.25, 0.25, 0.25, 1)
        )
        clear_btn.bind(on_press=self.clear_fields)
        url_row.add_widget(clear_btn)
        
        # Paste Button
        paste_btn = Button(
            text="Paste", 
            size_hint_x=0.2,
            font_size='14sp',
            background_normal='',
            background_color=(0.12, 0.53, 0.9, 1)
        )
        paste_btn.bind(on_press=self.paste_from_clipboard)
        url_row.add_widget(paste_btn)
        
        content_layout.add_widget(url_row)
        
        # Settings Row
        settings_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        self.quality_spinner = Spinner(
            text='Select Quality (720p)',
            values=('1080p (Best)', '720p (HD)', '480p (SD)', 'Audio Only (M4A)'),
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.2, 0.2, 0.2, 1)
        )
        settings_row.add_widget(self.quality_spinner)
        
        # Subtitle Checkbox
        sub_layout = BoxLayout(orientation='horizontal', size_hint_x=0.5, spacing=5)
        self.sub_checkbox = CheckBox(size_hint_x=0.2)
        sub_label = Label(text="Subtitles (.srt)", font_size='14sp', halign="left", size_hint_x=0.8)
        sub_label.bind(size=sub_label.setter('text_size'))
        
        sub_layout.add_widget(self.sub_checkbox)
        sub_layout.add_widget(sub_label)
        settings_row.add_widget(sub_layout)
        
        content_layout.add_widget(settings_row)
        
        # Fetch Details Button
        self.fetch_btn = Button(
            text="LOAD VIDEO DETAILS",
            size_hint_y=None,
            height=45,
            font_size='14sp',
            background_normal='',
            background_color=(0.18, 0.18, 0.18, 1),
            color=(0.12, 0.53, 0.9, 1)
        )
        self.fetch_btn.bind(on_press=self.start_fetch_thread)
        content_layout.add_widget(self.fetch_btn)
        
        # Download Button
        self.download_btn = Button(
            text="START DOWNLOAD", 
            size_hint_y=None, 
            height=55,
            font_size='16sp',
            bold=True,
            background_normal='',
            background_color=(0.12, 0.8, 0.4, 1)
        )
        self.download_btn.bind(on_press=self.start_download_thread)
        content_layout.add_widget(self.download_btn)
        
        # Open Folder Button
        self.open_folder_btn = Button(
            text="OPEN DOWNLOADS FOLDER",
            size_hint_y=None,
            height=50,
            font_size='14sp',
            background_normal='',
            background_color=(0.25, 0.25, 0.25, 1)
        )
        self.open_folder_btn.bind(on_press=self.open_downloads_folder)
        content_layout.add_widget(self.open_folder_btn)
        
        # Status Label (Height increased to 120 so long errors wrap and display fully)
        self.status_label = Label(
            text="Status: Ready", 
            size_hint_y=None, 
            height=120,
            font_size='13sp',
            halign="center",
            valign="middle",
            color=(0.7, 0.7, 0.7, 1)
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        content_layout.add_widget(self.status_label)
        
        root_scroll.add_widget(content_layout)
        
        return root_scroll

    @mainthread
    def update_status(self, text):
        self.status_label.text = text

    @mainthread
    def set_preview(self, title, thumb_url):
        self.label.text = title[:60] + "..." if len(title) > 60 else title
        if thumb_url:
            self.thumbnail.source = thumb_url
            self.thumbnail.height = 180 
        else:
            self.thumbnail.height = 0

    def paste_from_clipboard(self, instance):
        try:
            self.url_input.text = Clipboard.paste()
            self.update_status("Status: URL Pasted")
        except Exception as e:
            self.update_status("Status: Clipboard access failed")

    def clear_fields(self, instance):
        self.url_input.text = ""
        self.set_preview("YT-DLP Downloader Pro", "")
        self.update_status("Status: Fields Cleared")

    def start_fetch_thread(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.update_status("Status: Please paste a URL first")
            return
        self.update_status("Status: Fetching details...")
        threading.Thread(target=self.fetch_details, args=(url,)).start()

    def fetch_details(self, url):
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = SafeStream()
        sys.stderr = SafeStream()

        try:
            import yt_dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Video Loaded')
                thumbnail = info.get('thumbnail', '')
                self.set_preview(title, thumbnail)
                self.update_status("Status: Details loaded. Ready to Download!")
        except Exception as e:
            self.update_status(f"Status: Failed to load details - {str(e)}")
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0.0%').strip()
            speed = d.get('_speed_str', 'N/A').strip()
            eta = d.get('_eta_str', 'N/A').strip()
            self.update_status(f"Progress: {percent}\nSpeed: {speed} | ETA: {eta}")
        elif d['status'] == 'finished':
            self.update_status("Status: Saving video...")

    def start_download_thread(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.update_status("Status: Please enter a URL")
            return
        self.update_status("Status: Connecting...")
        threading.Thread(target=self.download_video, args=(url,)).start()

    def download_video(self, url):
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = SafeStream()
        sys.stderr = SafeStream()

        try:
            import yt_dlp

            if platform == 'android':
                from android.storage import primary_external_storage_path
                download_dir = os.path.join(primary_external_storage_path(), 'Download')
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir, exist_ok=True)
            else:
                download_dir = os.path.expanduser('~/Downloads')

            ydl_opts = {
                'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                'logger': MyLogger(),
                'quiet': True,
                'no_warnings': True,
                'noprogress': True,
                'progress_hooks': [self.progress_hook]
            }

            # Pre-merged format selection logic (Eliminates FFmpeg requirements)
            q_choice = self.quality_spinner.text
            if "1080p" in q_choice:
                # Downloads best single file (usually 720p pre-merged)
                ydl_opts['format'] = 'best[height<=1080]/best'
            elif "480p" in q_choice:
                # Downloads best single file <= 480p (typically 360p pre-merged)
                ydl_opts['format'] = 'best[height<=480]/best'
            elif "Audio Only" in q_choice:
                # Downloads best single audio file (m4a/webm - no merging needed)
                ydl_opts['format'] = 'bestaudio/best'
            else:
                # Default 720p (best pre-merged single file)
                ydl_opts['format'] = 'best[height<=720]/best'

            if self.sub_checkbox.active:
                ydl_opts['writesubtitles'] = True
                ydl_opts['writeautomaticsub'] = True
                ydl_opts['subtitleslangs'] = ['en', 'hi']

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.update_status("Status: Download Completed!")
        except Exception as e:
            self.update_status(f"Status: Error - {str(e)}")
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr

    def open_downloads_folder(self, instance):
        if platform == 'android':
            try:
                from jnius import autoclass
                DownloadManager = autoclass('android.app.DownloadManager')
                Intent = autoclass('android.content.Intent')
                intent = Intent(DownloadManager.ACTION_VIEW_DOWNLOADS)
                intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                current_activity = PythonActivity.mActivity
                current_activity.startActivity(intent)
            except Exception as e:
                self.update_status(f"Status: Cannot open folder - {str(e)}")
        else:
            try:
                import subprocess
                download_dir = os.path.expanduser('~/Downloads')
                if sys.platform == 'win32':
                    os.startfile(download_dir)
                elif sys.platform == 'darwin':
                    subprocess.Popen(['open', download_dir])
                else:
                    subprocess.Popen(['xdg-open', download_dir])
            except Exception as e:
                self.update_status(f"Status: Cannot open folder - {str(e)}")

if __name__ == '__main__':
    DownloaderApp().run()
