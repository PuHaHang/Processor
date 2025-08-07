#!/bin/bash
set -e

# YT_DLP_PATH=$(which yt-dlp)
# echo "YT_DLP_PATH: $YT_DLP_PATH"

# curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o yt-dlp
# chmod +x yt-dlp
# mv ./yt-dlp $YT_DLP_PATH

pip uninstall yt-dlp
pip install --upgrade pip -y
pip install yt-dlp -y

# aws s3 cp s3://recipe-it-s3/keys/cookies.txt /tmp/cookies.txt

# yt-dlp --add-header "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" \
#   --add-header "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp" \
#   --add-header "Accept-Language: en-US,en;q=0.9" \
#   --add-header "Referer: https://www.youtube.com/" \
#   --geo-bypass \
#   --no-check-certificate \
#   --cookies /tmp/cookies.txt \
#   "https://youtube.com/shorts/z4K1xfOZ06o?si=9poYTpngskv-fAFt"

exec python main.py