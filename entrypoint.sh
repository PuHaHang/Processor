#!/bin/bash
set -e

aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID --profile default
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY --profile default
aws configure set region $AWS_REGION --profile default

aws s3 cp s3://$AWS_S3_BUCKET_NAME/$COOKIES_S3_PATH cookies.txt --region $AWS_REGION --profile default
yt-dlp --cookies cookies.txt "https://youtube.com/shorts/z4K1xfOZ06o?si=9poYTpngskv-fAFt"

exec python main.py