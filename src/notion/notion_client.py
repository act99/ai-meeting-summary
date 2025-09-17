"""
Notion API Client

Notion API를 통한 회의록 저장 및 관리
"""

from notion_client import Client
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from ..utils.logger import LoggerMixin
from ..utils.config import config


class NotionClient(LoggerMixin):
    """Notion API 클라이언트"""
    
    def __init__(self):
        self.client = Client(auth=config.api.notion_api_key)
        self.database_id = config.api.notion_database_id
        self.log_info(f"Notion 클라이언트 초기화 완료 - 데이터베이스: {self.database_id}")
    
    def create_meeting_page(self, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        회의 페이지 생성
        
        Args:
            meeting_data: 회의 데이터
        
        Returns:
            생성된 페이지 정보
        """
        try:
            self.log_info("Notion 회의 페이지 생성 시작")
            
            # 페이지 속성 구성
            properties = self._build_page_properties(meeting_data)
            
            # 페이지 생성
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            page_id = response["id"]
            
            # 페이지 내용 추가
            self._add_page_content(page_id, meeting_data)
            
            result = {
                "page_id": page_id,
                "url": response.get("url", ""),
                "created_time": response.get("created_time", ""),
                "status": "success"
            }
            
            self.log_info(f"Notion 회의 페이지 생성 완료: {page_id}")
            return result
            
        except Exception as e:
            self.log_error(f"Notion 회의 페이지 생성 실패: {e}")
            raise
    
    def _build_page_properties(self, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """페이지 속성 구성 (기존 한국어 속성명 사용)"""
        # 타임스탬프를 포함한 유니크한 회의 ID 생성
        meeting_id = meeting_data.get("meeting_id", "")
        if not meeting_id:
            meeting_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 회의 제목에 타임스탬프 포함
        meeting_title = meeting_data.get("meeting_title", f"회의 - {meeting_id}")
        if not meeting_title.startswith("회의"):
            meeting_title = f"회의 - {meeting_title} ({meeting_id})"
        
        properties = {
            "제목": {
                "title": [
                    {
                        "text": {
                            "content": meeting_title
                        }
                    }
                ]
            },
            "회의 ID": {
                "rich_text": [
                    {
                        "text": {
                            "content": meeting_id
                        }
                    }
                ]
            },
            "날짜": {
                "date": {
                    "start": meeting_data.get("date", datetime.now().isoformat().split('T')[0])
                }
            },
            "지속시간": {
                "number": meeting_data.get("duration_minutes", 0)
            },
            "참석자": {
                "multi_select": [
                    {"name": speaker} for speaker in meeting_data.get("speakers", [])
                ]
            },
            "상태": {
                "select": {
                    "name": "완료"
                }
            }
        }
        
        return properties
    
    def _add_page_content(self, page_id: str, meeting_data: Dict[str, Any]) -> None:
        """페이지 내용 추가"""
        try:
            # 블록 구성
            blocks = self._build_content_blocks(meeting_data)
            
            # 블록 추가
            self.client.blocks.children.append(
                block_id=page_id,
                children=blocks
            )
            
            self.log_info("페이지 내용 추가 완료")
            
        except Exception as e:
            self.log_error(f"페이지 내용 추가 실패: {e}")
            raise
    
    def _clean_markdown_headers(self, text: str) -> str:
        """마크다운 헤더 제거"""
        import re
        # #, ##, ### 헤더 제거
        cleaned_text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
        return cleaned_text.strip()
    
    def _build_content_blocks(self, meeting_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """콘텐츠 블록 구성"""
        blocks = []
        
        # 회의 요약 헤더
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "📋 회의 요약"
                        }
                    }
                ]
            }
        })
        
        # 요약 내용 (마크다운 헤더 제거)
        summary = meeting_data.get("summary", "")
        if summary:
            cleaned_summary = self._clean_markdown_headers(summary)
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": cleaned_summary
                            }
                        }
                    ]
                }
            })
        
        # 액션 아이템 헤더
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "✅ 액션 아이템"
                        }
                    }
                ]
            }
        })
        
        # 액션 아이템 목록
        action_items = meeting_data.get("action_items", [])
        if action_items:
            for item in action_items:
                blocks.append({
                    "object": "block",
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"{item.get('task', '')} (담당자: {item.get('assignee', '미정')}, 마감일: {item.get('deadline', '미정')})"
                                }
                            }
                        ],
                        "checked": False
                    }
                })
        else:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "액션 아이템이 없습니다."
                            }
                        }
                    ]
                }
            })
        
        # 결정사항 헤더
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "📊 결정사항"
                        }
                    }
                ]
            }
        })
        
        # 결정사항 목록
        decisions = meeting_data.get("decisions", [])
        if decisions:
            for decision in decisions:
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": decision.get("decision", "")
                                }
                            }
                        ]
                    }
                })
        else:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "결정사항이 없습니다."
                            }
                        }
                    ]
                }
            })
        
        # 분석 결과 헤더
        if meeting_data.get("analysis"):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "🔍 회의 분석"
                            }
                        }
                    ]
                }
            })
            
            # 분석 내용 (마크다운 헤더 제거)
            analysis = meeting_data.get("analysis", "")
            cleaned_analysis = self._clean_markdown_headers(analysis)
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": cleaned_analysis
                            }
                        }
                    ]
                }
            })
        
        # 메타데이터 헤더
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "📊 메타데이터"
                        }
                    }
                ]
            }
        })
        
        # 메타데이터 테이블
        metadata = meeting_data.get("metadata", {})
        metadata_text = f"""
- 생성 시간: {meeting_data.get('timestamp', 'N/A')}
- 모델: {metadata.get('model_used', 'N/A')}
- 지속시간: {metadata.get('duration', 0):.1f}초
- 단어 수: {metadata.get('word_count', 0)}
- 언어: {metadata.get('language', 'ko')}
"""
        
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": metadata_text.strip()
                        }
                    }
                ]
            }
        })
        
        return blocks
    
    def update_meeting_page(self, page_id: str, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        회의 페이지 업데이트
        
        Args:
            page_id: 페이지 ID
            meeting_data: 업데이트할 회의 데이터
        
        Returns:
            업데이트 결과
        """
        try:
            self.log_info(f"Notion 페이지 업데이트 시작: {page_id}")
            
            # 속성 업데이트
            properties = self._build_page_properties(meeting_data)
            self.client.pages.update(page_id=page_id, properties=properties)
            
            # 기존 블록 삭제 후 새로 추가
            self._clear_page_content(page_id)
            self._add_page_content(page_id, meeting_data)
            
            result = {
                "page_id": page_id,
                "status": "success",
                "updated_time": datetime.now().isoformat()
            }
            
            self.log_info("Notion 페이지 업데이트 완료")
            return result
            
        except Exception as e:
            self.log_error(f"Notion 페이지 업데이트 실패: {e}")
            raise
    
    def _clear_page_content(self, page_id: str) -> None:
        """페이지 내용 삭제"""
        try:
            # 기존 블록 조회
            response = self.client.blocks.children.list(block_id=page_id)
            
            # 블록 삭제
            for block in response.get("results", []):
                if block["type"] != "child_page":  # 페이지 자체는 삭제하지 않음
                    self.client.blocks.delete(block_id=block["id"])
            
            self.log_info("페이지 내용 삭제 완료")
            
        except Exception as e:
            self.log_error(f"페이지 내용 삭제 실패: {e}")
    
    def get_meeting_pages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        회의 페이지 목록 조회
        
        Args:
            limit: 조회할 페이지 수
        
        Returns:
            페이지 목록
        """
        try:
            self.log_info("Notion 회의 페이지 목록 조회 시작")
            
            response = self.client.databases.query(
                database_id=self.database_id,
                page_size=limit,
                sorts=[
                    {
                        "property": "날짜",
                        "direction": "descending"
                    }
                ]
            )
            
            pages = []
            for page in response.get("results", []):
                page_info = {
                    "page_id": page["id"],
                    "title": self._extract_title(page),
                    "url": page.get("url", ""),
                    "created_time": page.get("created_time", ""),
                    "last_edited_time": page.get("last_edited_time", "")
                }
                pages.append(page_info)
            
            self.log_info(f"회의 페이지 목록 조회 완료: {len(pages)}개")
            return pages
            
        except Exception as e:
            self.log_error(f"회의 페이지 목록 조회 실패: {e}")
            return []
    
    def _extract_title(self, page: Dict[str, Any]) -> str:
        """페이지에서 제목 추출"""
        try:
            properties = page.get("properties", {})
            title_property = properties.get("제목", {})
            title_array = title_property.get("title", [])
            
            if title_array:
                return title_array[0].get("text", {}).get("content", "")
            return "제목 없음"
            
        except Exception:
            return "제목 추출 실패"
    
    def delete_meeting_page(self, page_id: str) -> bool:
        """
        회의 페이지 삭제
        
        Args:
            page_id: 페이지 ID
        
        Returns:
            삭제 성공 여부
        """
        try:
            self.log_info(f"Notion 페이지 삭제 시작: {page_id}")
            
            self.client.pages.update(
                page_id=page_id,
                archived=True
            )
            
            self.log_info("Notion 페이지 삭제 완료")
            return True
            
        except Exception as e:
            self.log_error(f"Notion 페이지 삭제 실패: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Notion API 연결 테스트
        
        Returns:
            연결 성공 여부
        """
        try:
            self.log_info("Notion API 연결 테스트 시작")
            
            # 데이터베이스 정보 조회
            response = self.client.databases.retrieve(database_id=self.database_id)
            
            if response.get("id"):
                self.log_info("Notion API 연결 테스트 성공")
                return True
            else:
                self.log_error("Notion API 연결 테스트 실패")
                return False
                
        except Exception as e:
            self.log_error(f"Notion API 연결 테스트 실패: {e}")
            return False
