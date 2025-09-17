#!/usr/bin/env python3
"""
Notion 데이터베이스 속성 자동 추가 스크립트
"""

import os
from dotenv import load_dotenv
from notion_client import Client

def main():
    load_dotenv()
    
    api_key = os.getenv('NOTION_API_KEY')
    database_id = os.getenv('NOTION_DATABASE_ID')
    
    print("🔧 Notion 데이터베이스 속성 자동 추가")
    print(f"Database ID: {database_id}")
    
    if not api_key or not database_id:
        print("❌ 환경 변수 확인 필요")
        return
    
    try:
        client = Client(auth=api_key)
        
        # 현재 데이터베이스 조회
        db = client.databases.retrieve(database_id=database_id)
        current_props = db.get('properties', {})
        
        print(f"현재 속성: {list(current_props.keys())}")
        
        # 실제 코드에서 사용하는 속성들 (notion_client.py 기준)
        new_properties = {
            "제목": {
                "type": "title",
                "title": {}
            },
            "회의 ID": {
                "type": "rich_text",
                "rich_text": {}
            },
            "날짜": {
                "type": "date", 
                "date": {}
            },
            "지속시간": {
                "type": "number",
                "number": {"format": "number"}
            },
            "참석자": {
                "type": "multi_select",
                "multi_select": {"options": []}
            },
            "상태": {
                "type": "select",
                "select": {
                    "options": [
                        {"name": "완료", "color": "green"},
                        {"name": "진행중", "color": "yellow"},
                        {"name": "예정", "color": "blue"}
                    ]
                }
            }
        }
        
        # 기존 속성들을 비활성화하고 새로운 속성만 활성화
        print(f"기존 속성 비활성화 및 새로운 속성 활성화: {list(new_properties.keys())}")
        
        # 모든 속성을 비활성화 (None으로 설정)
        all_properties = {}
        for prop_name in current_props.keys():
            all_properties[prop_name] = None
        
        # 새로운 속성들 활성화
        for prop_name, prop_config in new_properties.items():
            all_properties[prop_name] = prop_config
        
        client.databases.update(
            database_id=database_id,
            properties=all_properties
        )
        print("✅ 속성 구조 교체 완료!")
            
        # 테스트 페이지 생성 (실제 코드 구조에 맞게)
        print("🧪 테스트 페이지 생성...")
        page = client.pages.create(
            parent={"database_id": database_id},
            properties={
                "제목": {"title": [{"text": {"content": "🧪 테스트 회의"}}]},
                "회의 ID": {"rich_text": [{"text": {"content": "test_001"}}]},
                "날짜": {"date": {"start": "2025-09-17"}},
                "지속시간": {"number": 30},
                "참석자": {"multi_select": [{"name": "테스터"}]},
                "상태": {"select": {"name": "완료"}}
            }
        )
        
        print(f"✅ 테스트 페이지 생성 성공!")
        print(f"URL: {page.get('url')}")
        
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    main()
