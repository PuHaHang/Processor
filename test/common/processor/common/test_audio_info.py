# """
# 오디오 정보 추출 테스트 모듈

# 이 모듈은 audio_info 모듈의 기능을 검증하는 단위 테스트를 제공합니다.
# ffprobe를 사용한 실제 오디오 파일 분석과 Mock을 사용한 테스트를 모두 포함합니다.
# """

# import ffmpeg
# import pytest
# import os
# import tempfile
# from unittest.mock import Mock, patch, MagicMock
# import subprocess

# from src.common.processor.common import (
#     get_ffmpeg_format,
#     get_ffmpeg_extension,
#     get_ffmpeg_duration,
#     get_ffmpeg_info,
# )


# class TestAudioInfo:
#     """
#     audio_info 모듈에 대한 테스트 모음
    
#     오디오 형식 감지, 메타데이터 추출, ffprobe 연동 등의
#     모든 기능을 테스트합니다.
#     """
    
#     @pytest.fixture
#     def mock_run(self):
#         """
#         subprocess.run Mock 객체를 생성하는 fixture
#         """
#         return Mock()


#     @pytest.fixture
#     def sample_audio_data(self):
#         """
#         테스트용 오디오 데이터를 제공하는 fixture
        
#         Returns:
#             bytes: 테스트용 오디오 바이너리 데이터
#         """
#         # 간단한 WAV 헤더 (44.1kHz, 16bit, 모노)
#         wav_header = (
#             b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00'
#             b'\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
#         )
#         return wav_header
    
    
#     @pytest.fixture
#     def temp_audio_file(self, sample_audio_data):
#         """
#         임시 오디오 파일을 생성하는 fixture
        
#         Args:
#             sample_audio_data: 테스트용 오디오 데이터
            
#         Yields:
#             str: 임시 파일 경로
#         """
#         with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
#             temp_file.write(sample_audio_data)
#             temp_file_path = temp_file.name
        
#         yield temp_file_path
        
#         # 테스트 후 파일 정리
#         if os.path.exists(temp_file_path):
#             os.unlink(temp_file_path)
    
    
#     @pytest.mark.parametrize("target, expected", [
#         ("test.mp3", "mp3"),
#         ("test.webm", "matroska,webm"),
#         # ("test.wav", "wav"), # 용량 문제로 테스트 중단
#     ])
#     @pytest.mark.integration
#     def test_get_audio_format_success(self, target, expected):
#         """
#         MP3 형식 감지 테스트
#         """
#         # MP3 시그니처 (ID3v2)
#         with open(f"test/resources/mockdata/{target}", "rb") as f:
#             data = f.read()
#         format_name = get_ffmpeg_format(data)
#         assert format_name == expected
    
    
#     # 용량 문제로 테스트 중단
#     # def test_get_audio_extension_wav(self, sample_audio_data):
#     #     """
#     #     WAV 확장자 추출 테스트
        
#     #     Args:
#     #         sample_audio_data: 테스트용 오디오 데이터
#     #     """
#     #     extension = audio_info.get_audio_extension(sample_audio_data)
#     #     assert extension == "wav"
    
    
#     @pytest.mark.parametrize("target, expected", [
#         ("test.mp3", "mp3"),
#         ("test.webm", "webm"),
#         # ("test.wav", "wav"), # 용량 문제로 테스트 중단
#     ])
#     @pytest.mark.integration
#     def test_get_audio_extension_success(self, target, expected):
#         """
#         MP3 확장자 추출 테스트
#         """
#         with open(f"test/resources/mockdata/{target}", "rb") as f:
#             data = f.read()
#         extension = get_ffmpeg_extension(data)
#         assert extension == expected
    

#     @pytest.mark.integration
#     def test_get_audio_extension_failed(self):
#         """
#         유효하지 않은 파일에 대한 확장자 추출 테스트
        
#         Args:
#             temp_audio_file: 임시 오디오 파일 경로
#         """
#         with pytest.raises(ffmpeg.Error) as exc_info:
#             get_ffmpeg_extension(b"test.txt")
#         assert exc_info.type == ffmpeg.Error
    
    
#     @patch('subprocess.run')
#     @pytest.mark.unit
#     def test_get_audio_metadata_ffprobe_failure(self, mock_run):
#         """
#         ffprobe 실행 실패 시 예외 처리 테스트
        
#         Args:
#             mock_run: subprocess.run Mock 객체
#         """
#         # Mock 설정 - ffprobe 실패
#         mock_result = Mock()
#         mock_result.returncode = 1
#         mock_result.stderr = "ffprobe error: Invalid data found"
#         mock_run.return_value = mock_result
        
#         with pytest.raises(Exception) as exc_info:
#             get_ffmpeg_info(b"test.wav")
        
#         assert "ffprobe error" in str(exc_info.value)
    
    
#     @pytest.mark.parametrize("target, expected", [
#         ("test.mp3", 470.688),
#         ("test.webm", 470.661),
#         # ("test.wav", 15.25), # 용량 문제로 테스트 중단
#     ])
#     @pytest.mark.integration
#     def test_get_audio_duration_success(self, target, expected):
#         """
#         오디오 파일 길이 추출 성공 테스트
        
#         Args:
#             temp_audio_file: 임시 오디오 파일 경로
#         """
#         with open(f"test/resources/mockdata/{target}", "rb") as f:
#             data = f.read()
#         duration = get_ffmpeg_duration(data)
#         assert duration == expected
