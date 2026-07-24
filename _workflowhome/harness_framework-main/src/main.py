"""CLI 진입점 — Wave Academy 수강관리 시스템 전체 파이프라인."""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# src/ 디렉토리를 path에 추가 (상대 임포트 지원)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from exporters.excel_exporter import ExcelExporter
from parsers.filename_parser import parse_filename
from processors.assignment_manager import AssignmentManager
from processors.grade_calculator import calculate_all
from processors.student_processor import StudentProcessor
from utils.error_handler import Severity, log_error

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

_OUTPUT_DIR = Path("output")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Wave Academy 수강관리 파이프라인")
    p.add_argument("--scan-only", action="store_true", help="파일 스캔만 (다운로드까지)")
    p.add_argument("--export-only", action="store_true", help="기존 마스터에서 내보내기만")
    p.add_argument("--no-upload", action="store_true", help="Drive 업로드 스킵")
    p.add_argument("--master", type=Path, metavar="PATH", help="기존 마스터 Excel 경로 (업데이트 모드)")
    p.add_argument("--output", type=Path, metavar="PATH", default=_OUTPUT_DIR, help="출력 디렉토리")
    return p


def main() -> None:
    args = _build_parser().parse_args()
    output_dir: Path = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    # --export-only: 기존 마스터에서 내보내기만
    if args.export_only:
        if not args.master or not args.master.exists():
            logger.error("--export-only 사용 시 --master PATH가 필요합니다.")
            sys.exit(1)
        _run_export_only(args.master, output_dir, upload=not args.no_upload)
        return

    # Step 1: Google Drive 클라이언트 초기화
    logger.info("=== Step 1: Google Drive 초기화 ===")
    try:
        from drive.client import DriveClient
        from drive.scanner import DriveScanner
        client = DriveClient()
        scanner = DriveScanner(client)
    except FileNotFoundError as exc:
        log_error(Severity.CRITICAL, "main", "credentials.json 없음 — 인증 불가", exc=exc)
        logger.error(
            "사용자 개입 필요: Google Cloud Console에서 OAuth2 클라이언트 ID를 생성하고 "
            "credentials/credentials.json 에 저장하세요."
        )
        sys.exit(1)

    # Step 2: 파일 스캔 + 다운로드
    logger.info("=== Step 2: wave_수강신청 폴더 스캔 ===")
    scanned_files = scanner.scan()
    logger.info("스캔 완료: %d개 파일", len(scanned_files))

    if args.scan_only:
        logger.info("--scan-only: 스캔 완료 후 종료.")
        return

    if not scanned_files:
        logger.warning("처리할 파일이 없습니다. 종료.")
        return

    # Step 3: 각 파일 처리
    logger.info("=== Step 3: 수강생 데이터 처리 ===")
    processor = StudentProcessor()
    processor.load_existing(args.master)

    file_results: list[dict] = []
    for file_info in scanned_files:
        file_name = file_info["name"]
        local_path: Path | None = file_info.get("local_path")
        if not local_path or not local_path.exists():
            logger.warning("로컬 파일 없음, 스킵: %s", file_name)
            file_results.append({"name": file_name, "rows": 0, "error": True})
            continue

        parsed = parse_filename(file_name)
        try:
            rows = processor.process_file(local_path, parsed)
            logger.info("처리 완료: %s → %d행", file_name, rows)
            file_results.append({"name": file_name, "rows": rows, "error": False})
        except Exception as exc:
            log_error(Severity.HIGH, "main", f"파일 처리 실패: {file_name}", exc=exc)
            file_results.append({"name": file_name, "rows": 0, "error": True})

    # Step 4: 학점 계산
    logger.info("=== Step 4: 학점 계산 ===")
    master_df = processor.get_master()
    master_df = calculate_all(master_df)

    # Step 5: 내보내기
    logger.info("=== Step 5: Excel 내보내기 ===")
    am = AssignmentManager()
    if args.master:
        am.load_definitions(args.master)
        am.load_status(args.master)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"wave_academy_master_{timestamp}.xlsx"

    exporter = ExcelExporter()
    result_path = exporter.export(
        master_df=master_df,
        assignment_defs=am.get_definitions(),
        assignment_status=am.get_status(),
        output_path=output_path,
    )
    logger.info("Excel 생성: %s", result_path)

    # Step 6: Drive 업로드
    if not args.no_upload:
        logger.info("=== Step 6: Google Drive 업로드 ===")
        try:
            uploaded_id = client.upload_file(result_path)
            logger.info("업로드 완료: file_id=%s", uploaded_id)
        except Exception as exc:
            log_error(Severity.HIGH, "main", "Drive 업로드 실패", exc=exc)

    # 처리 결과 요약
    stats = processor.get_stats()
    error_count = sum(1 for r in file_results if r["error"])
    logger.info(
        "\n=== 처리 요약 ===\n"
        "  처리 파일: %d개 (에러: %d개)\n"
        "  수강생 — 신규: %d, 업데이트: %d, 스킵: %d, 에러: %d\n"
        "  결과 파일: %s",
        len(file_results), error_count,
        stats["new"], stats["updated"], stats["skipped"], stats["errors"],
        result_path,
    )


def _run_export_only(master_path: Path, output_dir: Path, *, upload: bool) -> None:
    """기존 마스터 Excel에서 내보내기만 실행."""
    import pandas as pd
    from utils.constants import SHEET_MASTER

    logger.info("=== export-only 모드: %s ===", master_path)
    master_df = pd.read_excel(master_path, sheet_name=SHEET_MASTER)
    master_df = calculate_all(master_df)

    am = AssignmentManager()
    am.load_definitions(master_path)
    am.load_status(master_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"wave_academy_master_{timestamp}.xlsx"

    exporter = ExcelExporter()
    result_path = exporter.export(
        master_df=master_df,
        assignment_defs=am.get_definitions(),
        assignment_status=am.get_status(),
        output_path=output_path,
    )
    logger.info("Excel 생성: %s", result_path)

    if upload:
        try:
            from drive.client import DriveClient
            client = DriveClient()
            uploaded_id = client.upload_file(result_path)
            logger.info("업로드 완료: file_id=%s", uploaded_id)
        except Exception as exc:
            log_error(Severity.HIGH, "main", "Drive 업로드 실패", exc=exc)


if __name__ == "__main__":
    main()
