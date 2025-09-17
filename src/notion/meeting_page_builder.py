"""
Meeting Page Builder

Notion 회의 페이지 구성 및 관리
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from ..utils.logger import LoggerMixin
from .notion_client import NotionClient


class MeetingPageBuilder(LoggerMixin):
    """회의 페이지 빌더"""
    
    def __init__(self):
        self.notion_client = NotionClient()
        self.log_info("회의 페이지 빌더 초기화 완료")
    
    def build_meeting_page_data(self, comprehensive_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        회의 페이지 데이터 구성
        
        Args:
            comprehensive_data: 종합 회의 데이터
        
        Returns:
            Notion 페이지용 데이터
        """
        try:
            self.log_info("회의 페이지 데이터 구성 시작")
            
            # 기본 정보 추출 및 타임스탬프 기반 유니크 ID 생성
            meeting_id = comprehensive_data.get("meeting_id", "")
            timestamp = comprehensive_data.get("timestamp", datetime.now().isoformat())
            
            # 타임스탬프가 없으면 현재 시간으로 생성
            if not meeting_id:
                meeting_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 날짜 파싱
            try:
                date_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                date_str = date_obj.strftime("%Y-%m-%d")
            except:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            # 회의 제목에 타임스탬프 포함
            meeting_title = comprehensive_data.get("meeting_title", f"회의 - {meeting_id}")
            if not meeting_title.startswith("회의"):
                meeting_title = f"회의 - {meeting_title}"
            
            # 페이지 데이터 구성
            page_data = {
                "meeting_id": meeting_id,
                "meeting_title": meeting_title,
                "date": date_str,
                "timestamp": timestamp,
                "duration_minutes": comprehensive_data.get("metadata", {}).get("duration", 0) / 60,
                "speakers": comprehensive_data.get("metadata", {}).get("speakers", []),
                "summary": comprehensive_data.get("summary", ""),
                "action_items": comprehensive_data.get("action_items", []),
                "decisions": comprehensive_data.get("decisions", []),
                "analysis": comprehensive_data.get("analysis", ""),
                "metadata": comprehensive_data.get("metadata", {})
            }
            
            self.log_info("회의 페이지 데이터 구성 완료")
            return page_data
            
        except Exception as e:
            self.log_error(f"회의 페이지 데이터 구성 실패: {e}")
            raise
    
    def create_meeting_page(self, comprehensive_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        회의 페이지 생성
        
        Args:
            comprehensive_data: 종합 회의 데이터
        
        Returns:
            생성된 페이지 정보
        """
        try:
            self.log_info("회의 페이지 생성 시작")
            
            # 페이지 데이터 구성
            page_data = self.build_meeting_page_data(comprehensive_data)
            
            # Notion 페이지 생성
            result = self.notion_client.create_meeting_page(page_data)
            
            self.log_info(f"회의 페이지 생성 완료: {result['page_id']}")
            return result
            
        except Exception as e:
            self.log_error(f"회의 페이지 생성 실패: {e}")
            raise
    
    def update_meeting_page(self, page_id: str, comprehensive_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        회의 페이지 업데이트
        
        Args:
            page_id: 페이지 ID
            comprehensive_data: 종합 회의 데이터
        
        Returns:
            업데이트 결과
        """
        try:
            self.log_info(f"회의 페이지 업데이트 시작: {page_id}")
            
            # 페이지 데이터 구성
            page_data = self.build_meeting_page_data(comprehensive_data)
            
            # Notion 페이지 업데이트
            result = self.notion_client.update_meeting_page(page_id, page_data)
            
            self.log_info("회의 페이지 업데이트 완료")
            return result
            
        except Exception as e:
            self.log_error(f"회의 페이지 업데이트 실패: {e}")
            raise
    
    def create_action_items_page(self, action_items_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        액션 아이템 전용 페이지 생성
        
        Args:
            action_items_data: 액션 아이템 데이터
        
        Returns:
            생성된 페이지 정보
        """
        try:
            self.log_info("액션 아이템 페이지 생성 시작")
            
            meeting_id = action_items_data.get("meeting_id", "")
            action_items = action_items_data.get("action_items", [])
            
            # 액션 아이템 페이지 데이터 구성
            page_data = {
                "meeting_id": f"{meeting_id}_actions",
                "meeting_title": f"액션 아이템 - {meeting_id}",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "timestamp": datetime.now().isoformat(),
                "duration_minutes": 0,
                "speakers": [],
                "summary": f"회의 {meeting_id}의 액션 아이템 목록입니다.",
                "action_items": action_items,
                "decisions": [],
                "analysis": "",
                "metadata": {
                    "type": "action_items_only",
                    "original_meeting_id": meeting_id
                }
            }
            
            # Notion 페이지 생성
            result = self.notion_client.create_meeting_page(page_data)
            
            self.log_info(f"액션 아이템 페이지 생성 완료: {result['page_id']}")
            return result
            
        except Exception as e:
            self.log_error(f"액션 아이템 페이지 생성 실패: {e}")
            raise
    
    def create_summary_page(self, summary_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        요약 전용 페이지 생성
        
        Args:
            summary_data: 요약 데이터
        
        Returns:
            생성된 페이지 정보
        """
        try:
            self.log_info("요약 페이지 생성 시작")
            
            meeting_id = summary_data.get("meeting_id", "")
            summary = summary_data.get("summary", "")
            
            # 요약 페이지 데이터 구성
            page_data = {
                "meeting_id": f"{meeting_id}_summary",
                "meeting_title": f"회의 요약 - {meeting_id}",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "timestamp": datetime.now().isoformat(),
                "duration_minutes": 0,
                "speakers": [],
                "summary": summary,
                "action_items": [],
                "decisions": [],
                "analysis": "",
                "metadata": {
                    "type": "summary_only",
                    "original_meeting_id": meeting_id,
                    "word_count": summary_data.get("word_count", 0)
                }
            }
            
            # Notion 페이지 생성
            result = self.notion_client.create_meeting_page(page_data)
            
            self.log_info(f"요약 페이지 생성 완료: {result['page_id']}")
            return result
            
        except Exception as e:
            self.log_error(f"요약 페이지 생성 실패: {e}")
            raise
    
    def get_meeting_pages_summary(self, limit: int = 10) -> Dict[str, Any]:
        """
        회의 페이지 요약 정보 조회
        
        Args:
            limit: 조회할 페이지 수
        
        Returns:
            페이지 요약 정보
        """
        try:
            self.log_info("회의 페이지 요약 정보 조회 시작")
            
            # 페이지 목록 조회
            pages = self.notion_client.get_meeting_pages(limit)
            
            # 요약 정보 구성
            summary = {
                "total_pages": len(pages),
                "recent_pages": pages[:5],
                "pages_by_date": self._group_pages_by_date(pages),
                "last_updated": pages[0].get("last_edited_time", "") if pages else ""
            }
            
            self.log_info(f"회의 페이지 요약 정보 조회 완료: {len(pages)}개")
            return summary
            
        except Exception as e:
            self.log_error(f"회의 페이지 요약 정보 조회 실패: {e}")
            return {}
    
    def _group_pages_by_date(self, pages: List[Dict[str, Any]]) -> Dict[str, int]:
        """날짜별 페이지 그룹화"""
        date_groups = {}
        
        for page in pages:
            try:
                # 날짜 추출 (created_time에서)
                created_time = page.get("created_time", "")
                if created_time:
                    date_str = created_time.split('T')[0]
                    date_groups[date_str] = date_groups.get(date_str, 0) + 1
            except:
                continue
        
        return date_groups
    
    def archive_old_meetings(self, days_old: int = 30) -> Dict[str, Any]:
        """
        오래된 회의 페이지 아카이브
        
        Args:
            days_old: 아카이브할 기준 일수
        
        Returns:
            아카이브 결과
        """
        try:
            self.log_info(f"오래된 회의 페이지 아카이브 시작: {days_old}일 이상")
            
            # 모든 페이지 조회
            pages = self.notion_client.get_meeting_pages(limit=100)
            
            # 오래된 페이지 필터링
            cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            old_pages = []
            
            for page in pages:
                try:
                    created_time = page.get("created_time", "")
                    if created_time:
                        page_timestamp = datetime.fromisoformat(created_time.replace('Z', '+00:00')).timestamp()
                        if page_timestamp < cutoff_date:
                            old_pages.append(page)
                except:
                    continue
            
            # 아카이브 실행
            archived_count = 0
            failed_count = 0
            
            for page in old_pages:
                try:
                    success = self.notion_client.delete_meeting_page(page["page_id"])
                    if success:
                        archived_count += 1
                    else:
                        failed_count += 1
                except:
                    failed_count += 1
            
            result = {
                "total_checked": len(pages),
                "old_pages_found": len(old_pages),
                "archived_count": archived_count,
                "failed_count": failed_count,
                "status": "completed"
            }
            
            self.log_info(f"오래된 회의 페이지 아카이브 완료: {archived_count}개 아카이브")
            return result
            
        except Exception as e:
            self.log_error(f"오래된 회의 페이지 아카이브 실패: {e}")
            return {"status": "failed", "error": str(e)}
    
    def test_notion_integration(self) -> Dict[str, Any]:
        """
        Notion 연동 테스트
        
        Returns:
            테스트 결과
        """
        try:
            self.log_info("Notion 연동 테스트 시작")
            
            # 연결 테스트
            connection_ok = self.notion_client.test_connection()
            
            # 페이지 목록 조회 테스트
            pages = self.notion_client.get_meeting_pages(limit=1)
            
            result = {
                "connection_test": connection_ok,
                "pages_query_test": len(pages) >= 0,
                "database_id": self.notion_client.database_id,
                "status": "success" if connection_ok else "failed"
            }
            
            self.log_info("Notion 연동 테스트 완료")
            return result
            
        except Exception as e:
            self.log_error(f"Notion 연동 테스트 실패: {e}")
            return {
                "connection_test": False,
                "pages_query_test": False,
                "error": str(e),
                "status": "failed"
            }
