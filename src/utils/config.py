"""
Configuration Management

환경 변수 및 설정 관리
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class AudioConfig(BaseSettings):
    """오디오 녹음 설정"""
    sample_rate: int = Field(default=44100, description="샘플링 레이트")
    channels: int = Field(default=1, description="채널 수 (모노)")
    chunk_size: int = Field(default=1024, description="청크 크기")
    format: str = Field(default="pyaudio.paInt16", description="오디오 포맷")
    
    class Config:
        env_prefix = "AUDIO_"


class APIConfig(BaseSettings):
    """API 설정"""
    openai_api_key: str = Field(..., description="OpenAI API 키")
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI 모델")
    notion_api_key: str = Field(..., description="Notion API 키")
    notion_database_id: str = Field(..., description="Notion 데이터베이스 ID")
    
    class Config:
        env_prefix = ""


class PathConfig(BaseSettings):
    """파일 경로 설정"""
    data_dir: str = Field(default="./data", description="데이터 디렉토리")
    output_dir: str = Field(default="./output", description="출력 디렉토리")
    temp_dir: str = Field(default="./temp", description="임시 디렉토리")
    
    class Config:
        env_prefix = ""


class LoggingConfig(BaseSettings):
    """로깅 설정"""
    log_level: str = Field(default="INFO", description="로그 레벨")
    log_file: str = Field(default="meeting_summary.log", description="로그 파일명")
    
    class Config:
        env_prefix = "LOG_"


class MeetingConfig(BaseSettings):
    """회의 설정"""
    duration_minutes: int = Field(default=60, description="회의 시간 (분)")
    auto_stop_recording: bool = Field(default=True, description="자동 녹음 중지")
    
    class Config:
        env_prefix = "MEETING_"


class Config:
    """전체 설정 관리 클래스"""
    
    def __init__(self, env_file: Optional[str] = None):
        # .env 파일 로드
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        # 각 설정 섹션 초기화
        self.audio = AudioConfig()
        self.api = APIConfig()
        self.paths = PathConfig()
        self.logging = LoggingConfig()
        self.meeting = MeetingConfig()
        
        # 디렉토리 생성
        self._create_directories()
    
    def _create_directories(self) -> None:
        """필요한 디렉토리 생성"""
        directories = [
            self.paths.data_dir,
            self.paths.output_dir,
            self.paths.temp_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> bool:
        """설정 유효성 검사"""
        required_fields = [
            self.api.openai_api_key,
            self.api.notion_api_key,
            self.api.notion_database_id
        ]
        
        return all(field for field in required_fields)
    
    def get_audio_format(self):
        """PyAudio 포맷 반환"""
        import pyaudio
        return getattr(pyaudio, self.audio.format.split('.')[-1])
    
    def get_temp_file_path(self, filename: str) -> str:
        """임시 파일 경로 반환"""
        return os.path.join(self.paths.temp_dir, filename)
    
    def get_output_file_path(self, filename: str) -> str:
        """출력 파일 경로 반환"""
        return os.path.join(self.paths.output_dir, filename)
    
    def get_data_file_path(self, filename: str) -> str:
        """데이터 파일 경로 반환"""
        return os.path.join(self.paths.data_dir, filename)


# 전역 설정 인스턴스
config = Config()
