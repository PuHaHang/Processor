"""
오디오 변환기 테스트 모듈

이 모듈은 AudioConverter 클래스의 기능을 검証하는 단위 테스트를 제공합니다.
Mock을 사용하여 실제 오디오 파일 없이도 테스트가 가능하도록 구현되었습니다.
"""

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
    def valid_audio_buffer(self):
        """
        유효한 오디오 BufferDto를 제공하는 fixture
        
        Returns:
            BufferDto: 테스트용 오디오 버퍼 데이터
        """
        return BufferDto(
            buffer=b"mock_audio_data",
            metadata={"ext": "webm"},
            data_type=DataType.AUDIO,
            status=BufferStatus.INIT
        )
    

    @pytest.fixture
    def invalid_buffer(self):
        """
        잘못된 타입의 BufferDto를 제공하는 fixture
        
        Returns:
            BufferDto: 테스트용 잘못된 버퍼 데이터
        """
        return BufferDto(
            buffer=b"invalid_data",
            metadata={},
            data_type=DataType.URL,
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


    def test_is_supported_with_valid_audio(self, converter, valid_audio_buffer):
        """
        유효한 오디오 데이터에 대한 지원 여부 테스트
        
        Args:
            converter: AudioConverter 인스턴스
            valid_audio_buffer: 유효한 오디오 버퍼
        """
        assert converter.is_supported(valid_audio_buffer) == True


    def test_is_supported_with_invalid_data_type(self, converter, invalid_buffer):
        """
        잘못된 데이터 타입에 대한 지원 여부 테스트
        
        Args:
            converter: AudioConverter 인스턴스
            invalid_buffer: 잘못된 버퍼 데이터
        """
        assert converter.is_supported(invalid_buffer) == False

    
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

    
    def test_process_success(self, converter, valid_audio_buffer):
        """
        성공적인 오디오 변환 처리 테스트
        
        Args:
            converter: AudioConverter 인스턴스
            valid_audio_buffer: 유효한 오디오 버퍼
        """
        import os
        
        # test/resources 디렉토리의 test.webm 파일 사용
        test_webm_path = "test/resources/test.webm"
        test_wav_path = "test/resources/test.wav"
        
        # test.webm 파일이 존재하는지 확인
        assert os.path.exists(test_webm_path), f"테스트 파일이 존재하지 않습니다: {test_webm_path}"
        
        # 실제 오디오 데이터로 BufferDto 생성
        with open(test_webm_path, 'rb') as f:
            audio_data = f.read()
        
        test_buffer = BufferDto(
            buffer=audio_data,
            metadata={"ext": "webm"},
            data_type=DataType.AUDIO,
            status=BufferStatus.INIT
        )
        
        result = converter.process(test_buffer, {"ext": "wav"})
        
        # 검증
        assert result.data_type == DataType.AUDIO
        assert result.status == BufferStatus.COMPLETED
        assert result.metadata["ext"] == "wav"
        assert len(result.buffer) > 0  # 변환된 데이터가 존재하는지 확인
        
        # 변환된 데이터를 test.wav와 비교 (선택적)
        if os.path.exists(test_wav_path):
            with open(test_wav_path, 'rb') as f:
                expected_wav_data = f.read()
            # 변환된 데이터가 유효한 WAV 형식인지 확인
            assert result.buffer.startswith(b'RIFF'), "변환된 데이터가 유효한 WAV 형식이 아닙니다"


    def test_process_invalid_output_extension(self, converter, valid_audio_buffer):
        """
        잘못된 출력 확장자로 처리 시 예외 테스트
        
        Args:
            converter: AudioConverter 인스턴스
            valid_audio_buffer: 유효한 오디오 버퍼
        """
        with pytest.raises(ValueError) as exc_info:
            converter.process(valid_audio_buffer, {"ext": "invalid"})
        
        assert "Invalid output extension" in str(exc_info.value)

    
    @patch('src.processor.converter.audio_converter.AudioSegment')
    def test_process_conversion_failure(self, mock_audio_segment, converter, valid_audio_buffer):
        """
        오디오 변환 실패 시 예외 처리 테스트
        
        Args:
            mock_audio_segment: AudioSegment Mock 객체
            converter: AudioConverter 인스턴스
            valid_audio_buffer: 유효한 오디오 버퍼
        """
        # AudioSegment Mock 설정 - 예외 발생
        mock_audio_segment.from_file.side_effect = Exception("Audio conversion failed")
        
        with pytest.raises(Exception) as exc_info:
            converter.process(valid_audio_buffer, {"ext": "mp3"})
        
        assert "Audio conversion failed" in str(exc_info.value)

    
    def test_convert_audio_missing_parameters(self, converter):
        """
        필수 매개변수 누락 시 예외 테스트
        
        Args:
            converter: AudioConverter 인스턴스
        """
        with pytest.raises(ValueError) as exc_info:
            converter._convert_audio(b"audio_data", {})
        
        assert "src_ext and dest_ext are required" in str(exc_info.value)


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


    def test_extract_audio_extension(self, converter):
        """
        오디오 확장자 추출 테스트
        
        Args:
            converter: AudioConverter 인스턴스
        """
        metadata = {"ext": "webm", "other": "data"}
        result = converter._extract_audio_extension(metadata)
        assert result == "webm"

    
    def test_extract_audio_extension_missing(self, converter):
        """
        확장자가 없는 메타데이터에서 확장자 추출 테스트
        
        Args:
            converter: AudioConverter 인스턴스
        """
        metadata = {"other": "data"}
        result = converter._extract_audio_extension(metadata)
        assert result == ""
