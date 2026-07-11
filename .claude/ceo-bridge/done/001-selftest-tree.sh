#!/bin/sh
# 브리지 자가 테스트: cmux 소켓 접근 + 노드 트리 확보 (CEO가 로그로 검증)
echo "=== bridge self-test $(date '+%F %T') ==="
cmux tree --all
