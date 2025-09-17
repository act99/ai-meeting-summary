# AI Meeting Summary 🎤🤖

AI 기반 회의 녹음, 음성 인식, 요약 및 Notion 저장을 위한 종합 도구입니다.

## ✨ 주요 기능

- 🎤 **실시간 회의 녹음**: 고품질 오디오 녹음
- 🎯 **음성 인식**: OpenAI Whisper를 통한 정확한 한국어 음성 인식
- 🤖 **AI 요약**: GPT-4를 활용한 스마트 회의 요약
- 📝 **Notion 연동**: 자동으로 Notion 페이지 생성 및 저장
- 🔧 **CLI 인터페이스**: 사용하기 쉬운 명령줄 도구

## 🚀 빠른 시작

### 0. 환경 설정

**💰 비용 절약 모드 (권장)**: 환경 변수 없이도 완전 무료로 사용 가능!

```bash
# 자동 설정 도우미 사용 (권장)
./setup_env.sh

# 환경 변수 설정을 건너뛰고 싶다면 'n' 선택
# 또는 수동 설정
cp env.example .env
# .env 파일을 편집하여 API 키 입력
```

**🎯 음성 인식 옵션:**
- **로컬 Whisper (기본값)**: 정확도 96%, 비용 $0 (완전 무료)
- **OpenAI API**: 정확도 98%, 비용 발생 ($0.006/분)

**선택적 API 키 (설정하면 더 많은 기능 사용 가능):**
- `OPENAI_API_KEY`: OpenAI API 키 (GPT 요약 및 고품질 음성 인식)
- `NOTION_API_KEY`: Notion Integration Token (Notion 자동 저장)
- `NOTION_DATABASE_ID`: Notion 데이터베이스 ID

**환경 변수 없이도 사용 가능한 기능:**
- 로컬 Whisper Large 모델로 음성 인식 (정확도 96%)
- 로컬 파일로 결과 저장
- 기본 회의 요약 기능

### 1. 설치

#### 🚀 자동 설치 (권장)
```bash
# 저장소 클론
git clone <repository-url>
cd ai-meeting-summary

# 가상환경 자동 생성 및 활성화 + 의존성 설치 + Whisper 모델 다운로드
./activate.sh
```

**설치 과정에서 Whisper 모델 다운로드 옵션:**
- **옵션 1 (권장)**: 최고 사양 모델 다운로드 - 정확도 96%, 비용 $0
- **옵션 2**: 나중에 다운로드 - 첫 실행 시 자동 다운로드  
- **옵션 3**: 건너뛰기

#### 🔧 수동 설치
```bash
# 저장소 클론
git clone <repository-url>
cd ai-meeting-summary

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

#### 🍎 macOS 사용자 주의사항

macOS에서 PyAudio 설치 시 PortAudio 라이브러리가 필요합니다:

```bash
# Homebrew로 PortAudio 설치
brew install portaudio

# 그 후 의존성 설치
pip install -r requirements.txt
```

**설치 오류 시 해결 방법:**
- `portaudio.h file not found` 오류: 위의 `brew install portaudio` 명령어 실행
- Homebrew가 없는 경우: [Homebrew 설치](https://brew.sh/) 후 위 명령어 실행

### 2. 첫 실행 테스트

설치가 완료되면 API 연결을 테스트해보세요:

```bash
# 가상환경 활성화
source venv/bin/activate

# API 연결 테스트
python main.py test-apis
```

모든 API가 정상적으로 연결되면 사용 준비 완료! 🎉

### 3. 사용법

#### 🎯 대화형 시작 (가장 쉬운 방법)
```bash
# 대화형 스크립트로 회의 시작
./start_meeting.sh
```

#### ⚡ 빠른 시작
```bash
# 간단한 질문으로 빠르게 시작
./quick_start.sh
```

#### 🚀 수동 실행
```bash
# 가상환경 활성화
source venv/bin/activate

# 전체 파이프라인 실행 (녹음 → 인식 → 요약 → Notion 저장)
python main.py full-pipeline --title "주간 회의" --duration 30
```

#### 📋 단계별 실행
```bash
# 1. 회의 녹음만
python main.py record-meeting --title "주간 회의" --duration 30

