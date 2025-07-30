import os
import boto3
import logfire
from botocore.exceptions import BotoCoreError, ClientError


def upload_image_to_s3(image, key: str, bucket: str) -> str:
    """
    이미지를 S3에 업로드하고, S3 URL을 반환합니다.

    Args:
        image: PIL.Image 객체
        key (str): S3에 저장될 파일 경로 및 이름
        bucket (str): S3 버킷명

    Returns:
        str: 업로드된 이미지의 S3 URL

    Raises:
        Exception: 업로드 실패 시 예외 발생
    """
    import io

    # 이미지 객체를 바이트 스트림으로 변환
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_REGION')
    )

    try:
        logfire.info('S3 이미지 업로드 시작 {bucket}/{key}', bucket=bucket, key=key)
        s3_client.upload_fileobj(
            img_byte_arr,
            bucket,
            key,
            ExtraArgs={'ContentType': 'image/png', 'ACL': 'public-read'}
        )
        s3_url = f"https://{bucket}.s3.{os.environ.get('AWS_REGION')}.amazonaws.com/{key}"
        logfire.info('S3 이미지 업로드 성공 {s3_url}', s3_url=s3_url)
        return s3_url
    except (BotoCoreError, ClientError) as e:
        logfire.error('S3 이미지 업로드 실패 {error}, bucket: {bucket}, key: {key}', error=str(e), bucket=bucket, key=key)
        raise
