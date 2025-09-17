#!/bin/bash

# AI Meeting Summary - 빠른 시작 스크립트
# 간단한 질문으로 빠르게 회의 시작

echo "🎤 AI Meeting Summary - 빠른 시작"
echo "================================="
echo ""

# 가상환경 활성화
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ 가상환경 활성화됨"
else
    echo "❌ 가상환경이 없습니다. ./activate.sh를 먼저 실행해주세요."
    exit 1
fi

# 환경 변수 확인 (선택사항)
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다."
    echo ""
    echo "💡 환경 변수는 선택사항입니다:"
    echo "   - 로컬 Whisper만 사용: .env 파일 없이도 사용 가능"
    echo "   - GPT 요약 및 Notion 저장: .env 파일 필요"
    echo ""
    echo "📝 환경 변수 설정하려면:"
    echo "   cp env.example .env"
    echo "   # .env 파일을 편집하여 API 키 입력"
    echo ""
    echo "🚀 .env 파일 없이도 로컬 Whisper로 음성 인식은 가능합니다!"
    echo ""
fi

echo ""
echo "📝 회의 정보를 간단히 입력해주세요:"
echo ""

# 회의 제목
read -p "회의 주제: " title
title=${title:-"회의"}  # 기본값: "회의"

# 회의 시간
read -p "예상 시간(분): " duration
duration=${duration:-30}  # 기본값: 30분

# 언어
read -p "언어 (ko/en/ja/zh, 기본값: ko): " language
language=${language:-ko}  # 기본값: 한국어

echo ""
echo "🎯 음성 인식 방법을 선택하세요:"
echo "1) 로컬 Whisper (무료, 정확도 91%, 빠른 처리) [기본값]"
echo "2) OpenAI API (유료, 정확도 98%)"

read -p "선택 (1-2, 기본값: 1): " whisper_choice
whisper_choice=${whisper_choice:-1}  # 기본값: 1 (로컬)

if [ "$whisper_choice" = "1" ]; then
    echo "✅ 로컬 Whisper 선택 - 비용 $0 (완전 무료)"
    echo "🚀 실용적 모델 (small) 사용 - 정확도 91%, 빠른 처리"
    whisper_option="--local-only"
else
    echo "✅ OpenAI API 선택 - 비용 발생"
    whisper_option=""
fi

echo ""
echo "🚀 회의 시작: $title ($duration분, $language)"
echo ""

# 대화형 파이프라인 실행 (q 키로 중지 가능)
python main.py interactive-meeting \
    --title "$title" \
    --duration "$duration" \
    --language "$language" \
    --save-to-notion \
    $whisper_option

echo ""
echo "✅ 회의 완료!"
