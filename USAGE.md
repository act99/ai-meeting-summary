# 🎤 AI Meeting Summary 사용 가이드

## 📋 기본 사용법

### 🎯 방법 1: 대화형 시작 (권장)

가장 쉬운 방법입니다. 스크립트가 모든 것을 안내해줍니다:

```bash
# 대화형 스크립트 실행
./start_meeting.sh
```

스크립트가 다음을 안내합니다:
- 회의 주제 입력
- 예상 시간 입력  
- 언어 선택
- Notion 저장 여부
- 설정 확인 후 자동 실행

### ⚡ 방법 2: 빠른 시작

간단한 질문으로 빠르게 시작:

```bash
# 빠른 시작 스크립트
./quick_start.sh
```

### 🔧 방법 3: 수동 실행

```bash
# 가상환경 활성화
source venv/bin/activate

# 환경 변수 설정 (최초 1회)
./setup_env.sh  # 자동 설정 도우미
# 또는
cp env.example .env  # 수동 설정

# API 테스트
python main.py test-apis

# 전체 파이프라인 실행
python main.py full-pipeline --title "주간 회의" --duration 30
```

## 🎯 단계별 사용법

### 단계 1: 회의 녹음만

```bash
# 기본 녹음 (제목: "회의")
python main.py record-meeting

# 제목과 시간 지정
python main.py record-meeting --title "프로젝트 리뷰" --duration 45

# 출력 파일 지정
python main.py record-meeting --title "팀 미팅" --output-file team_meeting.wav
```

### 단계 2: 음성 인식

```bash
# 기본 음성 인식 (한국어)
python main.py transcribe-file meeting.wav

# 영어 음성 인식
python main.py transcribe-file english_meeting.wav --language en

# 출력 파일 지정
python main.py transcribe-file audio.mp3 --output-file transcript.txt
```

### 단계 3: 요약 생성

```bash
# 기본 요약
python main.py summarize-meeting transcript.txt

# Notion에 저장
python main.py summarize-meeting transcript.txt --save-to-notion

# 파일로 저장
python main.py summarize-meeting transcript.txt --output-file summary.md
```

## 🔧 고급 사용법

### 다양한 오디오 형식 지원

```bash
# WAV 파일
python main.py transcribe-file meeting.wav

# MP3 파일
python main.py transcribe-file meeting.mp3

# M4A 파일
python main.py transcribe-file meeting.m4a
```

### 다국어 지원

```bash
# 한국어 (기본)
python main.py transcribe-file meeting.wav --language ko

# 영어
python main.py transcribe-file meeting.wav --language en

# 일본어
python main.py transcribe-file meeting.wav --language ja

# 중국어
python main.py transcribe-file meeting.wav --language zh
```

### Notion 관리

```bash
# 저장된 회의 목록 조회
python main.py list-meetings

# 특정 회의 페이지 확인
# (Notion에서 직접 확인)
```

## 📁 파일 구조

```
ai-meeting-summary/
├── data/           # 녹음 파일 저장
├── output/         # 결과 파일 저장
├── temp/           # 임시 파일
└── .env            # 환경 변수 (생성 필요)
```

## ⚠️ 주의사항

### 마이크 권한
- macOS: 시스템 환경설정 > 보안 및 개인정보 보호 > 마이크
- Windows: 설정 > 개인정보 > 마이크
- Linux: pulseaudio 권한 확인

### 파일 크기 제한
- Whisper 모델: 최대 25MB 오디오 파일 권장
- 큰 파일은 자동으로 청크 단위로 분할 처리

### API 사용량
- OpenAI API: 토큰 사용량에 따라 비용 발생
- Whisper: 무료 (로컬 처리)
- Notion API: 월 1000회 요청 제한

## 🚨 문제 해결

### 녹음이 안 될 때
```bash
# 마이크 권한 확인
# 다른 앱에서 마이크 사용 중인지 확인
# 시스템 볼륨 확인
```

### 음성 인식이 안 될 때
```bash
# 오디오 파일 형식 확인 (WAV, MP3, M4A 지원)
# 파일 크기 확인 (25MB 이하 권장)
# 배경 소음 확인
```

### Notion 저장이 안 될 때
```bash
# API 키 확인
# 데이터베이스 권한 확인
# 인터넷 연결 확인
```

## 💡 팁

### 최적의 녹음 환경
- 조용한 환경에서 녹음
- 마이크에 가까이서 명확하게 발음
- 배경 소음 최소화

### 효율적인 사용
- 정기 회의는 `full-pipeline` 사용
- 긴 회의는 시간 제한 설정
- 중요한 회의는 백업 파일 생성

### 결과 활용
- Notion에서 태그 추가
- 액션 아이템 별도 관리
- 회의록 템플릿 활용
