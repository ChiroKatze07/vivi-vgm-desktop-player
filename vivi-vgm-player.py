"""
AUDIO / VIDEO von Vivi's 24/7 VGM Radio auf YouTube/viviwebsite.net
Quelle: https://www.youtube.com/watch?v=ZyAavTqsU6k / viviwebsite.net

Zeigt den aktuellen Track-Name, den Spieletitel sowie den Requester des Lieds an
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import vlc
import requests
from bs4 import BeautifulSoup
from yt_dlp import YoutubeDL

# === Konfiguration ===
YOUTUBE_URL = "https://www.youtube.com/watch?v=ZyAavTqsU6k"  # Vivi Livestream
VIVI_URL = "https://viviwebsite.net"

class ViviRadioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vivi Radio Player")
        self.root.geometry("370x180")

        self.track_var = tk.StringVar(value="ViviVGM Radio Player…")
        self.requester_var = tk.StringVar(value="")
        self.game_var = tk.StringVar(value="")
        
        ttk.Label(root, textvariable=self.track_var, font=("Arial", 14, "bold")).pack(pady=5)
        ttk.Label(root, textvariable=self.game_var, font=("Arial", 12, "bold")).pack(pady=2)
        ttk.Label(root, textvariable=self.requester_var, font=("Arial", 11, "italic")).pack(pady=2)

        self.play_button = ttk.Button(root, text="▶ Play", command=self.toggle_play)
        self.play_button.pack(pady=10)

        # Frame für Checkbox + Lautstärke horizontal
        control_frame = ttk.Frame(root)
        control_frame.pack(side='bottom', pady=10, fill='x', padx=10)

        # Checkbox Video anzeigen
        self.video_var = tk.BooleanVar(value=False)
        self.video_checkbox = ttk.Checkbutton(control_frame, text="Video anzeigen", variable=self.video_var)
        self.video_checkbox.pack(side='left')

        # Lautstärkeregler
        self.volume_var = tk.DoubleVar(value=50)
        volume_label = ttk.Label(control_frame, text="Lautstärke")
        volume_label.pack(side='left', padx=(55,5))
        volume_slider = ttk.Scale(control_frame, from_=0, to=100, orient='horizontal', variable=self.volume_var, command=self.set_volume, length=125)
        volume_slider.pack(side='left')

        self.player = None
        self.vlc_instance = None
        self.is_playing = False

        # Track-Info Updater als Thread starten
        threading.Thread(target=self.update_track_info, daemon=True).start()

    def get_audio_url(self):
        """Holt direkte Audio-URL von YouTube."""
        opts = {'format': 'bestaudio/best', 'quiet': True, 'skip_download': True}
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(YOUTUBE_URL, download=False)
            return info['url'] if 'url' in info else None

    def toggle_play(self):
        if not self.is_playing:
            audio_url = self.get_audio_url()
            if not audio_url:
                self.track_var.set("Fehler: Keine Audio-URL gefunden.")
                return

            # VLC-Instanz: Video optional
            opts = [] if self.video_var.get() else ['--no-video']
            self.vlc_instance = vlc.Instance(*opts)
            self.player = self.vlc_instance.media_player_new()
            media = self.vlc_instance.media_new(audio_url)
            self.player.set_media(media)
            self.player.audio_set_volume(int(self.volume_var.get()))
            self.player.play()
            self.play_button.config(text="⏸ Pause")
            self.is_playing = True
        else:
            if self.player:
                self.player.stop()
            self.play_button.config(text="▶ Play")
            self.is_playing = False

    def set_volume(self, val):
        if self.player:
            self.player.audio_set_volume(int(float(val)))

    def update_track_info(self):
        """Fragt alle 15s die aktuelle Trackinfo von Vivi ab."""
        while True:
            try:
                r = requests.get(VIVI_URL, timeout=10)
                soup = BeautifulSoup(r.text, "html.parser")

                # Song-Titel
                np_header = soup.select_one("tr.song td div.title")
                if np_header:
                    self.track_var.set(f"♫ {np_header.get_text(strip=True)}")

                # Song-Spiel
                np_game = soup.select_one("tr.song td div.album")
                if np_game:
                    self.game_var.set(f"{np_game.get_text(strip=True)}")

                # Song-Requester (nicht immer vorhanden)
                np_req = soup.select_one("tr.song td i")
                if np_req:
                    reqtext = "Requested by: " + np_req.get_text(strip=True)
                    self.requester_var.set(f"{reqtext}")
                else:
                    self.requester_var.set("")

            except Exception:
                self.track_var.set("Track-Info konnte nicht geladen werden")
                self.requester_var.set("")
            time.sleep(15)

if __name__ == "__main__":
    root = tk.Tk()
    app = ViviRadioApp(root)
    root.mainloop()