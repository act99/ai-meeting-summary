"""
GPT API Client

OpenAI GPT API를 통한 회의 요약 및 분석
"""

import openai
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..utils.logger import LoggerMixin
from ..utils.config import config
from .prompt_templates import PromptTemplates


class GPTClient(LoggerMixin):
    """GPT API 클라이언트"""
    
    def __init__(self):
        self.client = None
        self.model = config.api.openai_model
        self.prompt_templates = PromptTemplates()
        
        # API 키가 있는 경우에만 클라이언트 초기화
        if config.api.openai_api_key:
            try:
                self.client = openai.OpenAI(api_key=config.api.openai_api_key)
                self.log_info(f"GPT 클라이언트 초기화 완료 - 모델: {self.model}")
            except Exception as e:
                self.log_warning(f"GPT 클라이언트 초기화 실패: {e}")
                self.client = None
        else:
            self.log_warning("OpenAI API 키가 없음 - GPT 요약 기능 사용 불가")
    
    def summarize_meeting(self, transcription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        회의 요약 생성
        
        Args:
            transcription_data: 음성 인식 결과 데이터
        
        Returns:
            회의 요약 결과
        """
        try:
            self.log_info("회의 요약 시작")
            
            # 메인 요약 프롬프트 생성
            prompt = self.prompt_templates.get_meeting_summary_prompt(transcription_data)
            
            # GPT API 호출
            response = self._call_gpt_api(prompt)
            
            # 결과 구조화
            summary_result = {
                "meeting_id": transcription_data.get("meeting_id", ""),
                "timestamp": datetime.now().isoformat(),
                "summary": response,
                "summary_type": "comprehensive",
                "word_count": len(response.split()),
                "character_count": len(response),
                "model_used": self.model
            }
            
            self.log_info(f"회의 요약 완료: {summary_result['word_count']}단어")
            return summary_result
            
        except Exception as e:
            self.log_error(f"회의 요약 실패: {e}")
            raise
    
    def extract_action_items(self, transcription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        액션 아이템 추출
        
        Args:
            transcription_data: 음성 인식 결과 데이터
        
        Returns:
            액션 아이템 추출 결과
        """
        try:
            self.log_info("액션 아이템 추출 시작")
            
            prompt = self.prompt_templates.get_action_items_extraction_prompt(transcription_data)
            response = self._call_gpt_api(prompt)
            
            # JSON 파싱 시도
            try:
                action_items_data = json.loads(response)
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 텍스트로 처리
                action_items_data = {"action_items": [{"task": response, "assignee": "미정", "deadline": "미정", "priority": "medium"}]}
            
            result = {
                "meeting_id": transcription_data.get("meeting_id", ""),
                "timestamp": datetime.now().isoformat(),
                "action_items": action_items_data.get("action_items", []),
                "extraction_method": "gpt_api"
            }
            
            self.log_info(f"액션 아이템 추출 완료: {len(result['action_items'])}개")
            return result
            
        except Exception as e:
            self.log_error(f"액션 아이템 추출 실패: {e}")
            raise
    
    def extract_decisions(self, transcription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        결정사항 추출
        
        Args:
            transcription_data: 음성 인식 결과 데이터
        
        Returns:
            결정사항 추출 결과
        """
        try:
            self.log_info("결정사항 추출 시작")
            
            prompt = self.prompt_templates.get_decision_extraction_prompt(transcription_data)
            response = self._call_gpt_api(prompt)
            
            # JSON 파싱 시도
            try:
                decisions_data = json.loads(response)
            except json.JSONDecodeError:
                decisions_data = {"decisions": [{"decision": response, "rationale": "미정", "impact": "medium", "stakeholders": []}]}
            
            result = {
                "meeting_id": transcription_data.get("meeting_id", ""),
                "timestamp": datetime.now().isoformat(),
                "decisions": decisions_data.get("decisions", []),
                "extraction_method": "gpt_api"
            }
            
            self.log_info(f"결정사항 추출 완료: {len(result['decisions'])}개")
            return result
            
        except Exception as e:
            self.log_error(f"결정사항 추출 실패: {e}")
            raise
    
    def analyze_meeting(self, transcription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        회의 분석
        
        Args:
            transcription_data: 음성 인식 결과 데이터
        
        Returns:
            회의 분석 결과
        """
        try:
            self.log_info("회의 분석 시작")
            
            prompt = self.prompt_templates.get_meeting_analysis_prompt(transcription_data)
            response = self._call_gpt_api(prompt)
            
            result = {
                "meeting_id": transcription_data.get("meeting_id", ""),
                "timestamp": datetime.now().isoformat(),
                "analysis": response,
                "analysis_type": "comprehensive",
                "model_used": self.model
            }
            
            self.log_info("회의 분석 완료")
            return result
            
        except Exception as e:
            self.log_error(f"회의 분석 실패: {e}")
            raise
    
    def generate_short_summary(self, transcription_data: Dict[str, Any]) -> str:
        """
        간단한 요약 생성
        
        Args:
            transcription_data: 음성 인식 결과 데이터
        
        Returns:
            간단한 요약 텍스트
        """
        try:
            prompt = self.prompt_templates.get_short_summary_prompt(transcription_data)
            response = self._call_gpt_api(prompt)
            
            self.log_info("간단한 요약 생성 완료")
            return response
            
        except Exception as e:
            self.log_error(f"간단한 요약 생성 실패: {e}")
            raise
    
    def generate_detailed_summary(self, transcription_data: Dict[str, Any]) -> str:
        """
        상세한 요약 생성
        
        Args:
            transcription_data: 음성 인식 결과 데이터
        
        Returns:
            상세한 요약 텍스트
        """
        try:
            prompt = self.prompt_templates.get_detailed_summary_prompt(transcription_data)
            response = self._call_gpt_api(prompt)
            
            self.log_info("상세한 요약 생성 완료")
            return response
            
        except Exception as e:
            self.log_error(f"상세한 요약 생성 실패: {e}")
            raise
    
    def _call_gpt_api(self, prompt: str, max_tokens: int = 4000) -> str:
        """
        GPT API 호출
        
        Args:
            prompt: 프롬프트 텍스트
            max_tokens: 최대 토큰 수
        
        Returns:
            GPT 응답 텍스트
        """
        if not self.client:
            raise Exception("OpenAI API 키가 없어서 GPT 요약을 사용할 수 없습니다. 로컬 Whisper 음성 인식만 가능합니다.")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 전문적인 회의 요약 전문가입니다. 정확하고 구조화된 요약을 제공해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3,  # 일관성을 위해 낮은 temperature 사용
                top_p=0.9
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.log_error(f"GPT API 호출 실패: {e}")
            raise
    
    def get_token_usage(self, prompt: str, response: str) -> Dict[str, int]:
        """
        토큰 사용량 계산 (대략적)
        
        Args:
            prompt: 프롬프트 텍스트
            response: 응답 텍스트
        
        Returns:
            토큰 사용량 정보
        """
        # 간단한 토큰 계산 (정확하지 않음)
        prompt_tokens = len(prompt.split()) * 1.3  # 대략적 계산
        response_tokens = len(response.split()) * 1.3
        
        return {
            "prompt_tokens": int(prompt_tokens),
            "completion_tokens": int(response_tokens),
            "total_tokens": int(prompt_tokens + response_tokens)
        }


class MeetingSummarizer(GPTClient):
    """회의 전용 요약 클래스"""
    
    def __init__(self):
        super().__init__()
        self.meeting_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def summarize_meeting_comprehensive(self, transcription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        회의 종합 요약
        
        Args:
            transcription_data: 음성 인식 결과 데이터
        
        Returns:
            종합 요약 결과
        """
        try:
            self.log_info("회의 종합 요약 시작")
            
            # 각종 요약 및 분석 수행
            main_summary = self.summarize_meeting(transcription_data)
            action_items = self.extract_action_items(transcription_data)
            decisions = self.extract_decisions(transcription_data)
            analysis = self.analyze_meeting(transcription_data)
            
            # 종합 결과 구성
            comprehensive_result = {
                "meeting_id": self.meeting_id,
                "timestamp": datetime.now().isoformat(),
                "summary": main_summary["summary"],
                "action_items": action_items["action_items"],
                "decisions": decisions["decisions"],
                "analysis": analysis["analysis"],
                "metadata": {
                    "duration": transcription_data.get("duration", 0),
                    "word_count": transcription_data.get("word_count", 0),
                    "speakers": transcription_data.get("speakers", []),
                    "language": transcription_data.get("language", "ko"),
                    "model_used": self.model,
                    "processing_time": datetime.now().isoformat()
                }
            }
            
            self.log_info("회의 종합 요약 완료")
            return comprehensive_result
            
        except Exception as e:
            self.log_error(f"회의 종합 요약 실패: {e}")
            raise
    
    def save_summary_to_file(self, summary_data: Dict[str, Any], format_type: str = "comprehensive") -> str:
        """
        요약 결과 파일 저장
        
        Args:
            summary_data: 요약 데이터
            format_type: 저장 형식
        
        Returns:
            저장된 파일 경로
        """
        try:
            from ..utils.file_manager import TextFileManager
            
            file_manager = TextFileManager()
            
            if format_type == "comprehensive":
                content = self._format_comprehensive_summary(summary_data)
                filename = f"comprehensive_summary_{self.meeting_id}.md"
            elif format_type == "action_items":
                content = self._format_action_items(summary_data)
                filename = f"action_items_{self.meeting_id}.txt"
            elif format_type == "decisions":
                content = self._format_decisions(summary_data)
                filename = f"decisions_{self.meeting_id}.txt"
            else:
                content = summary_data.get("summary", "")
                filename = f"summary_{self.meeting_id}.txt"
            
            file_path = file_manager.save_file(content, filename)
            self.log_info(f"요약 파일 저장 완료: {file_path}")
            return file_path
            
        except Exception as e:
            self.log_error(f"요약 파일 저장 실패: {e}")
            raise
    
    def _format_comprehensive_summary(self, data: Dict[str, Any]) -> str:
        """종합 요약 포맷팅"""
        return f"""# 회의 요약 - {data.get('meeting_id', 'N/A')}

## 📋 요약
{data.get('summary', '')}

## ✅ 액션 아이템
{self._format_action_items(data)}

## 📊 결정사항
{self._format_decisions(data)}

## 🔍 분석
{data.get('analysis', '')}

## 📊 메타데이터
- 생성 시간: {data.get('timestamp', 'N/A')}
- 모델: {data.get('metadata', {}).get('model_used', 'N/A')}
- 지속시간: {data.get('metadata', {}).get('duration', 0):.1f}초
- 단어 수: {data.get('metadata', {}).get('word_count', 0)}
"""
    
    def _format_action_items(self, data: Dict[str, Any]) -> str:
        """액션 아이템 포맷팅"""
        action_items = data.get('action_items', [])
        if not action_items:
            return "액션 아이템이 없습니다."
        
        formatted_items = []
        for i, item in enumerate(action_items, 1):
            formatted_items.append(f"{i}. **{item.get('task', 'N/A')}**")
            formatted_items.append(f"   - 담당자: {item.get('assignee', '미정')}")
            formatted_items.append(f"   - 마감일: {item.get('deadline', '미정')}")
            formatted_items.append(f"   - 우선순위: {item.get('priority', 'medium')}")
            if item.get('description'):
                formatted_items.append(f"   - 설명: {item.get('description')}")
            formatted_items.append("")
        
        return "\n".join(formatted_items)
    
    def _format_decisions(self, data: Dict[str, Any]) -> str:
        """결정사항 포맷팅"""
        decisions = data.get('decisions', [])
        if not decisions:
            return "결정사항이 없습니다."
        
        formatted_decisions = []
        for i, decision in enumerate(decisions, 1):
            formatted_decisions.append(f"{i}. **{decision.get('decision', 'N/A')}**")
            formatted_decisions.append(f"   - 이유: {decision.get('rationale', '미정')}")
            formatted_decisions.append(f"   - 영향도: {decision.get('impact', 'medium')}")
            if decision.get('stakeholders'):
                formatted_decisions.append(f"   - 관련자: {', '.join(decision.get('stakeholders', []))}")
            formatted_decisions.append("")
        
        return "\n".join(formatted_decisions)
