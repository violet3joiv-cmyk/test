#!/usr/bin/env bash
set -euo pipefail

# 사용법:
# 1) 대상 브랜치를 merge/rebase 한 뒤 충돌이 난 상태에서 실행
# 2) 이 스크립트는 현재 브랜치(ours) 기준으로 지정 파일 충돌을 정리
# 3) 이후 git commit (또는 rebase --continue)

FILES=(
  "README.md"
  "app/main.py"
  "app/services/data_sources.py"
  "app/services/notifier.py"
  "app/services/report_builder.py"
  "tests/test_report_builder.py"
)

for file in "${FILES[@]}"; do
  if git ls-files --unmerged -- "$file" | grep -q .; then
    echo "[resolve] $file -> ours"
    git checkout --ours -- "$file"
    git add "$file"
  fi
done

echo "[done] 지정 파일 충돌 정리 완료"
