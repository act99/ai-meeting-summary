"""
Audio Recording Module

회의 녹음 기능 구현
"""

import pyaudio
import wave
import threading
import time
from typing import Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path

from ..utils.logger import LoggerMixin
from ..utils.config import config


class AudioRecorder(LoggerMixin):
    """오디오 녹음 클래스"""
    
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        self.recording_thread: Optional[threading.Thread] = None
        self.audio_frames = []
        self.start_time: Optional[datetime] = None
        self.duration_limit: Optional[timedelta] = None
        self.on_recording_callback: Optional[Callable] = None
        
        # 오디오 설정
        self.sample_rate = config.audio.sample_rate
        self.channels = config.audio.channels
        self.chunk_size = config.audio.chunk_size
        self.audio_format = config.get_audio_format()
        
        self.log_info(f"오디오 레코더 초기화 완료 - 샘플레이트: {self.sample_rate}, 채널: {self.channels}")
    
    def start_recording(
        self, 
        duration_minutes: Optional[int] = None,
        on_recording_callback: Optional[Callable] = None
    ) -> bool:
        """
        녹음 시작
        
        Args:
            duration_minutes: 녹음 시간 제한 (분)
            on_recording_callback: 녹음 중 콜백 함수
        
        Returns:
            녹음 시작 성공 여부
        """
        if self.is_recording:
            self.log_warning("이미 녹음 중입니다")
            return False
        
        try:
            # 녹음 시간 제한 설정
            if duration_minutes:
                self.duration_limit = timedelta(minutes=duration_minutes)
            else:
                self.duration_limit = timedelta(minutes=config.meeting.duration_minutes)
            
            self.on_recording_callback = on_recording_callback
            self.audio_frames = []
            self.start_time = datetime.now()
            self.is_recording = True
            
            # 녹음 스레드 시작
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.start()
            
            self.log_info(f"녹음 시작 - 제한 시간: {self.duration_limit}")
            return True
            
        except Exception as e:
            self.log_error(f"녹음 시작 실패: {e}")
            return False
    
    def stop_recording(self) -> Optional[str]:
        """
        녹음 중지 및 파일 저장
        
        Returns:
            저장된 파일 경로 또는 None
        """
        if not self.is_recording and not self.audio_frames:
            self.log_warning("녹음 중이 아니거나 녹음된 데이터가 없습니다")
            return None
        
        try:
            self.is_recording = False
            
            # 녹음 스레드 종료 대기
            if self.recording_thread:
                self.recording_thread.join(timeout=5.0)
            
            # 파일 저장
            if self.audio_frames:
                filename = self._generate_filename()
                file_path = self._save_audio_file(filename)
                
                duration = datetime.now() - self.start_time if self.start_time else timedelta()
                self.log_info(f"녹음 완료 - 파일: {file_path}, 시간: {duration}")
                
                return file_path
            else:
                self.log_warning("녹음된 데이터가 없습니다")
                return None
                
        except Exception as e:
            self.log_error(f"녹음 중지 실패: {e}")
            return None
    
    def _record_audio(self) -> None:
        """실제 오디오 녹음 스레드"""
        try:
            # 오디오 스트림 열기
            stream = self.audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.log_info("오디오 스트림 시작")
            
            while self.is_recording:
                # 시간 제한 확인
                if self.duration_limit and self.start_time:
                    elapsed = datetime.now() - self.start_time
                    if elapsed >= self.duration_limit:
                        self.log_info("녹음 시간 제한에 도달했습니다")
                        self.is_recording = False
                        break
                
                # 오디오 데이터 읽기
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                self.audio_frames.append(data)
                
                # 콜백 함수 호출
                if self.on_recording_callback:
                    try:
                        self.on_recording_callback(len(self.audio_frames))
                    except Exception as e:
                        self.log_error(f"콜백 함수 실행 오류: {e}")
            
            # 스트림 종료
            stream.stop_stream()
            stream.close()
            
            self.log_info("오디오 스트림 종료")
            
        except Exception as e:
            self.log_error(f"녹음 스레드 오류: {e}")
            self.is_recording = False
    
    def _generate_filename(self) -> str:
        """녹음 파일명 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"meeting_recording_{timestamp}.wav"
    
    def _save_audio_file(self, filename: str) -> str:
        """오디오 파일 저장"""
        file_path = config.get_data_file_path(filename)
        
        with wave.open(file_path, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.audio_format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.audio_frames))
        
        return file_path
    
    def get_recording_status(self) -> dict:
        """녹음 상태 정보 반환"""
        status = {
            "is_recording": self.is_recording,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "duration_limit": str(self.duration_limit) if self.duration_limit else None,
            "frames_count": len(self.audio_frames),
            "estimated_duration_seconds": len(self.audio_frames) * self.chunk_size / self.sample_rate
        }
        
        if self.start_time and self.is_recording:
            elapsed = datetime.now() - self.start_time
            status["elapsed_time"] = str(elapsed)
        
        return status
    
    def cleanup(self) -> None:
        """리소스 정리"""
        if self.is_recording:
            self.stop_recording()
        
        if hasattr(self, 'audio'):
            self.audio.terminate()
        
        self.log_info("오디오 레코더 정리 완료")
    
    def __del__(self):
        """소멸자"""
        self.cleanup()


class MeetingRecorder:
    """회의 전용 녹음 관리 클래스"""
    
    def __init__(self):
        self.recorder = AudioRecorder()
        self.meeting_title = "회의"
        self.meeting_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._stop_requested = False
    
    def start_meeting_recording(
        self, 
        meeting_title: str = "회의",
        duration_minutes: Optional[int] = None
    ) -> bool:
        """회의 녹음 시작"""
        self.meeting_title = meeting_title
        self._stop_requested = False
        
        def recording_progress(frame_count: int):
            duration_seconds = frame_count * self.recorder.chunk_size / self.recorder.sample_rate
            print(f"\r녹음 중... {duration_seconds:.1f}초", end="", flush=True)
        
        return self.recorder.start_recording(
            duration_minutes=duration_minutes,
            on_recording_callback=recording_progress
        )
    
    def stop_meeting_recording(self) -> Optional[str]:
        """회의 녹음 중지"""
        print()  # 새 줄
        return self.recorder.stop_recording()
    
    def stop_recording(self) -> Optional[str]:
        """녹음 중지 (호환성을 위한 별칭)"""
        return self.stop_meeting_recording()
    
    def request_stop(self) -> None:
        """녹음 중지 요청"""
        self._stop_requested = True
        if self.recorder.is_recording:
            self.recorder.is_recording = False
    
    def is_stop_requested(self) -> bool:
        """중지 요청 여부 확인"""
        return self._stop_requested
    
    def get_meeting_info(self) -> dict:
        """회의 정보 반환"""
        return {
            "meeting_id": self.meeting_id,
            "meeting_title": self.meeting_title,
            "recording_status": self.recorder.get_recording_status()
        }
