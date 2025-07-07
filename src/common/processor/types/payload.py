"""
버퍼 데이터 전송 객체 모듈

이 모듈은 프로세서 파이프라인에서 데이터를 전달하는 데 사용되는
버퍼 데이터 전송 객체(DTO)를 정의합니다.
"""

from pydantic import BaseModel

from . import DataType
from .payload_status import PayloadStatus

class Payload (BaseModel):
    """
    프로세서 간 데이터 전달을 위한 버퍼 데이터 전송 객체
    
    파이프라인의 각 프로세서 간에 데이터를 전달할 때 사용되는 표준 형식입니다.
    바이너리 데이터, 메타데이터, 데이터 타입, 처리 상태를 포함합니다.
    
    Attributes:
        buffer (bytes): 실제 데이터 (바이너리 형태)
        metadata (dict): 데이터와 관련된 메타데이터
        data_type (DataType): 데이터의 타입 (URL, AUDIO, TEXT 등)
        status (BufferStatus): 현재 처리 상태
    """
    buffer: bytes
    metadata: dict
    data_type: DataType
    status: PayloadStatus


    def get_buffer_string(self) -> str:
        """
        버퍼 데이터를 UTF-8 문자열로 디코딩하여 반환합니다.
        
        Returns:
            str: 디코딩된 문자열 데이터
        """
        return self.buffer.decode('utf-8')
    
    
    def get_buffer_bytes(self) -> bytes:
        """
        버퍼 데이터를 바이트 형태로 반환합니다.
        
        Returns:
            bytes: 바이너리 데이터
        """
        return self.buffer


    def get_buffer(self) -> bytes:
        """
        버퍼 데이터를 반환합니다.
        
        Returns:
            bytes: 바이너리 데이터
        """
        return self.buffer
    
    
    def get_metadata(self) -> dict:
        """
        메타데이터를 반환합니다.
        
        Returns:
            dict: 메타데이터 딕셔너리
        """
        return self.metadata
    
    
    def get_data_type(self) -> DataType:
        """
        데이터 타입을 반환합니다.
        
        Returns:
            DataType: 데이터 타입 열거형
        """
        return self.data_type
    
    
    def get_status(self) -> PayloadStatus:
        """
        현재 처리 상태를 반환합니다.
        
        Returns:
            BufferStatus: 처리 상태 열거형
        """
        return self.status
    
