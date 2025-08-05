#!/bin/bash
set -e

# curl -I -s -c /tmp/cookies.txt -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" "https://www.youtube.com"
pip install -U --pre "yt-dlp[default]"
yt-dlp "https://youtube.com/shorts/z4K1xfOZ06o?si=9poYTpngskv-fAFt"

exec python main.py