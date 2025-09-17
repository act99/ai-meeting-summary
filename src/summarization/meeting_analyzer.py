"""
Meeting Analyzer

회의 내용 분석 및 인사이트 추출
"""

import re
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
from collections import Counter

from ..utils.logger import LoggerMixin


class MeetingAnalyzer(LoggerMixin):
    """회의 분석 클래스"""
    
    def __init__(self):
        self.log_info("회의 분석기 초기화 완료")
    
    def analyze_speaker_participation(self, transcription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        화자 참여도 분석
        
        Args:
            transcription_data: 음성 인식 결과 데이터
        
        Returns:
            화자 참여도 분석 결과
        """
        try:
            text = transcription_data.get("full_text", "")
            speakers = transcription_data.get("speakers", [])
            
            # 화자별 발언 횟수 계산
            speaker_counts = {}
            for speaker in speakers:
                # 간단한 패턴 매칭으로 발언 횟수 계산
                pattern = rf"{re.escape(speaker)}[:\s]"
                count = len(re.findall(pattern, text, re.IGNORECASE))
                speaker_counts[speaker] = count
            
            # 참여도 분석
            total_speeches = sum(speaker_counts.values())
            participation_analysis = {}
            
            for speaker, count in speaker_counts.items():
                participation_rate = (count / total_speeches * 100) if total_speeches > 0 else 0
                participation_analysis[speaker] = {
                    "speech_count": count,
                    "participation_rate": round(participation_rate, 2),
                    "level": self._get_participation_level(participation_rate)
                }
            
            result = {
                "speaker_participation": participation_analysis,
                "total_speeches": total_speeches,
                "most_active_speaker": max(speaker_counts.items(), key=lambda x: x[1])[0] if speaker_counts else None,
                "least_active_speaker": min(speaker_counts.items(), key=lambda x: x[1])[0] if speaker_counts else None
            }
            
            self.log_info("화자 참여도 분석 완료")
            return result
            
        except Exception as e:
            self.log_error(f"화자 참여도 분석 실패: {e}")
            return {}
    
    def _get_participation_level(self, rate: float) -> str:
        """참여도 레벨 반환"""
        if rate >= 40:
            return "high"
        elif rate >= 20:
            return "medium"
        else:
            return "low"
    
    def analyze_topic_distribution(self, transcription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        주제 분포 분석
        
        Args:
            transcription_data: 음성 인식 결과 데이터
        
        Returns:
            주제 분포 분석 결과
        """
        try:
            text = transcription_data.get("full_text", "")
            
            # 주제별 키워드 정의
            topic_keywords = {
                "프로젝트 관리": ["프로젝트", "일정", "마감일", "진행상황", "스케줄"],
                "예산 및 자원": ["예산", "비용", "자원", "인력", "투자", "금액"],
                "기술 및 개발": ["개발", "기술", "코드", "시스템", "프로그램", "소프트웨어"],
                "마케팅 및 영업": ["마케팅", "영업", "고객", "판매", "홍보", "캠페인"],
                "인사 및 조직": ["인사", "조직", "채용", "교육", "평가", "팀"],
                "품질 관리": ["품질", "테스트", "검증", "오류", "버그", "개선"],
                "커뮤니케이션": ["소통", "회의", "보고", "피드백", "의견", "토론"]
            }
            
            # 주제별 언급 횟수 계산
            topic_counts = {}
            for topic, keywords in topic_keywords.items():
                count = 0
                for keyword in keywords:
                    count += len(re.findall(keyword, text, re.IGNORECASE))
                topic_counts[topic] = count
            
            # 상위 주제 추출
            top_topics = Counter(topic_counts).most_common(5)
            
            result = {
                "topic_distribution": topic_counts,
                "top_topics": [{"topic": topic, "count": count} for topic, count in top_topics],
                "most_discussed_topic": top_topics[0][0] if top_topics else None,
                "total_topic_mentions": sum(topic_counts.values())
            }
            
            self.log_info("주제 분포 분석 완료")
            return result
            
        except Exception as e:
            self.log_error(f"주제 분포 분석 실패: {e}")
            return {}
    
    def analyze_sentiment(self, transcription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        감정 분석 (간단한 휴리스틱)
        
        Args:
            transcription_data: 음성 인식 결과 데이터
        
        Returns:
            감정 분석 결과
        """
        try:
            text = transcription_data.get("full_text", "")
            
            # 감정 키워드 정의
            positive_keywords = [
                "좋다", "훌륭하다", "훌륭한", "성공", "성공적", "완벽", "완벽한",
                "만족", "만족스럽다", "기대", "기대된다", "긍정적", "긍정",
                "좋은", "잘", "잘했다", "잘하고", "잘됐다", "잘될", "잘할"
            ]
            
            negative_keywords = [
                "문제", "문제가", "어렵다", "어려운", "실패", "실패했다",
                "불만", "불만족", "부정적", "부정", "나쁘다", "나쁜",
                "걱정", "걱정된다", "우려", "우려된다", "위험", "위험하다",
                "어려움", "어려워", "힘들다", "힘든", "스트레스"
            ]
            
            neutral_keywords = [
                "확인", "확인하다", "검토", "검토하다", "논의", "논의하다",
                "보고", "보고하다", "진행", "진행하다", "계획", "계획하다"
            ]
            
            # 감정 점수 계산
            positive_count = sum(len(re.findall(keyword, text, re.IGNORECASE)) for keyword in positive_keywords)
            negative_count = sum(len(re.findall(keyword, text, re.IGNORECASE)) for keyword in negative_keywords)
            neutral_count = sum(len(re.findall(keyword, text, re.IGNORECASE)) for keyword in neutral_keywords)
            
            total_emotion_words = positive_count + negative_count + neutral_count
            
            if total_emotion_words > 0:
                positive_ratio = positive_count / total_emotion_words
                negative_ratio = negative_count / total_emotion_words
                neutral_ratio = neutral_count / total_emotion_words
            else:
                positive_ratio = negative_ratio = neutral_ratio = 0
            
            # 전체 감정 판정
            if positive_ratio > negative_ratio and positive_ratio > 0.3:
                overall_sentiment = "positive"
            elif negative_ratio > positive_ratio and negative_ratio > 0.3:
                overall_sentiment = "negative"
            else:
                overall_sentiment = "neutral"
            
            result = {
                "positive_count": positive_count,
                "negative_count": negative_count,
                "neutral_count": neutral_count,
                "positive_ratio": round(positive_ratio, 3),
                "negative_ratio": round(negative_ratio, 3),
                "neutral_ratio": round(neutral_ratio, 3),
                "overall_sentiment": overall_sentiment,
                "sentiment_score": round(positive_ratio - negative_ratio, 3)
            }
            
            self.log_info("감정 분석 완료")
            return result
            
        except Exception as e:
            self.log_error(f"감정 분석 실패: {e}")
            return {}
    
    def analyze_meeting_efficiency(self, transcription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        회의 효율성 분석
        
        Args:
            transcription_data: 음성 인식 결과 데이터
        
        Returns:
            회의 효율성 분석 결과
        """
        try:
            duration = transcription_data.get("duration", 0)
            word_count = transcription_data.get("word_count", 0)
            speakers = transcription_data.get("speakers", [])
            
            # 효율성 지표 계산
            words_per_minute = (word_count / (duration / 60)) if duration > 0 else 0
            speakers_count = len(speakers)
            
            # 효율성 평가
            efficiency_score = self._calculate_efficiency_score(words_per_minute, speakers_count, duration)
            
            # 개선 제안
            suggestions = self._generate_efficiency_suggestions(words_per_minute, speakers_count, duration)
            
            result = {
                "duration_minutes": duration / 60,
                "word_count": word_count,
                "words_per_minute": round(words_per_minute, 2),
                "speakers_count": speakers_count,
                "efficiency_score": efficiency_score,
                "efficiency_level": self._get_efficiency_level(efficiency_score),
                "suggestions": suggestions
            }
            
            self.log_info("회의 효율성 분석 완료")
            return result
            
        except Exception as e:
            self.log_error(f"회의 효율성 분석 실패: {e}")
            return {}
    
    def _calculate_efficiency_score(self, words_per_minute: float, speakers_count: int, duration: float) -> float:
        """효율성 점수 계산"""
        # 이상적인 값들
        ideal_wpm = 150  # 분당 150단어
        ideal_speakers = 5  # 이상적인 참석자 수
        ideal_duration = 60  # 이상적인 회의 시간 (분)
        
        # 점수 계산 (0-100)
        wpm_score = min(100, (words_per_minute / ideal_wpm) * 100)
        speakers_score = max(0, 100 - abs(speakers_count - ideal_speakers) * 10)
        duration_score = max(0, 100 - abs(duration / 60 - ideal_duration) * 5)
        
        # 가중 평균
        efficiency_score = (wpm_score * 0.4 + speakers_score * 0.3 + duration_score * 0.3)
        return round(efficiency_score, 2)
    
    def _get_efficiency_level(self, score: float) -> str:
        """효율성 레벨 반환"""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "average"
        else:
            return "poor"
    
    def _generate_efficiency_suggestions(self, words_per_minute: float, speakers_count: int, duration: float) -> List[str]:
        """효율성 개선 제안 생성"""
        suggestions = []
        
        if words_per_minute < 100:
            suggestions.append("회의 중 불필요한 침묵이 많습니다. 더 활발한 토론을 유도해보세요.")
        elif words_per_minute > 200:
            suggestions.append("회의가 너무 빠르게 진행됩니다. 참석자들이 따라갈 수 있도록 속도를 조절해보세요.")
        
        if speakers_count > 8:
            suggestions.append("참석자가 너무 많습니다. 핵심 인물만 참석하도록 조정해보세요.")
        elif speakers_count < 3:
            suggestions.append("참석자가 적습니다. 더 많은 관련자들의 참여를 고려해보세요.")
        
        if duration / 60 > 90:
            suggestions.append("회의 시간이 너무 깁니다. 90분 이내로 단축해보세요.")
        elif duration / 60 < 15:
            suggestions.append("회의 시간이 너무 짧습니다. 충분한 논의 시간을 확보해보세요.")
        
        if not suggestions:
            suggestions.append("회의 효율성이 양호합니다. 현재 방식을 유지하세요.")
        
        return suggestions
    
    def generate_meeting_insights(self, transcription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        종합 회의 인사이트 생성
        
        Args:
            transcription_data: 음성 인식 결과 데이터
        
        Returns:
            종합 인사이트
        """
        try:
            self.log_info("종합 회의 인사이트 생성 시작")
            
            # 각종 분석 수행
            participation_analysis = self.analyze_speaker_participation(transcription_data)
            topic_analysis = self.analyze_topic_distribution(transcription_data)
            sentiment_analysis = self.analyze_sentiment(transcription_data)
            efficiency_analysis = self.analyze_meeting_efficiency(transcription_data)
            
            # 종합 인사이트 구성
            insights = {
                "meeting_id": transcription_data.get("meeting_id", ""),
                "timestamp": datetime.now().isoformat(),
                "participation": participation_analysis,
                "topics": topic_analysis,
                "sentiment": sentiment_analysis,
                "efficiency": efficiency_analysis,
                "key_insights": self._generate_key_insights(
                    participation_analysis, topic_analysis, sentiment_analysis, efficiency_analysis
                )
            }
            
            self.log_info("종합 회의 인사이트 생성 완료")
            return insights
            
        except Exception as e:
            self.log_error(f"종합 회의 인사이트 생성 실패: {e}")
            return {}
    
    def _generate_key_insights(self, participation: Dict, topics: Dict, sentiment: Dict, efficiency: Dict) -> List[str]:
        """핵심 인사이트 생성"""
        insights = []
        
        # 참여도 인사이트
        if participation.get("most_active_speaker"):
            insights.append(f"가장 활발한 참석자: {participation['most_active_speaker']}")
        
        # 주제 인사이트
        if topics.get("most_discussed_topic"):
            insights.append(f"가장 많이 논의된 주제: {topics['most_discussed_topic']}")
        
        # 감정 인사이트
        sentiment_score = sentiment.get("sentiment_score", 0)
        if sentiment_score > 0.1:
            insights.append("회의 분위기가 긍정적입니다.")
        elif sentiment_score < -0.1:
            insights.append("회의 분위기가 부정적입니다.")
        else:
            insights.append("회의 분위기가 중립적입니다.")
        
        # 효율성 인사이트
        efficiency_level = efficiency.get("efficiency_level", "unknown")
        if efficiency_level == "excellent":
            insights.append("회의 효율성이 매우 우수합니다.")
        elif efficiency_level == "poor":
            insights.append("회의 효율성 개선이 필요합니다.")
        
        return insights
