#!/usr/bin/env python3
"""YouTube-Playlist-Downloader (Eigengebrauch) – dünner Wrapper um yt-dlp.

Beispiele:
  python playlist_dl.py "<playlist-url>"                 # Video (mp4)
  python playlist_dl.py "<playlist-url>" -a              # nur Audio (mp3)
  python playlist_dl.py "<playlist-url>" -q 720 -o ~/Videos
  python playlist_dl.py "<playlist-url>" --items 1-5     # nur Teil der Playlist
"""
import argparse
import sys
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    sys.exit("yt-dlp fehlt -> pip install -U yt-dlp  (und ffmpeg installiert haben)")


def build_opts(args: argparse.Namespace) -> dict:
    out = Path(args.output).expanduser()
    opts = {
        # Ordner pro Playlist, Dateien nummeriert in Playlist-Reihenfolge
        "outtmpl": str(out / "%(playlist_title)s" / "%(playlist_index)03d - %(title)s.%(ext)s"),
        "ignoreerrors": True,      # private/gelöschte Videos überspringen
        "download_archive": str(out / "archive.txt"),  # bereits geladene nicht nochmal
        "noplaylist": False,
        "retries": 10,
        "fragment_retries": 10,
        "concurrent_fragment_downloads": 4,
        "writethumbnail": args.thumbnails,
        "playlist_items": args.items,
    }
    if args.audio:
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"},
            {"key": "FFmpegMetadata"},
        ]
    else:
        opts["format"] = (
            f"bv*[height<={args.quality}]+ba/b[height<={args.quality}]"
            if args.quality
            else "bv*+ba/b"
        )
        opts["merge_output_format"] = "mp4"
        opts["postprocessors"] = [{"key": "FFmpegMetadata"}]
    return opts


def main() -> None:
    p = argparse.ArgumentParser(description="YouTube-Playlist downloaden")
    p.add_argument("url", help="Playlist-URL")
    p.add_argument("-o", "--output", default="downloads", help="Zielordner (default: ./downloads)")
    p.add_argument("-a", "--audio", action="store_true", help="nur Audio als mp3")
    p.add_argument("-q", "--quality", type=int, help="max. Videohöhe, z.B. 720 oder 1080")
    p.add_argument("--items", help="Teilbereich, z.B. 1-5 oder 1,3,7")
    p.add_argument("--thumbnails", action="store_true", help="Thumbnails mitspeichern")
    args = p.parse_args()

    with yt_dlp.YoutubeDL(build_opts(args)) as ydl:
        code = ydl.download([args.url])
    sys.exit(code)


if __name__ == "__main__":
    main()
