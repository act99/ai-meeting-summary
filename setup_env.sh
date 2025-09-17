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
        echo "⏭️  환경 변수 설정을 건너뛰고 다음 단계로 진행합니다."
        skip_env_setup=true
    else
        skip_env_setup=false
    fi
else
    skip_env_setup=false
fi

# 환경 변수 설정을 건너뛰지 않는 경우에만 파일 복사 및 안내
if [ "$skip_env_setup" = "false" ]; then
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
fi

# 환경 변수 설정을 건너뛰지 않는 경우에만 편집기 선택
if [ "$skip_env_setup" = "false" ]; then
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
else
    editor_choice="3"  # 직접 편집으로 설정
fi

echo ""
echo "🔍 설정 확인"
echo "============"

if [ "$skip_env_setup" = "true" ]; then
    echo "⏭️  환경 변수 설정을 건너뛰었습니다."
    echo ""
    echo "💡 환경 변수 없이도 다음 기능들을 사용할 수 있습니다:"
    echo "   - 로컬 Whisper 모델로 음성 인식"
    echo "   - 로컬 파일로 결과 저장"
    echo "   - API 연결 테스트 (python main.py test-apis)"
    echo ""
    echo "📝 나중에 환경 변수를 설정하려면:"
    echo "   nano .env"
else
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
fi

echo ""
echo "🔧 추가 의존성 설치"
echo "=================="
echo ""
echo "macOS에서 오디오 처리를 위해 다음 패키지들이 필요합니다:"
echo ""
echo "1. ffmpeg (오디오 파일 처리용)"
echo "   brew install ffmpeg"
echo ""
echo "2. PortAudio (오디오 녹음용)"
echo "   brew install portaudio"
echo ""
echo "3. Python 패키지 설치"
echo "   pip install -r requirements.txt"
echo ""

# ffmpeg 설치 확인
if command -v ffmpeg &> /dev/null; then
    echo "✅ ffmpeg: 설치됨"
else
    echo "❌ ffmpeg: 설치 필요 (brew install ffmpeg)"
fi

# portaudio 설치 확인
if brew list portaudio &> /dev/null; then
    echo "✅ PortAudio: 설치됨"
else
    echo "❌ PortAudio: 설치 필요 (brew install portaudio)"
fi

echo ""
echo "🎉 환경 변수 설정 완료!"
echo ""
echo "💡 다음 단계:"
echo "   ./start_meeting.sh  # 대화형 회의 시작"
echo "   ./quick_start.sh    # 빠른 시작"
echo "   python main.py test-apis  # API 연결 테스트"
echo ""
echo "⚠️  OpenAI API 할당량 초과 시:"
echo "   - 로컬 Whisper 모델이 자동으로 사용됩니다"
echo "   - OpenAI 계정에서 할당량을 확인하세요"
