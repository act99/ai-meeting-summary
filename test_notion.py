#!/usr/bin/env python3
"""
Notion 연동 테스트 스크립트
"""

import os
from dotenv import load_dotenv
from notion_client import Client

def test_notion_connection():
    """Notion API 연결 테스트"""
    
    # .env 파일 로드
    load_dotenv()
    
    # 환경 변수 확인
    api_key = os.getenv('NOTION_API_KEY')
    database_id = os.getenv('NOTION_DATABASE_ID')
    
    print("🔍 Notion 설정 확인:")
    print(f"API Key: {'✅ 설정됨' if api_key else '❌ 없음'}")
    print(f"Database ID: {'✅ 설정됨' if database_id else '❌ 없음'}")
    
    if not api_key or not database_id:
        print("\n❌ 환경 변수가 설정되지 않았습니다.")
        print("📝 .env 파일을 확인하고 다음을 설정하세요:")
        print("   NOTION_API_KEY=your_integration_token")
        print("   NOTION_DATABASE_ID=your_database_id")
        return False
    
    try:
        # Notion 클라이언트 초기화
        client = Client(auth=api_key)
        
        # 데이터베이스 정보 조회
        print("\n🔗 Notion API 연결 테스트 중...")
        response = client.databases.retrieve(database_id=database_id)
        
        if response.get("id"):
            print("✅ Notion API 연결 성공!")
            print(f"📊 데이터베이스 제목: {response.get('title', [{}])[0].get('plain_text', 'N/A')}")
            
            # 간단한 페이지 생성 테스트
            print("\n📝 테스트 페이지 생성 중...")
            test_page = client.pages.create(
                parent={"database_id": database_id},
                properties={
                    "제목": {
                        "title": [
                            {
                                "text": {
                                    "content": "🧪 AI Meeting Summary 테스트"
                                }
                            }
                        ]
                    },
                    "회의 ID": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": "test_20250917"
                                }
                            }
                        ]
                    },
                    "상태": {
                        "select": {
                            "name": "테스트"
                        }
                    }
                }
            )
            
            print(f"✅ 테스트 페이지 생성 성공!")
            print(f"🔗 페이지 URL: {test_page.get('url', 'N/A')}")
            
            return True
            
        else:
            print("❌ 데이터베이스 조회 실패")
            return False
            
    except Exception as e:
        print(f"❌ Notion API 연결 실패: {e}")
        print("\n🔧 해결 방법:")
        print("1. Integration Token이 올바른지 확인")
        print("2. 데이터베이스 ID가 올바른지 확인")
        print("3. Integration에 데이터베이스 권한이 부여되었는지 확인")
        return False

if __name__ == "__main__":
    test_notion_connection()
