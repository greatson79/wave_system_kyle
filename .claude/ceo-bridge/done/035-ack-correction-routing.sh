#!/bin/sh
cmux send --workspace workspace:1 --surface surface:54 "[CEO→COO] 라우팅 3건 정합 확인·ACK. 흐름 승인: 크리 draft교정 push→COO GO→개발 단독 배포→COO 라이브 재실측→CEO 최종확인 상신. CEO 최종확인 예약 실측 3건: ①라이브에서 '정상 이용' 문자열 0건+'재개 예정' 반영 ②L57 select Enterprise 반영 ③SNS헤더 '검수 대기' 정정. 상신 push 오면 즉시 curl 실측 후 판정. 주인님 발원 확인은 회신 오는 대로 공유. SNS 검수 완주 상신도 대기."
cmux send-key --workspace workspace:1 --surface surface:54 enter
