"""
Logging Configuration

로깅 설정 및 관리
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console


def setup_logger(
    name: str = "meeting_summary",
    level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    로거 설정
    
    Args:
        name: 로거 이름
        level: 로그 레벨
        log_file: 로그 파일 경로 (None이면 파일 로깅 안함)
        console_output: 콘솔 출력 여부
    
    Returns:
        설정된 로거
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 기존 핸들러 제거
    logger.handlers.clear()
    
    # 포맷터 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 콘솔 핸들러 (Rich 사용)
    if console_output:
        console = Console()
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            rich_tracebacks=True
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 파일 핸들러
    if log_file:
        # 로그 디렉토리 생성
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "meeting_summary") -> logging.Logger:
    """기존 로거 반환"""
    return logging.getLogger(name)


class LoggerMixin:
    """로깅 기능을 제공하는 믹스인 클래스"""
    
    @property
    def logger(self) -> logging.Logger:
        """클래스별 로거 반환"""
        class_name = self.__class__.__name__
        return get_logger(f"meeting_summary.{class_name}")
    
    def log_info(self, message: str) -> None:
        """정보 로그"""
        self.logger.info(message)
    
    def log_warning(self, message: str) -> None:
        """경고 로그"""
        self.logger.warning(message)
    
    def log_error(self, message: str) -> None:
        """에러 로그"""
        self.logger.error(message)
    
    def log_debug(self, message: str) -> None:
        """디버그 로그"""
        self.logger.debug(message)
