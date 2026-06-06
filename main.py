import os
import sys
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout # Centering ke liye
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
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
        self.title = "YT-DLP Android Downloader"
        
        # 1. Root Layout: Jo poore content ko screen ke center mein rakhega
        main_layout = AnchorLayout(anchor_x='center', anchor_y='center', padding=30)
        
        # 2. Content Layout: Isme humare saare widgets honge (Width responsive hai 95%)
        content_layout = BoxLayout(
            orientation='vertical', 
            spacing=15, 
            size_hint=(0.95, None)
        )
        # Content layout ki height automatic widgets ke height ke sum ke barabar set hogi
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Title Label (Modern Blue highlight)
        self.label = Label(
            text="YT-DLP Downloader", 
            font_size='22sp', 
            bold=True,
            size_hint_y=None, 
            height=50,
            color=(0.12, 0.53, 0.9, 1) # Royal Blue
        )
        content_layout.add_widget(self.label)
        
        # Text Input (Dark theme and padded input)
        self.url_input = TextInput(
            hint_text="Video URL yahan paste karein...", 
            multiline=False, 
            size_hint_y=None, 
            height=55,
            font_size='16sp',
            padding=[15, 15, 15, 15], # Text ko box ke border se door rakhne ke liye
            background_color=(0.15, 0.15, 0.15, 1), # Dark Background
            foreground_color=(1, 1, 1, 1), # White Text
            hint_text_color=(0.5, 0.5, 0.5, 1),
            cursor_color=(0.12, 0.53, 0.9, 1)
        )
        content_layout.add_widget(self.url_input)
        
        # Download Button (Flat modern blue button)
        self.download_btn = Button(
            text="DOWNLOAD VIDEO", 
            size_hint_y=None, 
            height=55,
            font_size='18sp',
            bold=True,
            background_normal='', # Default gray shading hatane ke liye
            background_color=(0.12, 0.53, 0.9, 1) # Royal Blue
        )
        self.download_btn.bind(on_press=self.start_download_thread)
        content_layout.add_widget(self.download_btn)
        
        # Status Label (Centered multi-line status text)
        self.status_label = Label(
            text="Status: Ready to Download", 
            size_hint_y=None, 
            height=80,
            font_size='15sp',
            halign="center",
            valign="middle",
            color=(0.7, 0.7, 0.7, 1)
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        content_layout.add_widget(self.status_label)
        
        # Content box ko Main center-aligned layout mein add kiya
        main_layout.add_widget(content_layout)
        
        return main_layout

    @mainthread
    def update_status(self, text):
        self.status_label.text = text

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0.0%').strip()
            speed = d.get('_speed_str', 'N/A').strip()
            eta = d.get('_eta_str', 'N/A').strip()
            self.update_status(f"Progress: {percent}\nSpeed: {speed} | ETA: {eta}")
        elif d['status'] == 'finished':
            self.update_status("Status: Processing / Saving video...")

    def start_download_thread(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.update_status("Status: Please enter a valid URL")
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
                'format': 'best',
                'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                'logger': MyLogger(),
                'quiet': True,
                'no_warnings': True,
                'noprogress': True,
                'progress_hooks': [self.progress_hook]
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.update_status("Status: Download Completed!")
        except Exception as e:
            self.update_status(f"Status: Error - {str(e)}")
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr

if __name__ == '__main__':
    DownloaderApp().run()
