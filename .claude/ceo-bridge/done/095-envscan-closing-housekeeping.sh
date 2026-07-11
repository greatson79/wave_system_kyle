#!/bin/bash
cmux send --workspace workspace:1 --surface surface:54 "[CEO->COO] 환경스캐닝 7/3 마무리 정리 2건(주인님 확인 완료·경량) 리서치에 전달 바람: ①WF1-1 exploration 보고서(EN+KO, wf1-1-exploration/reports/daily/2026-07-03/)를 정본 폴더 output/DiA/리서치본부/환경스캐닝/2026-07-03/에 복사 ②주간완주율_매트릭스_2026-W27.md의 7/3 행 갱신 — WF3 ✅(insane-search 대체)·WF4 ✅·통합='주간보고서 대체'로 표기하고 판정을 '부분완주'->'완주(통합=주간판 대체)'로 정정, 완주율 4/7(57.1%)로 갱신. 일일 통합보고서 단독 파일은 소급 생성하지 않음(주인님 확인 — 주간 v2가 상회). 완료 시 push만."
cmux send-key --workspace workspace:1 --surface surface:54 enter
