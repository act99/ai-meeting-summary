"""
Text Formatting Module

음성 인식 결과 텍스트 포맷팅 및 구조화
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from ..utils.logger import LoggerMixin


class TextFormatter(LoggerMixin):
    """텍스트 포맷팅 클래스"""
    
    def __init__(self):
        self.log_info("텍스트 포맷터 초기화 완료")
    
    def clean_transcription_text(self, text: str) -> str:
        """
        음성 인식 텍스트 정리
        
        Args:
            text: 원본 음성 인식 텍스트
        
        Returns:
            정리된 텍스트
        """
        try:
            # 기본 정리
            cleaned = text.strip()
            
            # 불필요한 공백 제거
            cleaned = re.sub(r'\s+', ' ', cleaned)
            
            # 문장 부호 정리
            cleaned = re.sub(r'\s+([,.!?])', r'\1', cleaned)
            
            # 문장 시작 대문자화
            sentences = re.split(r'([.!?])', cleaned)
            formatted_sentences = []
            
            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    if i == 0 or sentences[i-1] in '.!?':
                        sentence = sentence.strip().capitalize()
                    formatted_sentences.append(sentence)
            
            cleaned = ''.join(formatted_sentences)
            
            self.log_info("텍스트 정리 완료")
            return cleaned
            
        except Exception as e:
            self.log_error(f"텍스트 정리 실패: {e}")
            return text
    
    def format_with_timestamps(self, transcription_result: Dict[str, Any]) -> str:
        """
        타임스탬프가 포함된 텍스트 포맷팅
        
        Args:
            transcription_result: 음성 인식 결과
        
        Returns:
            타임스탬프가 포함된 포맷된 텍스트
        """
        try:
            segments = transcription_result.get("segments", [])
            if not segments:
                return self.clean_transcription_text(transcription_result.get("text", ""))
            
            formatted_lines = []
            
            for segment in segments:
                # segment가 딕셔너리인지 객체인지 확인
                if isinstance(segment, dict):
                    start_time = self._format_timestamp(segment.get("start", 0))
                    end_time = self._format_timestamp(segment.get("end", 0))
                    text = segment.get("text", "").strip()
                else:
                    # TranscriptionSegment 객체인 경우
                    start_time = self._format_timestamp(getattr(segment, "start", 0))
                    end_time = self._format_timestamp(getattr(segment, "end", 0))
                    text = getattr(segment, "text", "").strip()
                
                if text:
                    formatted_lines.append(f"[{start_time} - {end_time}] {text}")
            
            formatted_text = "\n".join(formatted_lines)
            self.log_info("타임스탬프 포맷팅 완료")
            return formatted_text
            
        except Exception as e:
            self.log_error(f"타임스탬프 포맷팅 실패: {e}")
            return self.clean_transcription_text(transcription_result.get("text", ""))
    
    def _format_timestamp(self, seconds: float) -> str:
        """초를 MM:SS 형식으로 변환"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def extract_speakers(self, transcription_result: Dict[str, Any]) -> List[str]:
        """
        화자 정보 추출 (간단한 휴리스틱)
        
        Args:
            transcription_result: 음성 인식 결과
        
        Returns:
            추정된 화자 리스트
        """
        try:
            text = transcription_result.get("text", "")
            
            # 간단한 화자 구분 패턴
            speaker_patterns = [
                r'([A-Z가-힣]+):',  # "김철수:", "John:" 패턴
                r'([A-Z가-힣]+)\s+말씀',  # "김철수 말씀" 패턴
                r'([A-Z가-힣]+)\s+님',  # "김철수님" 패턴
            ]
            
            speakers = set()
            for pattern in speaker_patterns:
                matches = re.findall(pattern, text)
                speakers.update(matches)
            
            # 일반적인 회의 참석자 이름 패턴
            common_names = [
                "김철수", "이영희", "박민수", "최지영", "정현우",
                "John", "Jane", "Mike", "Sarah", "David"
            ]
            
            for name in common_names:
                if name in text:
                    speakers.add(name)
            
            speaker_list = list(speakers)
            self.log_info(f"추정된 화자: {speaker_list}")
            return speaker_list
            
        except Exception as e:
            self.log_error(f"화자 추출 실패: {e}")
            return []
    
    def structure_meeting_content(self, transcription_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        회의 내용 구조화
        
        Args:
            transcription_result: 음성 인식 결과
        
        Returns:
            구조화된 회의 내용
        """
        try:
            text = self.clean_transcription_text(transcription_result.get("text", ""))
            
            # 기본 구조
            structured_content = {
                "meeting_id": transcription_result.get("meeting_id", ""),
                "timestamp": transcription_result.get("transcription_timestamp", ""),
                "duration": transcription_result.get("duration", 0),
                "language": transcription_result.get("language", "ko"),
                "full_text": text,
                "speakers": self.extract_speakers(transcription_result),
                "topics": self._extract_topics(text),
                "action_items": self._extract_action_items(text),
                "decisions": self._extract_decisions(text),
                "key_points": self._extract_key_points(text),
                "word_count": len(text.split()),
                "character_count": len(text)
            }
            
            self.log_info("회의 내용 구조화 완료")
            return structured_content
            
        except Exception as e:
            self.log_error(f"회의 내용 구조화 실패: {e}")
            return {"error": str(e)}
    
    def _extract_topics(self, text: str) -> List[str]:
        """주제 추출"""
        topics = []
        
        # 주제 관련 키워드 패턴
        topic_patterns = [
            r'([^.!?]*(?:안건|주제|토론|검토|논의)[^.!?]*)',
            r'([^.!?]*(?:프로젝트|계획|제안|보고)[^.!?]*)',
            r'([^.!?]*(?:예산|비용|자원|인력)[^.!?]*)'
        ]
        
        for pattern in topic_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            topics.extend([match.strip() for match in matches if len(match.strip()) > 10])
        
        return list(set(topics))[:10]  # 최대 10개
    
    def _extract_action_items(self, text: str) -> List[str]:
        """액션 아이템 추출"""
        action_items = []
        
        # 액션 아이템 패턴
        action_patterns = [
            r'([^.!?]*(?:해야|해야 한다|진행|확인|검토|준비|작업)[^.!?]*)',
            r'([^.!?]*(?:다음|향후|앞으로|이후)[^.!?]*)',
            r'([^.!?]*(?:담당|책임|역할|업무)[^.!?]*)'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            action_items.extend([match.strip() for match in matches if len(match.strip()) > 10])
        
        return list(set(action_items))[:15]  # 최대 15개
    
    def _extract_decisions(self, text: str) -> List[str]:
        """결정사항 추출"""
        decisions = []
        
        # 결정사항 패턴
        decision_patterns = [
            r'([^.!?]*(?:결정|승인|합의|동의|채택)[^.!?]*)',
            r'([^.!?]*(?:확정|최종|최종적으로)[^.!?]*)',
            r'([^.!?]*(?:그렇게|그럼|좋습니다|알겠습니다)[^.!?]*)'
        ]
        
        for pattern in decision_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            decisions.extend([match.strip() for match in matches if len(match.strip()) > 10])
        
        return list(set(decisions))[:10]  # 최대 10개
    
    def _extract_key_points(self, text: str) -> List[str]:
        """핵심 포인트 추출"""
        key_points = []
        
        # 핵심 포인트 패턴
        key_patterns = [
            r'([^.!?]*(?:중요|핵심|주요|필수)[^.!?]*)',
            r'([^.!?]*(?:문제|이슈|과제)[^.!?]*)',
            r'([^.!?]*(?:목표|목적|방향)[^.!?]*)'
        ]
        
        for pattern in key_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            key_points.extend([match.strip() for match in matches if len(match.strip()) > 10])
        
        return list(set(key_points))[:12]  # 최대 12개
    
    def format_for_summary(self, structured_content: Dict[str, Any]) -> str:
        """
        요약용 텍스트 포맷팅
        
        Args:
            structured_content: 구조화된 회의 내용
        
        Returns:
            요약용 포맷된 텍스트
        """
        try:
            formatted_text = f"""회의 정보:
- 회의 ID: {structured_content.get('meeting_id', 'N/A')}
- 시간: {structured_content.get('timestamp', 'N/A')}
- 지속시간: {structured_content.get('duration', 0):.1f}초
- 언어: {structured_content.get('language', 'ko')}
- 단어 수: {structured_content.get('word_count', 0)}

참석자: {', '.join(structured_content.get('speakers', []))}

회의 내용:
{structured_content.get('full_text', '')}

주요 주제:
{chr(10).join(f'- {topic}' for topic in structured_content.get('topics', []))}

핵심 포인트:
{chr(10).join(f'- {point}' for point in structured_content.get('key_points', []))}

결정사항:
{chr(10).join(f'- {decision}' for decision in structured_content.get('decisions', []))}

액션 아이템:
{chr(10).join(f'- {action}' for action in structured_content.get('action_items', []))}
"""
            
            return formatted_text
            
        except Exception as e:
            self.log_error(f"요약용 포맷팅 실패: {e}")
            return structured_content.get('full_text', '')
    
    def save_formatted_text(self, formatted_text: str, meeting_id: str, format_type: str = "summary") -> str:
        """
        포맷된 텍스트 파일 저장
        
        Args:
            formatted_text: 포맷된 텍스트
            meeting_id: 회의 ID
            format_type: 포맷 타입 (summary, full, structured)
        
        Returns:
            저장된 파일 경로
        """
        try:
            from ..utils.file_manager import TextFileManager
            
            file_manager = TextFileManager()
            filename = f"{format_type}_{meeting_id}.txt"
            file_path = file_manager.save_file(formatted_text, filename)
            
            self.log_info(f"포맷된 텍스트 저장 완료: {file_path}")
            return file_path
            
        except Exception as e:
            self.log_error(f"포맷된 텍스트 저장 실패: {e}")
            raise