# 2. 기존 오디오 파일 음성 인식
python main.py transcribe-file audio_file.wav

# 3. 음성 인식 결과 요약 생성
python main.py summarize-meeting transcription.txt --save-to-notion
```

#### 🔧 유틸리티 명령어
```bash
# API 연결 테스트
python main.py test-apis

# 저장된 회의 목록 조회
python main.py list-meetings

# 도움말 보기
python main.py --help
```

## 📋 명령어 가이드

### 🎤 `record-meeting`
회의를 녹음합니다.

```bash
python main.py record-meeting [OPTIONS]

Options:
  --title TEXT        회의 제목 [default: 회의]
  --duration INTEGER  녹음 시간 (분)
  --output-file TEXT  출력 파일 경로

# 예시
python main.py record-meeting --title "주간 회의" --duration 30
python main.py record-meeting --title "프로젝트 리뷰" --output-file meeting.wav
```

### 🎯 `transcribe-file`
오디오 파일을 텍스트로 변환합니다.

```bash
python main.py transcribe-file AUDIO_FILE [OPTIONS]

Options:
  --language TEXT      언어 코드 [default: ko]
  --output-file TEXT   출력 파일 경로

# 예시
python main.py transcribe-file meeting.wav
python main.py transcribe-file audio.mp3 --language en --output-file transcript.txt
```

### 🤖 `summarize-meeting`
회의 내용을 요약합니다.

```bash
python main.py summarize-meeting TRANSCRIPTION_FILE [OPTIONS]

Options:
  --output-file TEXT    출력 파일 경로
  --save-to-notion      Notion에 저장

# 예시
python main.py summarize-meeting transcript.txt --save-to-notion
python main.py summarize-meeting transcript.txt --output-file summary.md
```

### 🚀 `full-pipeline`
전체 파이프라인을 한 번에 실행합니다.

```bash
python main.py full-pipeline [OPTIONS]

Options:
  --title TEXT          회의 제목 [default: 회의]
  --duration INTEGER    녹음 시간 (분)
  --language TEXT       언어 코드 [default: ko]
  --save-to-notion      Notion에 저장 [default: True]

# 예시
python main.py full-pipeline --title "주간 회의" --duration 30
python main.py full-pipeline --title "프로젝트 리뷰" --language en --save-to-notion
```

### 🔧 유틸리티 명령어

```bash
# API 연결 테스트
python main.py test-apis

# 저장된 회의 목록 조회
python main.py list-meetings

# 도움말 보기
python main.py --help
python main.py [COMMAND] --help  # 특정 명령어 도움말
```

## 🏗️ 프로젝트 구조

```
ai-meeting-summary/
├── src/
│   ├── audio/              # 오디오 녹음 및 처리
│   │   ├── recorder.py     # 녹음 기능
│   │   └── processor.py    # 오디오 전처리
│   ├── transcription/      # 음성 인식
│   │   ├── whisper_client.py
│   │   └── formatter.py
│   ├── summarization/      # AI 요약
│   │   ├── gpt_client.py
│   │   ├── meeting_analyzer.py
│   │   └── prompt_templates.py
│   ├── notion/            # Notion 연동
│   │   ├── notion_client.py
│   │   └── meeting_page_builder.py
│   └── utils/             # 유틸리티
│       ├── config.py
│       ├── logger.py
│       └── file_manager.py
├── data/                  # 임시 파일 저장소
├── output/                # 결과 파일 저장소
├── temp/                  # 임시 처리 파일
├── tests/                 # 테스트 파일
├── main.py               # 메인 실행 파일
├── requirements.txt      # 의존성 목록
├── env.example          # 환경 변수 템플릿
├── activate.sh           # 가상환경 자동 설정
├── setup_env.sh          # 환경 변수 설정 도우미
├── start_meeting.sh      # 대화형 회의 시작
├── quick_start.sh        # 빠른 시작
├── setup_notion_database.py  # Notion DB 설정
└── fix_notion_db.py      # Notion DB 수정
```

## 🔧 설정

### 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 키 | - |
| `OPENAI_MODEL` | 사용할 GPT 모델 | gpt-4o-mini |
| `NOTION_API_KEY` | Notion Integration Token | - |
| `NOTION_DATABASE_ID` | Notion 데이터베이스 ID | - |
| `AUDIO_SAMPLE_RATE` | 오디오 샘플링 레이트 | 44100 |
| `AUDIO_CHANNELS` | 오디오 채널 수 | 1 |
| `LOG_LEVEL` | 로그 레벨 | INFO |

### Notion 설정

1. [Notion Developers](https://developers.notion.com/)에서 Integration 생성
2. Integration Token 복사
3. 데이터베이스 생성 후 페이지 권한 부여
4. 데이터베이스 ID 복사

## 📊 지원 형식

### 입력 오디오 형식
- WAV, MP3, M4A, FLAC, OGG
- 샘플링 레이트: 16kHz 이상 권장
- 채널: 모노/스테레오 모두 지원

### 출력 형식
- 텍스트 파일 (.txt)
- Notion 페이지
- JSON 형식 요약 데이터

## 🛠️ 개발

### 개발 환경 설정

```bash
# 개발 의존성 설치
pip install -r requirements.txt

