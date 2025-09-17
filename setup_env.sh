#!/bin/bash

# 환경 변수 설정 도우미 스크립트
# .env 파일 생성 및 편집 안내

echo "🔧 AI Meeting Summary - 환경 변수 설정"
echo "======================================"
echo ""

# .env 파일이 이미 있는지 확인
if [ -f ".env" ]; then
    echo "⚠️  .env 파일이 이미 존재합니다."
    echo ""
    read -p "기존 파일을 덮어쓰시겠습니까? (y/n): " overwrite
    
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo "❌ 설정이 취소되었습니다."
        exit 1
    fi
fi

# env.example을 .env로 복사
echo "📝 .env 파일 생성 중..."
cp env.example .env

echo ""
echo "✅ .env 파일이 생성되었습니다!"
echo ""
echo "📋 다음 API 키들을 설정해주세요:"
echo ""
echo "1. OpenAI API Key"
echo "   - https://platform.openai.com/api-keys 에서 발급"
echo "   - OPENAI_API_KEY=sk-..."
echo ""
echo "2. Notion Integration Token"
echo "   - https://developers.notion.com/ 에서 Integration 생성"
echo "   - NOTION_API_KEY=secret_..."
echo ""
echo "3. Notion Database ID"
echo "   - Notion 데이터베이스 URL에서 추출"
echo "   - NOTION_DATABASE_ID=abc123-def456-..."
echo ""

# 편집기 선택
echo "📝 .env 파일을 편집하시겠습니까?"
echo "1) nano (간단한 편집기)"
echo "2) vim (고급 편집기)"
echo "3) 직접 편집 (나중에)"
echo "4) 현재 편집기로 열기"

read -p "선택 (1-4): " editor_choice

case $editor_choice in
    1)
        nano .env
        ;;
    2)
        vim .env
        ;;
    3)
        echo "📝 나중에 다음 명령어로 편집하세요:"
        echo "   nano .env"
        echo "   # 또는"
        echo "   vim .env"
        ;;
    4)
        ${EDITOR:-nano} .env
        ;;
    *)
        echo "❌ 잘못된 선택입니다."
        ;;
esac

echo ""
echo "🔍 설정 확인"
echo "============"

# API 키 확인
if grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "✅ OpenAI API Key: 설정됨"
else
    echo "❌ OpenAI API Key: 설정 필요"
fi

if grep -q "NOTION_API_KEY=secret_" .env; then
    echo "✅ Notion API Key: 설정됨"
else
    echo "❌ Notion API Key: 설정 필요"
fi

if grep -q "NOTION_DATABASE_ID=" .env && ! grep -q "NOTION_DATABASE_ID=your_notion_database_id_here" .env; then
    echo "✅ Notion Database ID: 설정됨"
else
    echo "❌ Notion Database ID: 설정 필요"
fi

echo ""
echo "🎉 환경 변수 설정 완료!"
echo ""
echo "💡 다음 단계:"
echo "   ./start_meeting.sh  # 대화형 회의 시작"
echo "   ./quick_start.sh    # 빠른 시작"
echo "   python main.py test-apis  # API 연결 테스트"
