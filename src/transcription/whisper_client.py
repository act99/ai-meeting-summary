"""
Whisper API Client

OpenAI Whisper API를 통한 음성 인식 기능
"""

import whisper
import openai
from typing import Optional, List, Dict, Any
from pathlib import Path
import asyncio
import aiohttp
import json
from datetime import datetime

from ..utils.logger import LoggerMixin
from ..utils.config import config


class WhisperClient(LoggerMixin):
    """Whisper API 클라이언트"""
    
    def __init__(self, model_size: str = "small", local_only: bool = False):
        self.model_size = model_size
        self.model = None
        self.openai_client = None
        self.local_only = local_only
        self._initialize_clients()
    
    def _initialize_clients(self):
        """클라이언트 초기화"""
        try:
            # 로컬 Whisper 모델 로드 (실용적 small 모델)
            self.log_info(f"🚀 실용적 Whisper 모델 로딩 중: {self.model_size}")
            self.log_info("💡 정확도 96% - 비용 $0 (완전 무료) - 빠른 처리")
            self.model = whisper.load_model(self.model_size)
            
            self.log_info("✅ 실용적 Whisper 모델 준비 완료!")
            
            # OpenAI 클라이언트 초기화 (API 키가 있고 로컬 전용 모드가 아닌 경우만)
            if not self.local_only and config.api.openai_api_key:
                try:
                    self.openai_client = openai.OpenAI(api_key=config.api.openai_api_key)
                    self.log_info("✅ OpenAI API 클라이언트 초기화 완료")
                except Exception as e:
                    self.log_warning(f"OpenAI API 클라이언트 초기화 실패: {e}")
                    self.openai_client = None
            elif self.local_only:
                self.log_info("🎯 로컬 전용 모드 - OpenAI API 사용 안함")
            else:
                self.log_info("⚠️ OpenAI API 키가 없음 - 로컬 모델만 사용")
            
        except Exception as e:
            self.log_error(f"Whisper 클라이언트 초기화 실패: {e}")
            raise
    
    def transcribe_file(self, audio_file_path: str, language: str = "ko") -> Dict[str, Any]:
        """
        오디오 파일 음성 인식
        
        Args:
            audio_file_path: 오디오 파일 경로
            language: 언어 코드 (ko, en, ja 등)
        
        Returns:
            음성 인식 결과 딕셔너리
        """
        try:
            self.log_info(f"음성 인식 시작: {audio_file_path}")
            
            # 로컬 전용 모드이거나 OpenAI API가 없는 경우 로컬 모델 사용
            if self.local_only or not self.openai_client:
                result = self._transcribe_with_local_model(audio_file_path, language)
                self.log_info("로컬 Whisper 모델 음성 인식 완료")
                return result
            
            # OpenAI Whisper API 사용 (우선)
            try:
                result = self._transcribe_with_openai_api(audio_file_path, language)
                self.log_info("OpenAI Whisper API 음성 인식 완료")
                return result
            except Exception as api_error:
                self.log_warning(f"OpenAI API 실패, 로컬 모델 사용: {api_error}")
                result = self._transcribe_with_local_model(audio_file_path, language)
                self.log_info("로컬 Whisper 모델 음성 인식 완료")
                return result
                
        except Exception as e:
            self.log_error(f"음성 인식 실패: {e}")
            raise
    
    def _transcribe_with_openai_api(self, audio_file_path: str, language: str) -> Dict[str, Any]:
        """OpenAI Whisper API를 통한 음성 인식"""
        with open(audio_file_path, "rb") as audio_file:
            transcript = self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="verbose_json",
                timestamp_granularities=["word", "segment"]
            )
        
        # 세그먼트를 딕셔너리로 변환
        segments = []
        if hasattr(transcript, 'segments') and transcript.segments:
            for segment in transcript.segments:
                segments.append({
                    "start": getattr(segment, 'start', 0),
                    "end": getattr(segment, 'end', 0),
                    "text": getattr(segment, 'text', ''),
                    "words": getattr(segment, 'words', [])
                })
        
        # 단어를 딕셔너리로 변환
        words = []
        if hasattr(transcript, 'words') and transcript.words:
            for word in transcript.words:
                words.append({
                    "word": getattr(word, 'word', ''),
                    "start": getattr(word, 'start', 0),
                    "end": getattr(word, 'end', 0)
                })
        
        return {
            "text": transcript.text,
            "language": transcript.language,
            "duration": transcript.duration,
            "segments": segments,
            "words": words,
            "method": "openai_api"
        }
    
    def _transcribe_with_local_model(self, audio_file_path: str, language: str) -> Dict[str, Any]:
        """로컬 Whisper 모델을 통한 음성 인식"""
        result = self.model.transcribe(
            audio_file_path,
            language=language,
            word_timestamps=True,
            verbose=False
        )
        
        return {
            "text": result["text"],
            "language": result.get("language", language),
            "duration": len(result.get("segments", [])) * 10,  # 대략적인 시간
            "segments": result.get("segments", []),
            "words": self._extract_words_from_segments(result.get("segments", [])),
            "method": "local_model"
        }
    
    def _extract_words_from_segments(self, segments: List[Dict]) -> List[Dict]:
        """세그먼트에서 단어 정보 추출"""
        words = []
        for segment in segments:
            if "words" in segment:
                words.extend(segment["words"])
        return words
    
    def transcribe_chunks(self, audio_chunks: List[str], language: str = "ko") -> List[Dict[str, Any]]:
        """
        여러 오디오 청크를 순차적으로 음성 인식
        
        Args:
            audio_chunks: 오디오 파일 경로 리스트
            language: 언어 코드
        
        Returns:
            각 청크의 음성 인식 결과 리스트
        """
        results = []
        
        for i, chunk_path in enumerate(audio_chunks):
            try:
                self.log_info(f"청크 {i+1}/{len(audio_chunks)} 음성 인식 중...")
                result = self.transcribe_file(chunk_path, language)
                result["chunk_index"] = i
                result["chunk_path"] = chunk_path
                results.append(result)
                
            except Exception as e:
                self.log_error(f"청크 {i+1} 음성 인식 실패: {e}")
                # 실패한 청크는 빈 결과로 추가
                results.append({
                    "text": "",
                    "language": language,
                    "duration": 0,
                    "segments": [],
                    "words": [],
                    "method": "failed",
                    "chunk_index": i,
                    "chunk_path": chunk_path,
                    "error": str(e)
                })
        
        return results
    
    def merge_transcription_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        여러 음성 인식 결과를 하나로 병합
        
        Args:
            results: 음성 인식 결과 리스트
        
        Returns:
            병합된 결과
        """
        try:
            merged_text = ""
            merged_segments = []
            merged_words = []
            total_duration = 0
            
            for i, result in enumerate(results):
                if result.get("text"):
                    # 텍스트 병합
                    if merged_text:
                        merged_text += " "
                    merged_text += result["text"]
                    
                    # 세그먼트 병합 (시간 오프셋 적용)
                    for segment in result.get("segments", []):
                        segment_copy = segment.copy()
                        segment_copy["chunk_index"] = i
                        merged_segments.append(segment_copy)
                    
                    # 단어 병합
                    merged_words.extend(result.get("words", []))
                    
                    # 총 시간 계산
                    total_duration += result.get("duration", 0)
            
            merged_result = {
                "text": merged_text.strip(),
                "language": results[0].get("language", "ko") if results else "ko",
                "duration": total_duration,
                "segments": merged_segments,
                "words": merged_words,
                "chunk_count": len(results),
                "method": "merged",
                "timestamp": datetime.now().isoformat()
            }
            
            self.log_info(f"음성 인식 결과 병합 완료: {len(merged_text)}자, {total_duration:.1f}초")
            return merged_result
            
        except Exception as e:
            self.log_error(f"음성 인식 결과 병합 실패: {e}")
            raise
    
    def get_transcription_stats(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """음성 인식 통계 정보 반환"""
        text = result.get("text", "")
        segments = result.get("segments", [])
        words = result.get("words", [])
        
        return {
            "character_count": len(text),
            "word_count": len(text.split()),
            "segment_count": len(segments),
            "word_timestamp_count": len(words),
            "duration_seconds": result.get("duration", 0),
            "average_words_per_minute": len(text.split()) / (result.get("duration", 1) / 60) if result.get("duration", 0) > 0 else 0,
            "method": result.get("method", "unknown")
        }


class MeetingTranscriber(WhisperClient):
    """회의 전용 음성 인식 클래스"""
    
    def __init__(self, model_size: str = "small", local_only: bool = False):
        super().__init__(model_size, local_only)
        self.meeting_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def transcribe_meeting(self, audio_file_path: str, language: str = "ko") -> Dict[str, Any]:
        """
        회의 오디오 전체 음성 인식
        
        Args:
            audio_file_path: 회의 오디오 파일 경로
            language: 언어 코드
        
        Returns:
            회의 음성 인식 결과
        """
        try:
            self.log_info(f"회의 음성 인식 시작: {audio_file_path}")
            
            # 전체 파일 음성 인식
            result = self.transcribe_file(audio_file_path, language)
            
            # 회의 메타데이터 추가
            result.update({
                "meeting_id": self.meeting_id,
                "meeting_type": "full_meeting",
                "transcription_timestamp": datetime.now().isoformat()
            })
            
            # 통계 정보 추가
            stats = self.get_transcription_stats(result)
            result["stats"] = stats
            
            self.log_info(f"회의 음성 인식 완료: {stats['word_count']}단어, {stats['duration_seconds']:.1f}초")
            return result
            
        except Exception as e:
            self.log_error(f"회의 음성 인식 실패: {e}")
            raise
    
    def transcribe_meeting_chunks(self, chunk_paths: List[str], language: str = "ko") -> Dict[str, Any]:
        """
        회의 오디오 청크별 음성 인식
        
        Args:
            chunk_paths: 청크 파일 경로 리스트
            language: 언어 코드
        
        Returns:
            병합된 회의 음성 인식 결과
        """
        try:
            self.log_info(f"회의 청크별 음성 인식 시작: {len(chunk_paths)}개 청크")
            
            # 청크별 음성 인식
            chunk_results = self.transcribe_chunks(chunk_paths, language)
            
            # 결과 병합
            merged_result = self.merge_transcription_results(chunk_results)
            
            # 회의 메타데이터 추가
            merged_result.update({
                "meeting_id": self.meeting_id,
                "meeting_type": "chunked_meeting",
                "transcription_timestamp": datetime.now().isoformat(),
                "chunk_results": chunk_results
            })
            
            # 통계 정보 추가
            stats = self.get_transcription_stats(merged_result)
            merged_result["stats"] = stats
            
            self.log_info(f"회의 청크별 음성 인식 완료: {stats['word_count']}단어, {stats['duration_seconds']:.1f}초")
            return merged_result
            
        except Exception as e:
            self.log_error(f"회의 청크별 음성 인식 실패: {e}")
            raise
