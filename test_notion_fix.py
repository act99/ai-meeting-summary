#!/usr/bin/env python3
"""
Notion 연결 테스트 스크립트
"""

import os
from dotenv import load_dotenv
from src.notion.notion_client import NotionClient
from src.notion.meeting_page_builder import MeetingPageBuilder
from datetime import datetime

def main():
    load_dotenv()
    
    print("🧪 Notion 연결 테스트")
    print("====================")
    
    try:
        # Notion 클라이언트 테스트
        print("\n1. Notion 클라이언트 연결 테스트...")
        notion_client = NotionClient()
        connection_ok = notion_client.test_connection()
        
        if connection_ok:
            print("✅ Notion 클라이언트 연결 성공")
        else:
            print("❌ Notion 클라이언트 연결 실패")
            return
        
        # 페이지 빌더 테스트
        print("\n2. 회의 페이지 빌더 테스트...")
        page_builder = MeetingPageBuilder()
        
        # 테스트 데이터 생성
        test_data = {
            "meeting_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "meeting_title": "테스트 회의",
            "timestamp": datetime.now().isoformat(),
            "summary": "이것은 테스트 회의 요약입니다.",
            "action_items": [
                {
                    "task": "테스트 작업",
                    "assignee": "테스터",
                    "deadline": "2025-09-18",
                    "priority": "high"
                }
            ],
            "decisions": [
                {
                    "decision": "테스트 결정사항",
                    "rationale": "테스트 목적",
                    "impact": "낮음"
                }
            ],
            "analysis": "테스트 분석 결과입니다.",
            "metadata": {
                "duration": 60,
                "speakers": ["테스터1", "테스터2"],
                "word_count": 100
            }
        }
        
        # 페이지 생성 테스트
        print("\n3. 테스트 페이지 생성...")
        result = page_builder.create_meeting_page(test_data)
        
        print(f"✅ 테스트 페이지 생성 성공!")
        print(f"   페이지 ID: {result['page_id']}")
        print(f"   URL: {result['url']}")
        
        # 페이지 목록 조회 테스트
        print("\n4. 페이지 목록 조회 테스트...")
        pages = notion_client.get_meeting_pages(limit=5)
        print(f"✅ 최근 {len(pages)}개 페이지 조회 성공")
        
        for i, page in enumerate(pages[:3], 1):
            title = page.get('properties', {}).get('제목', {}).get('title', [{}])[0].get('text', {}).get('content', 'N/A')
            print(f"   {i}. {title}")
        
        print("\n🎉 모든 테스트 통과!")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
