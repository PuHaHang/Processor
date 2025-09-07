import os
import re
from typing import Tuple

import logfire

from src.common.exception.custom_exceptions import ValidationException
from src.common.processor.formatter.formatter import Formatter
from src.common.processor.types.payload_status import PayloadStatus
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter, TextFormatter
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.common.processor.transcriber.transcriber_strategy import TranscriberStrategy
from src.common.processor.types.data_type import DataType
from src.common.processor.types.payload import Payload


YOUTUBE = build("youtube", "v3", developerKey=str(os.getenv("YOUTUBE_API_KEY")))

class YoutubeTranscriber(TranscriberStrategy):
    data_flow: Tuple[DataType, DataType] = (DataType.URL, DataType.TEXT)

    YOUTUBE_URL_PATTERN = re.compile(
        r"""^
        (?:https?://)?                # 프로토콜 (선택)
        (?:www\.|m\.)?                # www. 또는 m. (선택)
        (?:
            (?:youtube\.com/          # youtube.com/
                (?:
                    watch\?           # watch? (쿼리)
                    (?:.*&)?v=        # v= 파라미터 (중간에 다른 파라미터 허용)
                    (?P<id1>[a-zA-Z0-9_-]{11}) # 비디오 ID
                    (?:[&#].*)?       # 추가 파라미터 (선택)
                |
                    (?:embed|v|shorts)/ # embed/, v/, shorts/
                    (?P<id2>[a-zA-Z0-9_-]{11}) # 비디오 ID
                    (?:[/?&#].*)?     # 추가 파라미터 (선택)
                )
            )
        |
            youtu\.be/                # youtu.be/
            (?P<id3>[a-zA-Z0-9_-]{11}) # 비디오 ID
            (?:[/?&#].*)?             # 추가 파라미터 (선택)
        )
        $""",
        re.IGNORECASE | re.VERBOSE
    )

    def process(self, payload: Payload, opt: dict = {}) -> Payload:
        formatter = Formatter()

        buffer_data = payload.get_buffer().decode('utf-8')

        # URL에서 비디오 ID와 플랫폼 추출
        reference = formatter.parse(buffer_data)
        if not reference:
            raise ValidationException(
                message="유효하지 않은 YouTube URL 형식입니다",
                field_name="url",
                field_value=buffer_data,
                validation_rule="youtube_url_valid_format"
            )
        
        video_id = reference["url"].split('v=')[-1]

        transcript = YouTubeTranscriptApi().fetch(video_id, languages=['ko', 'en', 'ja'])
        srt_formatter = SRTFormatter()
        srt_formatted = srt_formatter.format_transcript(transcript)
        logfire.info('YoutubeTranscriber 처리 완료 {video_id}', video_id=video_id)
        return Payload(
            buffer=srt_formatted.encode('utf-8'),
            metadata={
                **self._get_video_author(video_id),
                "reference": reference,
            },
            data_type=DataType.TEXT,
            status=PayloadStatus.COMPLETED,
            processor=self
        )
    
    def is_supported(self, payload: Payload) -> bool:
        return self.YOUTUBE_URL_PATTERN.match(payload.get_buffer().decode('utf-8')) is not None

    def _get_video_author(self, video_id: str):
        resp = YOUTUBE.videos().list(
            part="snippet",
            id=video_id,
            # 쿼터 절약: 필요한 필드만
            fields="items(id,snippet(channelId,channelTitle,publishedAt,title))",
        ).execute()
        items = resp.get("items", [])
        if not items:
            raise ValueError(f"Video not found: {video_id}")
        it = items[0]
        sn = it["snippet"]
        return {
            "id": it["id"],
            "title": sn["title"],
            "upload_date": sn["publishedAt"],
            "uploader_id": sn["channelId"],
            "uploader": sn["channelTitle"],
        }