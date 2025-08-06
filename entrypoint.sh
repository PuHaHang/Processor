#!/bin/bash
set -e

curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o yt-dlp
chmod +x yt-dlp

./yt-dlp "https://youtube.com/shorts/z4K1xfOZ06o?si=9poYTpngskv-fAFt"

exec python main.py