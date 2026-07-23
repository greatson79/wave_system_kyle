#!/bin/bash
# 자원 실측 샘플러 (CSO 자원전담) — READ-ONLY. kill/설정변경 일절 없음.
# 사용: res_sample.sh [간격초] [반복횟수]   기본 300초 × 96회(=8시간)
# 출력: TSV 1행/샘플 → output/WaveAI/경영본부/_round/자원감시_로그_YYYY-MM-DD.tsv

set -u
INTERVAL="${1:-300}"
COUNT="${2:-96}"
OUTDIR="/Users/kylechoi/Desktop/Ai_works/output/WaveAI/경영본부/_round"

sample() {
  local ts load1 load5 freepct swap_used mcp_n mcp_gb agent_n gpu_util gpu_mb fp_cpu
  ts=$(date "+%Y-%m-%d %H:%M:%S")
  read -r load1 load5 <<<"$(sysctl -n vm.loadavg | awk '{print $2, $3}')"
  freepct=$(memory_pressure 2>/dev/null | awk -F': ' '/free percentage/{gsub("%","",$2); print $2}')
  swap_used=$(sysctl -n vm.swapusage | awk '{gsub("M","",$6); print $6}')
  # MCP/서브프로세스 집계
  read -r mcp_n mcp_gb <<<"$(ps -Ao rss=,args= | grep -E 'npm exec|_npx|mcp-server|serena|mcp@' | grep -v grep \
    | awk '{s+=$1; n++} END {printf "%d %.2f", n+0, s/1048576}')"
  # 에이전트 메인 세션 수(claude/codex, 보조프로세스 제외)
  # tty 단위 유일 카운트(코덱스는 세션당 노드 래퍼 3프로세스 → 중복계상 방지)
  agent_n=$(ps -Ao tty=,args= | grep -E 'bin/claude|(^| )claude --|bin/codex' \
    | grep -vE 'bg-pty|bg-spare|daemon run|grep' | awk '$1!="??"{print $1}' | sort -u | wc -l | tr -d ' ')
  # GPU
  read -r gpu_util gpu_mb <<<"$(ioreg -r -d 1 -w 0 -c IOAccelerator 2>/dev/null | python3 -c "
import sys,re
t=sys.stdin.read()
u=re.search(r'\"Device Utilization %\"=(\d+)',t); m=re.search(r'\"In use system memory\"=(\d+)',t)
print(u.group(1) if u else -1, round(int(m.group(1))/1048576) if m else -1)" 2>/dev/null || echo "-1 -1")"
  fp_cpu=$(ps -Ao %cpu=,comm= | grep -E 'fileproviderd|iCloudDriveCore|cloudd' | awk '{s+=$1} END {printf "%.1f", s+0}')
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$ts" "$load1" "$load5" "$freepct" "$swap_used" "$agent_n" "$mcp_n" "$mcp_gb" "$gpu_util" "$gpu_mb" "$fp_cpu"
}

i=0
while [ "$i" -lt "$COUNT" ]; do
  OUT="$OUTDIR/자원감시_로그_$(date +%F).tsv"
  if [ ! -f "$OUT" ]; then
    printf "ts\tload1\tload5\tmem_free_pct\tswap_used_MB\tagent_sessions\tmcp_procs\tmcp_RSS_GB\tgpu_util_pct\tgpu_inuse_MB\ticloud_cpu_pct\n" >"$OUT"
  fi
  sample >>"$OUT"
  i=$((i+1))
  [ "$i" -lt "$COUNT" ] && sleep "$INTERVAL"
done
