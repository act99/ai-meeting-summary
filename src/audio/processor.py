"""
Audio Processing Module

오디오 파일 전처리 및 최적화
"""

import librosa
import numpy as np
import noisereduce as nr
import soundfile as sf
from typing import Optional, Tuple
from pathlib import Path

from ..utils.logger import LoggerMixin
from ..utils.config import config


class AudioProcessor(LoggerMixin):
    """오디오 전처리 클래스"""
    
    def __init__(self):
        self.sample_rate = config.audio.sample_rate
        self.log_info("오디오 프로세서 초기화 완료")
    
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        오디오 파일 로드
        
        Args:
            file_path: 오디오 파일 경로
        
        Returns:
            (오디오 데이터, 샘플레이트)
        """
        try:
            audio_data, sr = librosa.load(file_path, sr=self.sample_rate)
            self.log_info(f"오디오 파일 로드 완료: {file_path}, 길이: {len(audio_data)/sr:.2f}초")
            return audio_data, sr
        except Exception as e:
            self.log_error(f"오디오 파일 로드 실패: {e}")
            raise
    
    def reduce_noise(self, audio_data: np.ndarray, sr: int) -> np.ndarray:
        """
        노이즈 제거
        
        Args:
            audio_data: 오디오 데이터
            sr: 샘플레이트
        
        Returns:
            노이즈 제거된 오디오 데이터
        """
        try:
            # 노이즈 제거
            reduced_noise = nr.reduce_noise(y=audio_data, sr=sr)
            self.log_info("노이즈 제거 완료")
            return reduced_noise
        except Exception as e:
            self.log_warning(f"노이즈 제거 실패, 원본 데이터 사용: {e}")
            return audio_data
    
    def normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """
        오디오 정규화
        
        Args:
            audio_data: 오디오 데이터
        
        Returns:
            정규화된 오디오 데이터
        """
        try:
            # RMS 정규화
            rms = np.sqrt(np.mean(audio_data**2))
            if rms > 0:
                normalized = audio_data / rms * 0.1  # 적절한 레벨로 조정
                self.log_info("오디오 정규화 완료")
                return normalized
            return audio_data
        except Exception as e:
            self.log_warning(f"오디오 정규화 실패, 원본 데이터 사용: {e}")
            return audio_data
    
    def trim_silence(self, audio_data: np.ndarray, sr: int) -> np.ndarray:
        """
        무음 구간 제거
        
        Args:
            audio_data: 오디오 데이터
            sr: 샘플레이트
        
        Returns:
            무음 구간이 제거된 오디오 데이터
        """
        try:
            # 무음 구간 감지 및 제거
            trimmed, _ = librosa.effects.trim(audio_data, top_db=20)
            self.log_info(f"무음 구간 제거 완료: {len(audio_data)/sr:.2f}초 -> {len(trimmed)/sr:.2f}초")
            return trimmed
        except Exception as e:
            self.log_warning(f"무음 구간 제거 실패, 원본 데이터 사용: {e}")
            return audio_data
    
    def enhance_audio(self, audio_data: np.ndarray, sr: int) -> np.ndarray:
        """
        오디오 품질 향상
        
        Args:
            audio_data: 오디오 데이터
            sr: 샘플레이트
        
        Returns:
            향상된 오디오 데이터
        """
        try:
            # 1. 노이즈 제거
            enhanced = self.reduce_noise(audio_data, sr)
            
            # 2. 정규화
            enhanced = self.normalize_audio(enhanced)
            
            # 3. 무음 구간 제거
            enhanced = self.trim_silence(enhanced, sr)
            
            self.log_info("오디오 품질 향상 완료")
            return enhanced
            
        except Exception as e:
            self.log_error(f"오디오 품질 향상 실패: {e}")
            return audio_data
    
    def split_into_chunks(
        self, 
        audio_data: np.ndarray, 
        sr: int, 
        chunk_duration_seconds: int = 30
    ) -> list:
        """
        오디오를 청크로 분할
        
        Args:
            audio_data: 오디오 데이터
            sr: 샘플레이트
            chunk_duration_seconds: 청크 길이 (초)
        
        Returns:
            청크 리스트
        """
        try:
            chunk_size = chunk_duration_seconds * sr
            chunks = []
            
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                if len(chunk) > 0:
                    chunks.append(chunk)
            
            self.log_info(f"오디오 청크 분할 완료: {len(chunks)}개 청크")
            return chunks
            
        except Exception as e:
            self.log_error(f"오디오 청크 분할 실패: {e}")
            return [audio_data]
    
    def get_audio_info(self, audio_data: np.ndarray, sr: int) -> dict:
        """
        오디오 정보 반환
        
        Args:
            audio_data: 오디오 데이터
            sr: 샘플레이트
        
        Returns:
            오디오 정보 딕셔너리
        """
        duration = len(audio_data) / sr
        rms = np.sqrt(np.mean(audio_data**2))
        max_amplitude = np.max(np.abs(audio_data))
        
        return {
            "duration_seconds": duration,
            "sample_rate": sr,
            "samples_count": len(audio_data),
            "rms": rms,
            "max_amplitude": max_amplitude,
            "is_silent": rms < 0.01
        }
    
    def process_audio_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        오디오 파일 전체 처리
        
        Args:
            input_path: 입력 파일 경로
            output_path: 출력 파일 경로 (None이면 자동 생성)
        
        Returns:
            처리된 파일 경로
        """
        try:
            # 오디오 로드
            audio_data, sr = self.load_audio(input_path)
            
            # 오디오 정보 로그
            audio_info = self.get_audio_info(audio_data, sr)
            self.log_info(f"원본 오디오 정보: {audio_info}")
            
            # 품질 향상
            enhanced_audio = self.enhance_audio(audio_data, sr)
            
            # 출력 파일 경로 설정
            if output_path is None:
                input_file = Path(input_path)
                output_path = str(input_file.parent / f"enhanced_{input_file.name}")
            
            # 파일 저장
            sf.write(output_path, enhanced_audio, sr)
            
            # 처리된 오디오 정보
            enhanced_info = self.get_audio_info(enhanced_audio, sr)
            self.log_info(f"처리된 오디오 정보: {enhanced_info}")
            
            return output_path
            
        except Exception as e:
            self.log_error(f"오디오 파일 처리 실패: {e}")
            raise


