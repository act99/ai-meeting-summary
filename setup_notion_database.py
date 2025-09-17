#!/usr/bin/env python3
"""
Notion 데이터베이스 자동 설정 스크립트
MCP를 사용하여 필요한 속성들을 자동으로 추가합니다.
"""

import os
import json
from dotenv import load_dotenv
from notion_client import Client
from typing import Dict, List, Any

def setup_notion_database():
    """Notion 데이터베이스 자동 설정"""
    
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
        return False
    
    try:
        # Notion 클라이언트 초기화
        client = Client(auth=api_key)
        
        # 현재 데이터베이스 정보 조회
        print("\n📊 현재 데이터베이스 정보 조회 중...")
        database = client.databases.retrieve(database_id=database_id)
        
        print(f"데이터베이스 제목: {database.get('title', [{}])[0].get('plain_text', 'N/A')}")
        
        # 현재 속성들 확인
        current_properties = database.get('properties', {})
        print(f"\n현재 속성들: {list(current_properties.keys())}")
        
        # 필요한 속성들 정의
        required_properties = {
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
                "number": {
                    "format": "number"
                }
            },
            "참석자": {
                "type": "multi_select",
                "multi_select": {
                    "options": []
                }
            },
            "상태": {
                "type": "select",
                "select": {
                    "options": [
                        {
                            "name": "완료",
                            "color": "green"
                        },
                        {
                            "name": "진행중", 
                            "color": "yellow"
                        },
                        {
                            "name": "예정",
                            "color": "blue"
                        }
                    ]
                }
            }
        }
        
        # 누락된 속성들 확인
        missing_properties = {}
        for prop_name, prop_config in required_properties.items():
            if prop_name not in current_properties:
                missing_properties[prop_name] = prop_config
                print(f"❌ 누락된 속성: {prop_name}")
            else:
                print(f"✅ 기존 속성: {prop_name}")
        
        if not missing_properties:
            print("\n🎉 모든 필요한 속성이 이미 존재합니다!")
            return True
        
        # 누락된 속성들 추가
        print(f"\n🔧 {len(missing_properties)}개 속성 추가 중...")
        
        # 데이터베이스 업데이트
        update_data = {
            "properties": missing_properties
        }
        
        updated_database = client.databases.update(
            database_id=database_id,
            properties=update_data
        )
        
        print("✅ 데이터베이스 속성 추가 완료!")
        
        # 추가된 속성들 확인
        new_properties = updated_database.get('properties', {})
        print(f"\n📋 최종 속성 목록:")
        for prop_name in required_properties.keys():
            if prop_name in new_properties:
                print(f"  ✅ {prop_name}")
            else:
                print(f"  ❌ {prop_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 설정 실패: {e}")
        print("\n🔧 해결 방법:")
        print("1. Integration Token이 올바른지 확인")
        print("2. 데이터베이스 ID가 올바른지 확인") 
        print("3. Integration에 데이터베이스 권한이 부여되었는지 확인")
        return False

def test_database_creation():
    """데이터베이스 생성 테스트"""
    
    load_dotenv()
    api_key = os.getenv('NOTION_API_KEY')
    database_id = os.getenv('NOTION_DATABASE_ID')
    
    if not api_key or not database_id:
        print("❌ 환경 변수가 설정되지 않았습니다.")
        return False
    
    try:
        client = Client(auth=api_key)
        
        print("\n🧪 테스트 페이지 생성 중...")
        
        # 테스트 페이지 생성
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
                "날짜": {
                    "date": {
                        "start": "2025-09-17"
                    }
                },
                "지속시간": {
                    "number": 30
                },
                "참석자": {
                    "multi_select": [
                        {"name": "테스트 사용자"}
                    ]
                },
                "상태": {
                    "select": {
                        "name": "완료"
                    }
                }
            }
        )
        
        print(f"✅ 테스트 페이지 생성 성공!")
        print(f"🔗 페이지 URL: {test_page.get('url', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 페이지 생성 실패: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Notion 데이터베이스 자동 설정 시작")
    print("=" * 50)
    
    # 데이터베이스 설정
    if setup_notion_database():
        print("\n🧪 테스트 페이지 생성 중...")
        test_database_creation()
    
    print("\n🎉 설정 완료!")
