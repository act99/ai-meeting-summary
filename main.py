"""
AI Meeting Summary - Main Pipeline

회의 녹음 → 음성 인식 → 요약 → Notion 저장 전체 파이프라인
"""

import typer
import asyncio
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table

from src.audio import AudioRecorder, AudioProcessor, MeetingRecorder, MeetingAudioProcessor
from src.transcription import WhisperClient, TextFormatter, MeetingTranscriber
from src.summarization import GPTClient, MeetingSummarizer, MeetingAnalyzer
from src.notion import NotionClient, MeetingPageBuilder
from src.utils import Config, setup_logger, FileManager

# CLI 앱 초기화
app = typer.Typer(help="AI 회의 요약 도구")
console = Console()

# 전역 설정
config = Config()
logger = setup_logger("meeting_summary", config.logging.log_level, config.logging.log_file)


@app.command()
def record_meeting(
    title: str = typer.Option("회의", help="회의 제목"),
    duration: Optional[int] = typer.Option(None, help="녹음 시간 (분)"),
    output_file: Optional[str] = typer.Option(None, help="출력 파일 경로")
):
    """회의 녹음"""
    console.print(Panel(f"🎤 회의 녹음 시작: {title}", style="bold blue"))
    
    try:
        # 녹음기 초기화
        recorder = MeetingRecorder()
        
        # 녹음 시작
        success = recorder.start_meeting_recording(title, duration)
        if not success:
            console.print("❌ 녹음 시작 실패", style="red")
            return
        
        console.print("✅ 녹음이 시작되었습니다. 중지하려면 Ctrl+C를 누르세요.", style="green")
        
        # 녹음 대기
        try:
            while recorder.recorder.is_recording:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n🛑 녹음 중지 요청됨", style="yellow")
        
        # 녹음 중지 및 저장
        file_path = recorder.stop_recording()
        if file_path:
            console.print(f"✅ 녹음 완료: {file_path}", style="green")
            
            # 출력 파일 지정된 경우 복사
            if output_file:
                import shutil
                shutil.copy2(file_path, output_file)
                console.print(f"📁 파일 복사 완료: {output_file}", style="green")
        else:
            console.print("❌ 녹음 저장 실패", style="red")
            
    except Exception as e:
        console.print(f"❌ 녹음 오류: {e}", style="red")
        logger.error(f"녹음 오류: {e}")


@app.command()
def transcribe_file(
    audio_file: str = typer.Argument(..., help="오디오 파일 경로"),
    language: str = typer.Option("ko", help="언어 코드"),
    output_file: Optional[str] = typer.Option(None, help="출력 파일 경로")
):
    """오디오 파일 음성 인식"""
    console.print(Panel(f"🎯 음성 인식 시작: {audio_file}", style="bold blue"))
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            # 오디오 처리
            task1 = progress.add_task("오디오 처리 중...", total=100)
            processor = MeetingAudioProcessor()
            processed_file, chunks = processor.process_meeting_audio(audio_file)
            progress.update(task1, completed=100)
            
            # 음성 인식
            task2 = progress.add_task("음성 인식 중...", total=100)
            transcriber = MeetingTranscriber()
            
            if len(chunks) > 1:
                # 청크별 처리
                chunk_paths = [processor._save_processed_audio(chunk, config.audio.sample_rate, f"chunk_{i}.wav") for i, chunk in enumerate(chunks)]
                result = transcriber.transcribe_meeting_chunks(chunk_paths, language)
            else:
                # 전체 파일 처리
                result = transcriber.transcribe_meeting(processed_file, language)
            
            progress.update(task2, completed=100)
            
            # 텍스트 포맷팅
            task3 = progress.add_task("텍스트 포맷팅 중...", total=100)
            formatter = TextFormatter()
            structured_content = formatter.structure_meeting_content(result)
            progress.update(task3, completed=100)
        
        # 결과 저장
        if output_file:
            formatted_text = formatter.format_for_summary(structured_content)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(formatted_text)
            console.print(f"✅ 결과 저장 완료: {output_file}", style="green")
        
        # 결과 표시
        console.print(Panel("📝 음성 인식 결과", style="bold green"))
        console.print(f"단어 수: {structured_content['word_count']}")
        console.print(f"문자 수: {structured_content['character_count']}")
        console.print(f"지속시간: {structured_content['duration']:.1f}초")
        console.print(f"참석자: {', '.join(structured_content['speakers'])}")
        
        # 미리보기
        preview = structured_content['full_text'][:200] + "..." if len(structured_content['full_text']) > 200 else structured_content['full_text']
        console.print(f"\n📖 미리보기:\n{preview}")
        
    except Exception as e:
        console.print(f"❌ 음성 인식 오류: {e}", style="red")
        logger.error(f"음성 인식 오류: {e}")


