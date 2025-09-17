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

# Whisper 모델 다운로드 옵션
echo "🎯 Whisper 모델 다운로드 옵션:"
echo "1) 최고 사양 모델 다운로드 (권장) - 정확도 96%, 비용 $0"
echo "2) 나중에 다운로드 - 첫 실행 시 자동 다운로드"
echo "3) 건너뛰기"

read -p "선택 (1-3, 기본값: 1): " whisper_choice
whisper_choice=${whisper_choice:-1}

if [ "$whisper_choice" = "1" ]; then
    echo ""
    echo "🚀 최고 사양 Whisper 모델 다운로드 시작..."
    echo "⏰ 예상 시간: 5-10분"
    echo ""
    
    python3 << 'EOF'
import whisper
from rich.console import Console

console = Console()

try:
    console.print("📦 Whisper Large 모델 다운로드 중... (1.5GB)", style="bold blue")
    model = whisper.load_model("large")
    console.print("✅ 최고 사양 모델 준비 완료! 정확도 96%, 비용 $0", style="bold green")
except Exception as e:
    console.print(f"❌ 다운로드 실패: {e}", style="red")
    console.print("💡 나중에 ./setup_whisper.sh로 다운로드할 수 있습니다.", style="yellow")
EOF
    
elif [ "$whisper_choice" = "2" ]; then
    echo "💡 첫 실행 시 자동으로 다운로드됩니다."
else
    echo "⏭️  Whisper 모델 다운로드를 건너뛰었습니다."
fi

echo ""
echo "💡 사용법:"
echo "   ./quick_start.sh                  # 빠른 시작 (로컬 Whisper 기본값)"
echo "   ./setup_whisper.sh               # Whisper 모델 다운로드"
echo "   python main.py test-apis         # API 테스트"
echo ""
echo "🔧 비활성화: deactivate"
