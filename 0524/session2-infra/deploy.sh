#!/usr/bin/env bash
# SESSION 2 실습: miri.dev 배포 준비
# 사용법: bash deploy.sh

set -euo pipefail

SITE_DIR="$HOME/my-site"
mkdir -p "$SITE_DIR"

cat > "$SITE_DIR/index.html" << 'HTML'
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>내 1인 사업</title>
  <style>
    body { font-family: sans-serif; max-width: 640px; margin: 60px auto; padding: 0 20px; }
    h1 { font-size: 2rem; }
    .links a { display: block; margin: 8px 0; color: #0066cc; }
  </style>
</head>
<body>
  <h1>안녕하세요 👋</h1>
  <p>AI로 운영하는 1인 사업입니다.</p>
  <div class="links">
    <a href="mailto:hello@example.com">연락하기</a>
  </div>
</body>
</html>
HTML

echo "✅ $SITE_DIR/index.html 생성 완료"
echo ""
echo "▶ 다음 단계:"
echo "  1. open https://www.miri.dev"
echo "  2. $SITE_DIR 폴더를 브라우저에 드래그앤드롭"
echo "  3. 30초 후 xxxx.miri.dev 주소 확인"