@app.command()
def summarize_meeting(
    transcription_file: str = typer.Argument(..., help="음성 인식 결과 파일"),
    output_file: Optional[str] = typer.Option(None, help="출력 파일 경로"),
    save_to_notion: bool = typer.Option(False, help="Notion에 저장")
):
    """회의 요약 생성"""
    console.print(Panel("🤖 회의 요약 생성", style="bold blue"))
    
    try:
        # 음성 인식 결과 로드
        with open(transcription_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 임시 데이터 구조 생성
        transcription_data = {
            "meeting_id": Path(transcription_file).stem,
            "full_text": content,
            "word_count": len(content.split()),
            "character_count": len(content),
            "speakers": [],
            "duration": 0,
            "language": "ko"
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            # GPT 요약
            task1 = progress.add_task("GPT 요약 생성 중...", total=100)
            summarizer = MeetingSummarizer()
            comprehensive_result = summarizer.summarize_meeting_comprehensive(transcription_data)
            progress.update(task1, completed=100)
            
            # 분석
            task2 = progress.add_task("회의 분석 중...", total=100)
            analyzer = MeetingAnalyzer()
            insights = analyzer.generate_meeting_insights(transcription_data)
            progress.update(task2, completed=100)
        
        # 결과 표시
        console.print(Panel("📋 회의 요약 결과", style="bold green"))
        console.print(f"회의 ID: {comprehensive_result['meeting_id']}")
        console.print(f"액션 아이템: {len(comprehensive_result['action_items'])}개")
        console.print(f"결정사항: {len(comprehensive_result['decisions'])}개")
        
        # 요약 미리보기
        summary_preview = comprehensive_result['summary'][:300] + "..." if len(comprehensive_result['summary']) > 300 else comprehensive_result['summary']
        console.print(f"\n📖 요약 미리보기:\n{summary_preview}")
        
        # 파일 저장
        if output_file:
            summarizer.save_summary_to_file(comprehensive_result, "comprehensive")
            console.print(f"✅ 요약 파일 저장 완료: {output_file}", style="green")
        
        # Notion 저장
        if save_to_notion:
            console.print("📝 Notion에 저장 중...", style="yellow")
            page_builder = MeetingPageBuilder()
            notion_result = page_builder.create_meeting_page(comprehensive_result)
            console.print(f"✅ Notion 저장 완료: {notion_result['url']}", style="green")
        
    except Exception as e:
        console.print(f"❌ 요약 생성 오류: {e}", style="red")
        logger.error(f"요약 생성 오류: {e}")


@app.command()
def interactive_meeting(
    title: str = typer.Option("회의", help="회의 제목"),
    duration: Optional[int] = typer.Option(None, help="녹음 시간 (분)"),
    language: str = typer.Option("ko", help="언어 코드"),
    save_to_notion: bool = typer.Option(True, help="Notion에 저장"),
    local_only: bool = typer.Option(False, help="로컬 Whisper만 사용 (비용 절약)")
):
    """대화형 회의 파이프라인 (q 키로 중지 가능)"""
    console.print(Panel("🎤 대화형 AI 회의 요약", style="bold blue"))
    console.print("💡 회의 중 'q'를 두 번 누르면 회의를 종료하고 요약을 시작합니다.", style="yellow")
    
    try:
        # 1단계: 녹음
        console.print("\n🎤 1단계: 회의 녹음", style="bold yellow")
        recorder = MeetingRecorder()
        success = recorder.start_meeting_recording(title, duration)
        
        if not success:
            console.print("❌ 녹음 시작 실패", style="red")
            return
        
        console.print("✅ 녹음이 시작되었습니다.", style="green")
        console.print("💡 회의 종료를 원하시면 'q'를 두 번 누르세요.", style="cyan")
        
        # 대화형 중지 처리
        import sys
        import select
        import tty
        import termios
        
        def get_key():
            """키 입력 감지"""
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
        
        q_count = 0
        try:
            while recorder.recorder.is_recording:
                import time
                time.sleep(0.1)
                
                # 키 입력 확인 (논블로킹)
                if select.select([sys.stdin], [], [], 0)[0]:
                    key = get_key()
                    if key.lower() == 'q':
                        q_count += 1
                        if q_count == 1:
                            console.print(f"\n⚠️  회의를 종료하시겠습니까? 한 번 더 'q'를 누르면 회의를 종료하고 요약을 시작합니다.", style="yellow")
                        elif q_count == 2:
                            console.print(f"\n🛑 회의 종료 요청됨 - 요약을 시작합니다.", style="yellow")
                            recorder.request_stop()
                            break
                    else:
                        q_count = 0  # 다른 키를 누르면 카운트 리셋
                        
        except KeyboardInterrupt:
            console.print(f"\n🛑 녹음 중지 요청됨", style="yellow")
            recorder.request_stop()
        
        audio_file = recorder.stop_recording()
        if not audio_file:
            console.print("❌ 녹음 저장 실패", style="red")
            return
        
        console.print(f"✅ 녹음 완료: {audio_file}", style="green")
        
        # 2단계: 오디오 처리 및 음성 인식
        console.print("\n🎯 2단계: 음성 인식", style="bold yellow")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            # 오디오 처리
            task1 = progress.add_task("오디오 처리 중...", total=100)
            processor = MeetingAudioProcessor()
            processed_file, chunks = processor.process_meeting_audio(audio_file)
            progress.update(task1, completed=100)
            
            # 음성 인식
            task2 = progress.add_task("음성 인식 중...", total=100)
            transcriber = MeetingTranscriber()
            
            if len(chunks) > 1:
                chunk_paths = [processor._save_processed_audio(chunk, config.audio.sample_rate, f"chunk_{i}.wav") for i, chunk in enumerate(chunks)]
                transcription_result = transcriber.transcribe_meeting_chunks(chunk_paths, language)
            else:
                transcription_result = transcriber.transcribe_meeting(processed_file, language)
            
            progress.update(task2, completed=100)
        
        # 텍스트 포맷팅
        formatter = TextFormatter()
        structured_content = formatter.structure_meeting_content(transcription_result)
        console.print(f"✅ 음성 인식 완료: {structured_content['word_count']}단어", style="green")
        
        # 3단계: 요약 생성
        console.print("\n🤖 3단계: 회의 요약", style="bold yellow")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            # GPT 요약
            task3 = progress.add_task("GPT 요약 생성 중...", total=100)
            summarizer = MeetingSummarizer()
            comprehensive_result = summarizer.summarize_meeting_comprehensive(structured_content)
            progress.update(task3, completed=100)
        
        console.print(f"✅ 요약 완료: {len(comprehensive_result['action_items'])}개 액션 아이템", style="green")
        
        # 4단계: Notion 저장
        if save_to_notion:
            console.print("\n📝 4단계: Notion 저장", style="bold yellow")
            
            try:
                page_builder = MeetingPageBuilder()
                notion_result = page_builder.create_meeting_page(comprehensive_result)
                console.print(f"✅ Notion 저장 완료: {notion_result['url']}", style="green")
            except Exception as e:
                console.print(f"⚠️ Notion 저장 실패: {e}", style="yellow")
                console.print("로컬 파일로 저장합니다.", style="yellow")
                
                # 로컬 파일 저장
                summarizer.save_summary_to_file(comprehensive_result, "comprehensive")
                console.print("✅ 로컬 파일 저장 완료", style="green")
        
        # 최종 결과 표시
        console.print(Panel("🎉 대화형 회의 파이프라인 완료!", style="bold green"))
        
        # 결과 테이블
        table = Table(title="회의 요약 결과")
        table.add_column("항목", style="cyan")
        table.add_column("내용", style="white")
        
        table.add_row("회의 ID", comprehensive_result['meeting_id'])
        table.add_row("지속시간", f"{structured_content['duration']:.1f}초")
        table.add_row("단어 수", str(structured_content['word_count']))
        table.add_row("액션 아이템", str(len(comprehensive_result['action_items'])))
        table.add_row("결정사항", str(len(comprehensive_result['decisions'])))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ 파이프라인 오류: {e}", style="red")
        logger.error(f"파이프라인 오류: {e}")


@app.command()
def full_pipeline(
    title: str = typer.Option("회의", help="회의 제목"),
    duration: Optional[int] = typer.Option(None, help="녹음 시간 (분)"),
    language: str = typer.Option("ko", help="언어 코드"),
    save_to_notion: bool = typer.Option(True, help="Notion에 저장"),
    local_only: bool = typer.Option(False, help="로컬 Whisper만 사용 (비용 절약)")
):
    """전체 파이프라인 실행 (녹음 → 인식 → 요약 → 저장)"""
    console.print(Panel("🚀 AI 회의 요약 전체 파이프라인", style="bold blue"))
    
    try:
        # 1단계: 녹음
        console.print("\n🎤 1단계: 회의 녹음", style="bold yellow")
        recorder = MeetingRecorder()
        success = recorder.start_meeting_recording(title, duration)
        
        if not success:
            console.print("❌ 녹음 시작 실패", style="red")
            return
        
        console.print("✅ 녹음이 시작되었습니다. 중지하려면 Ctrl+C를 누르세요.", style="green")
        
        try:
            while recorder.recorder.is_recording:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n🛑 녹음 중지 요청됨", style="yellow")
        
        audio_file = recorder.stop_recording()
        if not audio_file:
            console.print("❌ 녹음 저장 실패", style="red")
            return
        
        console.print(f"✅ 녹음 완료: {audio_file}", style="green")
        
        # 2단계: 오디오 처리 및 음성 인식
        console.print("\n🎯 2단계: 음성 인식", style="bold yellow")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            # 오디오 처리
            task1 = progress.add_task("오디오 처리 중...", total=100)
            processor = MeetingAudioProcessor()
            processed_file, chunks = processor.process_meeting_audio(audio_file)
            progress.update(task1, completed=100)
            
            # 음성 인식
            task2 = progress.add_task("음성 인식 중...", total=100)
            transcriber = MeetingTranscriber()
            
            if len(chunks) > 1:
                chunk_paths = [processor._save_processed_audio(chunk, config.audio.sample_rate, f"chunk_{i}.wav") for i, chunk in enumerate(chunks)]
                transcription_result = transcriber.transcribe_meeting_chunks(chunk_paths, language)
            else:
                transcription_result = transcriber.transcribe_meeting(processed_file, language)
            
            progress.update(task2, completed=100)
        
        # 텍스트 포맷팅
        formatter = TextFormatter()
        structured_content = formatter.structure_meeting_content(transcription_result)
        console.print(f"✅ 음성 인식 완료: {structured_content['word_count']}단어", style="green")
        
        # 3단계: 요약 생성
        console.print("\n🤖 3단계: 회의 요약", style="bold yellow")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            # GPT 요약
            task3 = progress.add_task("GPT 요약 생성 중...", total=100)
            summarizer = MeetingSummarizer()
            comprehensive_result = summarizer.summarize_meeting_comprehensive(structured_content)
            progress.update(task3, completed=100)
        
        console.print(f"✅ 요약 완료: {len(comprehensive_result['action_items'])}개 액션 아이템", style="green")
        
        # 4단계: Notion 저장
        if save_to_notion:
            console.print("\n📝 4단계: Notion 저장", style="bold yellow")
            
            try:
                page_builder = MeetingPageBuilder()
                notion_result = page_builder.create_meeting_page(comprehensive_result)
                console.print(f"✅ Notion 저장 완료: {notion_result['url']}", style="green")
            except Exception as e:
                console.print(f"⚠️ Notion 저장 실패: {e}", style="yellow")
                console.print("로컬 파일로 저장합니다.", style="yellow")
                
                # 로컬 파일 저장
                summarizer.save_summary_to_file(comprehensive_result, "comprehensive")
                console.print("✅ 로컬 파일 저장 완료", style="green")
        
        # 최종 결과 표시
        console.print(Panel("🎉 전체 파이프라인 완료!", style="bold green"))
        
        # 결과 테이블
        table = Table(title="회의 요약 결과")
        table.add_column("항목", style="cyan")
        table.add_column("내용", style="white")
        
        table.add_row("회의 ID", comprehensive_result['meeting_id'])
        table.add_row("지속시간", f"{structured_content['duration']:.1f}초")
        table.add_row("단어 수", str(structured_content['word_count']))
        table.add_row("액션 아이템", str(len(comprehensive_result['action_items'])))
        table.add_row("결정사항", str(len(comprehensive_result['decisions'])))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ 파이프라인 오류: {e}", style="red")
        logger.error(f"파이프라인 오류: {e}")


@app.command()
def test_apis():
    """API 연결 테스트"""
    console.print(Panel("🔧 API 연결 테스트", style="bold blue"))
    
    # OpenAI API 테스트
    console.print("\n🤖 OpenAI API 테스트", style="yellow")
    try:
        from src.summarization import GPTClient
        gpt_client = GPTClient()
        console.print("✅ OpenAI API 연결 성공", style="green")
    except Exception as e:
        console.print(f"❌ OpenAI API 연결 실패: {e}", style="red")
    
    # Notion API 테스트
    console.print("\n📝 Notion API 테스트", style="yellow")
    try:
        page_builder = MeetingPageBuilder()
        test_result = page_builder.test_notion_integration()
        
        if test_result["status"] == "success":
            console.print("✅ Notion API 연결 성공", style="green")
        else:
            console.print(f"❌ Notion API 연결 실패: {test_result.get('error', 'Unknown error')}", style="red")
    except Exception as e:
        console.print(f"❌ Notion API 연결 실패: {e}", style="red")
    
    # Whisper 테스트
    console.print("\n🎯 Whisper 테스트", style="yellow")
    try:
        from src.transcription import WhisperClient
        whisper_client = WhisperClient()
        console.print("✅ Whisper 모델 로드 성공", style="green")
    except Exception as e:
        console.print(f"❌ Whisper 모델 로드 실패: {e}", style="red")


@app.command()
def list_meetings():
    """저장된 회의 목록 조회"""
    console.print(Panel("📋 저장된 회의 목록", style="bold blue"))
    
    try:
        page_builder = MeetingPageBuilder()
        summary = page_builder.get_meeting_pages_summary(limit=20)
        
        if summary["total_pages"] == 0:
            console.print("저장된 회의가 없습니다.", style="yellow")
            return
        
        # 회의 목록 테이블
        table = Table(title="회의 목록")
        table.add_column("제목", style="cyan")
        table.add_column("생성일", style="white")
        table.add_column("URL", style="blue")
        
        for page in summary["recent_pages"]:
            table.add_row(
                page["title"],
                page["created_time"][:10],
                page["url"]
            )
        
        console.print(table)
        console.print(f"\n총 {summary['total_pages']}개의 회의가 저장되어 있습니다.")
        
    except Exception as e:
        console.print(f"❌ 회의 목록 조회 실패: {e}", style="red")


if __name__ == "__main__":
    app()