class MeetingAudioProcessor(AudioProcessor):
    """회의 오디오 전용 처리 클래스"""
    
    def __init__(self):
        super().__init__()
        self.chunk_duration = 30  # 30초 청크
    
    def process_meeting_audio(self, input_path: str) -> Tuple[str, list]:
        """
        회의 오디오 처리
        
        Args:
            input_path: 입력 파일 경로
        
        Returns:
            (처리된 파일 경로, 청크 리스트)
        """
        try:
            # 오디오 로드 및 처리
            audio_data, sr = self.load_audio(input_path)
            enhanced_audio = self.enhance_audio(audio_data, sr)
            
            # 청크로 분할
            chunks = self.split_into_chunks(enhanced_audio, sr, self.chunk_duration)
            
            # 처리된 파일 저장
            output_path = self._save_processed_audio(enhanced_audio, sr, input_path)
            
            self.log_info(f"회의 오디오 처리 완료: {len(chunks)}개 청크")
            return output_path, chunks
            
        except Exception as e:
            self.log_error(f"회의 오디오 처리 실패: {e}")
            raise
    
    def _save_processed_audio(self, audio_data: np.ndarray, sr: int, original_path: str) -> str:
        """처리된 오디오 저장"""
        original_file = Path(original_path)
        output_path = str(original_file.parent / f"processed_{original_file.name}")
        sf.write(output_path, audio_data, sr)
        return output_path
