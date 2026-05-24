# SESSION 2 실습 — 큰 비용 없이 1인 사업 기반 만들기

**목표**: 오늘 저녁 안에 내 사이트를 인터넷에 올린다  
**소요**: 약 10분  
**비용**: 0원

---

## STEP 1 · miri.dev로 사이트 30초 배포 (비개발자 OK)

> [miri.dev](https://www.miri.dev) — 드래그앤드롭, 로그인 불필요, HTTPS 자동, 무료

### 방법 A: 폴더 드래그앤드롭

```bash
# 1. 아래 내용으로 index.html 만들기
cat > ~/my-site/index.html << 'EOF'
<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8"><title>내 1인 사업</title></head>
<body>
  <h1>안녕하세요 👋</h1>
  <p>AI로 운영하는 1인 사업입니다.</p>
</body>
</html>
EOF

# 2. miri.dev 열고 ~/my-site 폴더를 드래그앤드롭
open https://www.miri.dev
```

**→ 30초 안에 `xxxx.miri.dev` 주소로 공개됩니다.**

---

### 방법 B: 링크모아 템플릿 클론 → miri.dev 배포 (추천)

당근 세션 후원사 [baryonlabs의 free-linkmoa](https://github.com/baryonlabs/free-linkmoa) 템플릿 사용

```bash
# 1. 다운로드 (git 없어도 됨 — ZIP 다운로드도 가능)
git clone https://github.com/baryonlabs/free-linkmoa my-linkmoa
cd my-linkmoa

# 2. 내 정보로 수정 (에디터 없으면 nano로)
nano index.html
# 또는 VSCode/Cursor에서 열기

# 3. miri.dev에 my-linkmoa 폴더 드래그앤드롭
open https://www.miri.dev
```

---

### 방법 C: miri.dev CLI (개발자)

```bash
# 설치
npm install -g miri-cli   # 또는 문서 확인: miri.dev/hosting-guide

# 배포
miri deploy ./my-site

# 결과
# ✓ Deployed: https://my-site-abc123.miri.dev
```

> 📖 전체 호스팅 비교 가이드: [miri.dev/hosting-guide](https://www.miri.dev/hosting-guide)

---

## STEP 2 · 1인 사업 4계층 스택 체크리스트

| 계층 | 무료 추천 | 설정 명령 or URL |
|------|-----------|-----------------|
| L1 코드·문서 | GitHub Free | `git init && git remote add origin <url>` |
| L2 AI 도구 | Claude.ai Free | [claude.ai](https://claude.ai) |
| L3 배포 | **miri.dev** | [miri.dev](https://www.miri.dev) → 드래그앤드롭 |
| L4 자동화 | n8n (self-host) | `docker run -p 5678:5678 n8nio/n8n` |

### L4 n8n 빠른 시작 (터미널 OK한 분)

```bash
# Docker로 n8n 로컬 실행
docker run -it --rm \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# → http://localhost:5678 열면 노코드 자동화 UI
```

---

## 오늘 할 일 1개

```
✅ miri.dev에 내 이름 / 소개 한 줄 / 연락처 올리기
   (5분 소요, 비용 0원)
```

---

## 참고 링크

- [miri.dev](https://www.miri.dev) — 드래그앤드롭 배포
- [miri.dev/hosting-guide](https://www.miri.dev/hosting-guide) — 20개 호스팅 비교표
- [github.com/baryonlabs/free-linkmoa](https://github.com/baryonlabs/free-linkmoa) — 링크모아 무료 템플릿 (MIT)
