#!/bin/bash
set -e

curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o yt-dlp
chmod +x yt-dlp

./yt-dlp --add-header "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" \
  --add-header "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp" \
  --add-header "Accept-Language: en-US,en;q=0.9" \
  --add-header "Referer: https://www.youtube.com/" \
  "https://youtube.com/shorts/z4K1xfOZ06o?si=9poYTpngskv-fAFt"

exec python main.py