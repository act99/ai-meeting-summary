"""
File Management Utilities

파일 관리 및 유틸리티 기능
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List, Union
from datetime import datetime
import uuid


class FileManager:
    """파일 관리 클래스"""
    
    def __init__(self, base_dir: str = "./data"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def create_temp_file(self, suffix: str = "", prefix: str = "temp_") -> str:
        """임시 파일 생성"""
        fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=self.base_dir)
        os.close(fd)
        return path
    
    def create_unique_filename(self, base_name: str, extension: str = "") -> str:
        """고유한 파일명 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        if extension and not extension.startswith('.'):
            extension = f".{extension}"
        
        filename = f"{base_name}_{timestamp}_{unique_id}{extension}"
        return str(self.base_dir / filename)
    
    def save_file(self, content: Union[str, bytes], filename: str) -> str:
        """파일 저장"""
        file_path = self.base_dir / filename
        
        if isinstance(content, str):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            with open(file_path, 'wb') as f:
                f.write(content)
        
        return str(file_path)
    
    def read_file(self, filename: str, encoding: str = 'utf-8') -> str:
        """파일 읽기"""
        file_path = self.base_dir / filename
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    
    def delete_file(self, filename: str) -> bool:
        """파일 삭제"""
        try:
            file_path = self.base_dir / filename
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def list_files(self, pattern: str = "*") -> List[str]:
        """파일 목록 반환"""
        return [str(f) for f in self.base_dir.glob(pattern)]
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """오래된 임시 파일 정리"""
        cleaned_count = 0
        current_time = datetime.now().timestamp()
        max_age_seconds = max_age_hours * 3600
        
        for file_path in self.base_dir.glob("temp_*"):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        file_path.unlink()
                        cleaned_count += 1
                    except Exception:
                        pass
        
        return cleaned_count
    
    def get_file_size(self, filename: str) -> int:
        """파일 크기 반환 (바이트)"""
        file_path = self.base_dir / filename
        return file_path.stat().st_size if file_path.exists() else 0
    
    def copy_file(self, src_filename: str, dst_filename: str) -> bool:
        """파일 복사"""
        try:
            src_path = self.base_dir / src_filename
            dst_path = self.base_dir / dst_filename
            shutil.copy2(src_path, dst_path)
            return True
        except Exception:
            return False
    
    def move_file(self, src_filename: str, dst_filename: str) -> bool:
        """파일 이동"""
        try:
            src_path = self.base_dir / src_filename
            dst_path = self.base_dir / dst_filename
            shutil.move(str(src_path), str(dst_path))
            return True
        except Exception:
            return False


class AudioFileManager(FileManager):
    """오디오 파일 전용 관리 클래스"""
    
    def __init__(self, base_dir: str = "./data/audio"):
        super().__init__(base_dir)
    
    def save_audio_file(self, audio_data: bytes, filename: str) -> str:
        """오디오 파일 저장"""
        return self.save_file(audio_data, filename)
    
    def create_recording_filename(self, meeting_title: str = "meeting") -> str:
        """녹음 파일명 생성"""
        return self.create_unique_filename(meeting_title, "wav")
    
    def cleanup_old_recordings(self, max_age_hours: int = 48) -> int:
        """오래된 녹음 파일 정리"""
        return self.cleanup_temp_files(max_age_hours)


class TextFileManager(FileManager):
    """텍스트 파일 전용 관리 클래스"""
    
    def __init__(self, base_dir: str = "./data/text"):
        super().__init__(base_dir)
    
    def save_transcription(self, text: str, meeting_id: str) -> str:
        """음성 인식 결과 저장"""
        filename = f"transcription_{meeting_id}.txt"
        return self.save_file(text, filename)
    
    def save_summary(self, summary: str, meeting_id: str) -> str:
        """회의 요약 저장"""
        filename = f"summary_{meeting_id}.txt"
        return self.save_file(summary, filename)
    
    def save_meeting_notes(self, notes: str, meeting_id: str) -> str:
        """회의록 저장"""
        filename = f"meeting_notes_{meeting_id}.md"
        return self.save_file(notes, filename)