# 코드 포맷팅
black src/
isort src/

# 타입 체킹
mypy src/

# 린팅
pylint src/
```

### 테스트

```bash
# 단위 테스트 실행
pytest tests/

# API 연결 테스트
python main.py test-apis
```

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 🆘 문제 해결

### 일반적인 문제

**Q: PyAudio 설치가 실패해요 (macOS)**
A: PortAudio 라이브러리가 필요합니다. `brew install portaudio` 실행 후 다시 시도하세요.

**Q: 녹음이 시작되지 않아요**
A: 마이크 권한을 확인하고, 다른 애플리케이션이 마이크를 사용 중인지 확인하세요.

**Q: Whisper 모델 로딩이 느려요**
A: 첫 실행 시 모델을 다운로드하므로 시간이 걸립니다. 인터넷 연결을 확인하세요.

**Q: Notion 저장이 실패해요**
A: API 키와 데이터베이스 ID를 확인하고, Notion Integration에 적절한 권한이 있는지 확인하세요.

**Q: 음성 인식 정확도가 낮아요**
A: 배경 소음을 줄이고, 마이크에 가까이서 명확하게 발음하세요.

**Q: 가상환경이 활성화되지 않아요**
A: `source venv/bin/activate` 명령어를 실행하거나 `./activate.sh` 스크립트를 사용하세요.

**Q: OpenAI API 할당량 초과 오류가 발생해요**
A: 로컬 Whisper 모델이 자동으로 사용됩니다. OpenAI 계정에서 할당량을 확인하고 충전하세요.

**Q: ffmpeg를 찾을 수 없다는 오류가 발생해요**
A: `brew install ffmpeg` 명령어로 ffmpeg를 설치하세요.

**Q: 환경 변수 설정을 건너뛰고 싶어요**
A: `./setup_env.sh` 실행 시 'n'을 선택하면 환경 변수 설정을 건너뛸 수 있습니다.

**Q: Notion에 저장된 요약에 # 기호가 포함되어 있어요**
A: 최신 버전에서는 마크다운 헤더가 자동으로 제거됩니다. 코드를 업데이트하세요.

**Q: Notion 데이터베이스 속성이 없다는 오류가 발생해요**
A: `python fix_notion_db.py` 명령어로 데이터베이스 속성을 자동으로 추가하세요.

**Q: 음성 인식 결과 병합 오류가 발생해요**
A: 최신 버전에서 수정되었습니다. 코드를 업데이트하세요.

**Q: 환경 변수 없이도 사용할 수 있나요?**
A: 네! 로컬 Whisper 모델로 음성 인식하고 로컬 파일로 저장할 수 있습니다. API 키는 선택사항입니다.

### 로그 확인

```bash
# 로그 파일 확인
tail -f meeting_summary.log

# 디버그 모드로 실행
LOG_LEVEL=DEBUG python main.py full-pipeline
```

## 📞 지원

문제가 발생하거나 기능 요청이 있으시면 [Issues](https://github.com/your-repo/issues)를 통해 알려주세요.

---

**Made with ❤️ for productive meetings**
