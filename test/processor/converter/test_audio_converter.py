"""
오디오 변환기 테스트 모듈

이 모듈은 AudioConverter 클래스의 기능을 검증하는 단위 테스트를 제공합니다.
Mock을 사용하여 실제 오디오 파일 없이도 테스트가 가능하도록 구현되었습니다.
"""

from textwrap import indent
import pytest
from unittest.mock import MagicMock, Mock, patch
import io

from src.processor.converter.audio_converter import AudioConverter
from src.processor.data_type import DataType
from src.processor.data_structure.buffer_dto import BufferDto
from src.processor.data_structure.buffer_status import BufferStatus
from src.processor.processor_type import ProcessorType


class TestAudioConverter:
    """
    AudioConverter 클래스에 대한 테스트 모음
    
    오디오 변환기의 초기화, 지원 여부 확인, 변환 처리 등의
    모든 기능을 테스트합니다.
    """
    
    @pytest.fixture
    def converter(self):
        """
        테스트용 AudioConverter 인스턴스를 제공하는 fixture
        
        Returns:
            AudioConverter: 테스트용 변환기 인스턴스
        """
        return AudioConverter()
    

    @pytest.fixture
    def audio_buffer(self, request):
        """
        유효한 오디오 BufferDto를 제공하는 fixture
        
        Args:
            request: 테스트 파라미터
            - param[0]: 테스트 파일 경로
            - param[1]: 테스트 파일 확장자
        Returns:
            BufferDto: 테스트용 오디오 버퍼 데이터
        """
        src, ext = request.param
        return BufferDto(
            buffer=open(f"test/resources/{src}", "rb").read(),
            metadata={"ext": ext},
            data_type=DataType.AUDIO,
            status=BufferStatus.INIT
        )

    
    def test_init(self, converter):
        """
        AudioConverter 초기화 테스트
        
        Args:
            converter: AudioConverter 인스턴스
        """
        assert converter.data_flow == (DataType.AUDIO, DataType.AUDIO)
        assert "webm" in converter.available_input_ext
        assert "mp3" in converter.available_output_ext
        assert converter.default_output_ext == "mp3"


    @pytest.mark.parametrize("audio_buffer", [
        ("test.webm", "webm"),
        ("test.mp3", "mp3"),
        # ("test.wav", "wav"), # 용량 문제로 테스트 중단
    ], indirect=["audio_buffer"])
    @pytest.mark.integration
    def test_is_supported_with_valid_audio(self, converter, audio_buffer):
        """
        유효한 오디오 데이터에 대한 지원 여부 테스트
        
        Args:
            converter: AudioConverter 인스턴스
            valid_audio_buffer: 유효한 오디오 버퍼
        """
        assert converter.is_supported(audio_buffer) == True


    @pytest.mark.integration
    def test_is_supported_with_invalid_data_type(self, converter):
        """
        잘못된 데이터 타입에 대한 지원 여부 테스트
        
        Args:
            converter: AudioConverter 인스턴스
        """
        invalid_buffer = BufferDto(
            buffer=b"invalid_data",
            metadata={},
            data_type=DataType.URL,
            status=BufferStatus.INIT
        )
        assert converter.is_supported(invalid_buffer) == False

    
    @pytest.mark.integration
    def test_is_supported_with_unsupported_extension(self, converter):
        """
        지원하지 않는 확장자에 대한 지원 여부 테스트
        
        Args:
            converter: AudioConverter 인스턴스
        """
        unsupported_buffer = BufferDto(
            buffer=b"audio_data",
            metadata={"ext": "unsupported"},
            data_type=DataType.AUDIO,
            status=BufferStatus.INIT
        )
        assert converter.is_supported(unsupported_buffer) == False

    
    @pytest.mark.parametrize("audio_buffer, dest_ext", [
        (("test.webm", "webm"), "mp3"),
        (("test.mp3", "mp3"), "wav"),
        # (("test.wav", "wav"), "mp3"), # 용량 문제로 테스트 중단
    ], indirect=["audio_buffer"])
    @pytest.mark.integration
    def test_process_success(self, converter, audio_buffer, dest_ext):
        """
        성공적인 오디오 변환 처리 테스트
        
        Args:
            converter: AudioConverter 인스턴스
            audio_buffer: 유효한 오디오 버퍼
        """
        result = converter.process(audio_buffer, {"ext": dest_ext})
        
        # 검증
        assert result.data_type == DataType.AUDIO
        assert result.status == BufferStatus.COMPLETED
        assert result.metadata["ext"] == dest_ext
        assert len(result.buffer) > 0  # 변환된 데이터가 존재하는지 확인


    @pytest.mark.parametrize("audio_buffer", [
        ("test.webm", "webm"),
        ("test.mp3", "mp3"),
        # ("test.wav", "wav"), # 용량 문제로 테스트 중단
    ], indirect=["audio_buffer"])
    @pytest.mark.integration
    def test_process_invalid_output_extension(self, converter, audio_buffer):
        """
        잘못된 출력 확장자로 처리 시 예외 테스트
        
        Args:
            converter: AudioConverter 인스턴스
            audio_buffer: 유효한 오디오 버퍼
        """
        with pytest.raises(ValueError) as exc_info:
            converter.process(audio_buffer, {"ext": "invalid"})
        
        assert "Invalid input or output extension" in str(exc_info.value)

    
    @pytest.mark.parametrize("audio_buffer", [
        ("test.webm", "webm"),
        ("test.mp3", "mp3"),
        # ("test.wav", "wav"), # 용량 문제로 테스트 중단
    ], indirect=["audio_buffer"])
    @patch('src.processor.converter.audio_converter.AudioSegment')
    @pytest.mark.integration
    def test_process_conversion_failure(self, mock_audio_segment, converter, audio_buffer):
        """
        오디오 변환 실패 시 예외 처리 테스트
        
        Args:
            mock_audio_segment: AudioSegment Mock 객체
            converter: AudioConverter 인스턴스
            audio_buffer: 유효한 오디오 버퍼
        """
        # AudioSegment Mock 설정 - 예외 발생
        mock_audio_segment.from_file.side_effect = Exception("Audio conversion failed")
        
        with pytest.raises(Exception) as exc_info:
            converter.process(audio_buffer, {"ext": "mp3"})
        
        assert "Audio conversion failed" in str(exc_info.value)

    
    def test_convert_audio_missing_parameters(self, converter):
        """
        필수 매개변수 누락 시 예외 테스트
        
        Args:
            converter: AudioConverter 인스턴스
        """
        with pytest.raises(ValueError) as exc_info:
            converter._convert_audio(b"audio_data", {})
        
        assert "Invalid input or output extension" in str(exc_info.value)


    def test_get_processor_type(self, converter):
        """
        프로세서 타입 반환 테스트
        
        Args:
            converter: AudioConverter 인스턴스
        """
        assert converter.get_processor_type() == ProcessorType.CONVERTER


    def test_get_data_flow(self, converter):
        """
        데이터 플로우 반환 테스트
        
        Args:
            converter: AudioConverter 인스턴스
        """
        expected_flow = (DataType.AUDIO, DataType.AUDIO)
        assert converter.get_data_flow() == expected_flow

    
    def test_get_available_input_ext(self, converter):
        """
        입력 확장자 목록 반환 테스트
        
        Args:
            converter: AudioConverter 인스턴스
        """
        input_exts = converter.get_available_input_ext()
        assert "webm" in input_exts
        assert "mp3" in input_exts
        assert "m4a" in input_exts


    def test_get_available_output_ext(self, converter):
        """
        출력 확장자 목록 반환 테스트
        
        Args:
            converter: AudioConverter 인스턴스
        """
        output_exts = converter.get_available_output_ext()
        assert "mp3" in output_exts
        assert "webm" in output_exts
        assert "wav" in output_exts

    
    def test_get_default_output_ext(self, converter):
        """
        기본 출력 확장자 반환 테스트
        
        Args:
            converter: AudioConverter 인스턴스
        """
        assert converter.get_default_output_ext() == "mp3"
