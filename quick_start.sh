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

# 환경 변수 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다."
    echo ""
    echo "📝 환경 변수 설정이 필요합니다:"
    echo "   cp env.example .env"
    echo "   # .env 파일을 편집하여 API 키 입력"
    echo ""
    echo "❌ .env 파일을 먼저 설정해주세요."
    exit 1
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
echo "🚀 회의 시작: $title ($duration분, $language)"
echo ""

# 전체 파이프라인 실행
python main.py full-pipeline \
    --title "$title" \
    --duration "$duration" \
    --language "$language" \
    --save-to-notion

echo ""
echo "✅ 회의 완료!"
