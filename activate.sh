#!/bin/bash
# 가상환경 활성화 스크립트

echo "🚀 AI Meeting Summary 가상환경 활성화"
echo "=================================="

# 가상환경이 존재하는지 확인
if [ ! -d "venv" ]; then
    echo "❌ 가상환경이 존재하지 않습니다. 생성 중..."
    python -m venv venv
    echo "✅ 가상환경 생성 완료"
fi

# macOS에서 PortAudio 확인
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 macOS 감지됨 - PortAudio 확인 중..."
    if ! brew list portaudio &>/dev/null; then
        echo "⚠️  PortAudio가 설치되지 않았습니다."
        echo "📦 PortAudio 설치 중... (PyAudio 설치에 필요)"
        brew install portaudio
        echo "✅ PortAudio 설치 완료"
    else
        echo "✅ PortAudio가 이미 설치되어 있습니다."
    fi
fi

# 가상환경 활성화
echo "🔄 가상환경 활성화 중..."
source venv/bin/activate

# pip 업그레이드
echo "📦 pip 업그레이드 중..."
pip install --upgrade pip

# 의존성 설치
echo "📚 의존성 설치 중..."
pip install -r requirements.txt

echo ""
echo "✅ 가상환경 활성화 완료!"
echo "🐍 Python 경로: $(which python)"
echo "📦 pip 경로: $(which pip)"
echo ""
echo "💡 사용법:"
echo "   python main.py test-apis          # API 테스트"
echo "   python main.py full-pipeline     # 전체 파이프라인 실행"
echo ""
echo "🔧 비활성화: deactivate"
