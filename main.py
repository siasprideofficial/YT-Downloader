import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform

import yt_dlp

class DownloaderApp(App):
    def build(self):
        self.title = "YT-DLP Android Downloader"
        
        # Main Layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Header Label
        self.label = Label(
            text="Video URL Paste Karein:", 
            size_hint_y=None, 
            height=40,
            font_size=18
        )
        layout.add_widget(self.label)
        
        # URL Input Box
        self.url_input = TextInput(
            hint_text="https://...", 
            multiline=False, 
            size_hint_y=None, 
            height=50
        )
        layout.add_widget(self.url_input)
        
        # Download Button
        self.download_btn = Button(
            text="Download Video", 
            size_hint_y=None, 
            height=50,
            background_color=(0.1, 0.6, 0.8, 1)
        )
        self.download_btn.bind(on_press=self.start_download_thread)
        layout.add_widget(self.download_btn)
        
        # Status Label
        self.status_label = Label(text="Status: Ready", size_hint_y=None, height=40)
        layout.add_widget(self.status_label)
        
        return layout

    def start_download_thread(self, instance):
        # UI freeze na ho, isliye download background thread mein chalega
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = "Status: Please enter a valid URL"
            return
            
        self.status_label.text = "Status: Downloading..."
        threading.Thread(target=self.download_video, args=(url,)).start()

    def download_video(self, url):
        # Android par files save karne ki default directory select karna
        if platform == 'android':
            from android.storage import primary_external_storage_path
            # Downloads folder ka path
            download_dir = os.path.join(primary_external_storage_path(), 'Download')
        else:
            download_dir = os.path.expanduser('~/Downloads')

        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.status_label.text = "Status: Download Completed!"
        except Exception as e:
            self.status_label.text = f"Status: Error - {str(e)}"

if __name__ == '__main__':
    DownloaderApp().run()
