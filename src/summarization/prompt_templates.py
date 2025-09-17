"""
Prompt Templates for Meeting Summarization

회의 요약을 위한 GPT 프롬프트 템플릿
"""

from typing import Dict, Any, List
from datetime import datetime


class PromptTemplates:
    """회의 요약 프롬프트 템플릿 클래스"""
    
    @staticmethod
    def get_meeting_summary_prompt(transcription_data: Dict[str, Any]) -> str:
        """회의 요약 프롬프트 생성 (Notion 최적화)"""
        
        meeting_info = f"""
회의 정보:
- 회의 ID: {transcription_data.get('meeting_id', 'N/A')}
- 시간: {transcription_data.get('timestamp', 'N/A')}
- 지속시간: {transcription_data.get('duration', 0):.1f}초
- 언어: {transcription_data.get('language', 'ko')}
- 참석자: {', '.join(transcription_data.get('speakers', []))}
"""
        
        main_prompt = f"""
당신은 전문적인 회의 요약 전문가입니다. 다음 회의 내용을 분석하고 Notion에 저장하기 적합한 구조화된 요약을 작성해주세요.

{meeting_info}

회의 내용:
{transcription_data.get('full_text', '')}

다음 형식으로 요약해주세요. 마크다운 헤더(#)는 사용하지 말고, 일반 텍스트로 작성해주세요:

📋 회의 요약

🎯 회의 개요
- 목적: 회의의 주요 목적과 목표
- 참석자: 참석자 목록 및 역할
- 주요 안건: 논의된 주요 주제들

💡 핵심 내용
- 주요 논의사항: 중요한 토론 내용
- 핵심 포인트: 기억해야 할 핵심 내용
- 문제점: 식별된 문제나 이슈

✅ 결정사항
- 확정된 사항: 최종 결정된 내용들
- 합의사항: 참석자들이 합의한 내용

📝 액션 아이템
- 담당자별 업무: 각 담당자가 해야 할 일
- 마감일: 각 업무의 마감일
- 우선순위: 중요도에 따른 우선순위

🔄 다음 단계
- 후속 조치: 다음에 해야 할 일
- 다음 회의: 다음 회의 계획

📊 회의 평가
- 효과성: 회의의 효과성 평가
- 개선점: 향후 개선할 점

한국어로 작성하고, 명확하고 구체적으로 작성해주세요. 마크다운 문법은 사용하지 마세요.
"""
        
        return main_prompt
    
    @staticmethod
    def get_action_items_extraction_prompt(transcription_data: Dict[str, Any]) -> str:
        """액션 아이템 추출 프롬프트"""
        
        prompt = f"""
다음 회의 내용에서 액션 아이템을 추출해주세요.

회의 내용:
{transcription_data.get('full_text', '')}

다음 JSON 형식으로 응답해주세요:

{{
    "action_items": [
        {{
            "task": "구체적인 업무 내용",
            "assignee": "담당자",
            "deadline": "마감일",
            "priority": "high/medium/low",
            "description": "상세 설명"
        }}
    ]
}}

담당자가 명시되지 않은 경우 "미정"으로 표시하고, 마감일이 없는 경우 "미정"으로 표시해주세요.
"""
        
        return prompt
    
    @staticmethod
    def get_decision_extraction_prompt(transcription_data: Dict[str, Any]) -> str:
        """결정사항 추출 프롬프트"""
        
        prompt = f"""
다음 회의 내용에서 결정사항을 추출해주세요.

회의 내용:
{transcription_data.get('full_text', '')}

다음 JSON 형식으로 응답해주세요:

{{
    "decisions": [
        {{
            "decision": "결정된 내용",
            "rationale": "결정 이유",
            "impact": "영향도",
            "stakeholders": ["관련자1", "관련자2"]
        }}
    ]
}}
"""
        
        return prompt
    
    @staticmethod
    def get_key_points_extraction_prompt(transcription_data: Dict[str, Any]) -> str:
        """핵심 포인트 추출 프롬프트"""
        
        prompt = f"""
다음 회의 내용에서 핵심 포인트를 추출해주세요.

회의 내용:
{transcription_data.get('full_text', '')}

다음 JSON 형식으로 응답해주세요:

{{
    "key_points": [
        {{
            "point": "핵심 포인트",
            "category": "주제 분류",
            "importance": "high/medium/low",
            "context": "배경 설명"
        }}
    ]
}}
"""
        
        return prompt
    
    @staticmethod
    def get_meeting_analysis_prompt(transcription_data: Dict[str, Any]) -> str:
        """회의 분석 프롬프트 (Notion 최적화)"""
        
        prompt = f"""
다음 회의를 분석하고 종합적인 평가를 해주세요.

회의 내용:
{transcription_data.get('full_text', '')}

다음 형식으로 분석해주세요. 마크다운 헤더(#)는 사용하지 말고, 일반 텍스트로 작성해주세요:

📊 회의 분석

🎯 목표 달성도
- 달성된 목표: 성공적으로 달성한 목표들
- 미달성 목표: 달성하지 못한 목표들
- 달성률: 전체 목표 대비 달성률 (%)

💬 참여도 분석
- 적극적 참여자: 활발히 참여한 참석자들
- 참여도가 낮은 참석자: 상대적으로 조용했던 참석자들
- 균형성: 참석자 간 참여도 균형

⏰ 시간 효율성
- 시간 활용도: 회의 시간의 효율적 활용 정도
- 불필요한 시간: 낭비된 시간이나 비효율적 구간
- 개선 제안: 시간 효율성 개선 방안

🔍 의사소통 품질
- 명확성: 의사소통의 명확성 정도
- 이해도: 서로의 의견 이해도
- 갈등: 발생한 갈등이나 의견 차이

📈 성과 평가
- 긍정적 요소: 잘된 점들
- 개선 필요 요소: 개선이 필요한 점들
- 다음 회의 준비사항: 다음 회의를 위한 준비사항

마크다운 문법은 사용하지 마세요.
"""
        
        return prompt
    
    @staticmethod
    def get_notion_format_prompt(summary_data: Dict[str, Any]) -> str:
        """Notion 저장용 포맷 프롬프트"""
        
        prompt = f"""
다음 회의 요약을 Notion 페이지에 저장하기 적합한 형식으로 변환해주세요.

회의 요약:
{summary_data.get('summary', '')}

다음 형식으로 작성해주세요:

# 회의 요약 - {summary_data.get('meeting_id', 'N/A')}

## 📅 회의 정보
- **날짜**: {summary_data.get('timestamp', 'N/A')}
- **지속시간**: {summary_data.get('duration', 0):.1f}초
- **참석자**: {', '.join(summary_data.get('speakers', []))}

## 📋 요약 내용
{summary_data.get('summary', '')}

## ✅ 액션 아이템
{summary_data.get('action_items', '')}

## 📊 메타데이터
- **단어 수**: {summary_data.get('word_count', 0)}
- **생성 시간**: {datetime.now().isoformat()}

Notion의 블록 형식에 맞게 작성해주세요.
"""
        
        return prompt
    
    @staticmethod
    def get_short_summary_prompt(transcription_data: Dict[str, Any]) -> str:
        """간단한 요약 프롬프트"""
        
        prompt = f"""
다음 회의 내용을 3-5문장으로 간단히 요약해주세요.

회의 내용:
{transcription_data.get('full_text', '')}

핵심만 간결하게 요약해주세요.
"""
        
        return prompt
    
    @staticmethod
    def get_detailed_summary_prompt(transcription_data: Dict[str, Any]) -> str:
        """상세한 요약 프롬프트"""
        
        prompt = f"""
다음 회의 내용을 상세하고 포괄적으로 요약해주세요.

회의 내용:
{transcription_data.get('full_text', '')}

다음 요소들을 모두 포함하여 상세히 작성해주세요:
1. 회의 배경 및 목적
2. 주요 논의사항 (시간순)
3. 각 참석자의 주요 발언
4. 결정사항 및 합의사항
5. 액션 아이템 및 담당자
6. 다음 단계 및 후속 조치
7. 회의 평가 및 개선점

최소 500자 이상으로 작성해주세요.
"""
        
        return prompt
