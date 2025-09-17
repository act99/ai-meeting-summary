#!/bin/bash

# AI Meeting Summary - 대화형 시작 스크립트
# 사용자에게 회의 정보를 입력받아 자동으로 파이프라인 실행

echo "🎤 AI Meeting Summary - 회의 시작"
echo "=================================="
echo ""

# 가상환경 확인 및 활성화
if [ ! -d "venv" ]; then
    echo "❌ 가상환경이 없습니다. 먼저 ./activate.sh를 실행해주세요."
    exit 1
fi

echo "🔄 가상환경 활성화 중..."
source venv/bin/activate

# 환경 변수 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다."
    echo ""
    echo "📝 환경 변수 설정이 필요합니다:"
    echo "   1. env.example을 .env로 복사"
    echo "   2. .env 파일을 편집하여 API 키 입력"
    echo ""
    echo "   cp env.example .env"
    echo "   # 그 후 .env 파일을 편집하세요"
    echo ""
    read -p "지금 .env 파일을 생성하시겠습니까? (y/n): " create_env
    
    if [ "$create_env" = "y" ] || [ "$create_env" = "Y" ]; then
        cp env.example .env
        echo ""
        echo "✅ .env 파일이 생성되었습니다!"
        echo "📝 이제 .env 파일을 편집하여 API 키를 입력해주세요:"
        echo "   - OPENAI_API_KEY: OpenAI API 키"
        echo "   - NOTION_API_KEY: Notion Integration Token"
        echo "   - NOTION_DATABASE_ID: Notion 데이터베이스 ID"
        echo ""
        read -p "API 키 설정을 완료하셨나요? (y/n): " keys_set
        
        if [ "$keys_set" != "y" ] && [ "$keys_set" != "Y" ]; then
            echo "❌ API 키 설정을 완료한 후 다시 실행해주세요."
            exit 1
        fi
    else
        echo "❌ .env 파일을 먼저 설정해주세요."
        echo "   cp env.example .env"
        echo "   # .env 파일을 편집하여 API 키 입력"
        exit 1
    fi
fi

echo ""
echo "📋 회의 정보 입력"
echo "=================="

# 회의 제목 입력
while true; do
    read -p "회의 주제가 어떻게 되나요? " meeting_title
    if [ -n "$meeting_title" ]; then
        break
    else
        echo "❌ 회의 주제를 입력해주세요."
    fi
done

# 회의 시간 입력
while true; do
    read -p "몇분 예상하시나요? (숫자만 입력, 예: 30): " meeting_duration
    if [[ "$meeting_duration" =~ ^[0-9]+$ ]] && [ "$meeting_duration" -gt 0 ]; then
        break
    else
        echo "❌ 올바른 시간을 입력해주세요. (예: 30)"
    fi
done

# 언어 선택
echo ""
echo "🌍 언어를 선택해주세요:"
echo "1) 한국어 (기본)"
echo "2) 영어"
echo "3) 일본어"
echo "4) 중국어"
read -p "선택 (1-4, 기본값: 1): " language_choice

case $language_choice in
    2) language="en" ;;
    3) language="ja" ;;
    4) language="zh" ;;
    *) language="ko" ;;
esac

# Notion 저장 여부
echo ""
read -p "Notion에 자동으로 저장하시겠습니까? (y/n, 기본값: y): " save_to_notion
if [ "$save_to_notion" = "n" ] || [ "$save_to_notion" = "N" ]; then
    notion_flag=""
else
    notion_flag="--save-to-notion"
fi

# 설정 확인
echo ""
echo "📝 입력된 정보 확인"
echo "===================="
echo "회의 주제: $meeting_title"
echo "예상 시간: $meeting_duration분"
echo "언어: $language"
echo "Notion 저장: $([ -n "$notion_flag" ] && echo "예" || echo "아니오")"
echo ""

read -p "이 설정으로 회의를 시작하시겠습니까? (y/n): " confirm_start

if [ "$confirm_start" = "y" ] || [ "$confirm_start" = "Y" ]; then
    echo ""
    echo "🚀 회의 시작!"
    echo "=============="
    echo "🎤 녹음이 시작됩니다. 중지하려면 Ctrl+C를 누르세요."
    echo ""
    
    # 전체 파이프라인 실행
    python main.py full-pipeline \
        --title "$meeting_title" \
        --duration "$meeting_duration" \
        --language "$language" \
        $notion_flag
    
    echo ""
    echo "✅ 회의가 완료되었습니다!"
    echo ""
    echo "📁 결과 파일 위치:"
    echo "   - 녹음 파일: ./data/"
    echo "   - 요약 파일: ./output/"
    echo "   - Notion 페이지: 위에서 제공된 URL"
    
else
    echo "❌ 회의가 취소되었습니다."
fi

echo ""
echo "👋 AI Meeting Summary를 이용해주셔서 감사합니다!"
