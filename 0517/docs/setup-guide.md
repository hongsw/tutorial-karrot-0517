# Claude Code/opencode Manus API 설정 가이드

## 1. 준비물

- Manus API key
- Node.js 18 이상
- `curl`, `jq`
- Claude Code 또는 opencode 설치
- 테스트용 Manus 계정과 낮은 민감도의 샘플 데이터

API 키는 셸 환경변수로 둔다.

```bash
export MANUS_API_KEY="your-api-key"
```

## 2. REST 직접 호출 테스트

```bash
./scripts/manus_create_task.sh "한국어로 당근 신규 사업 확장 아이디어 5개를 조사해줘"
```

성공하면 `task_id`, `task_url`이 출력된다. 이후 공식 API의 `task.detail`과 `task.listMessages`로 상태와 결과를 조회한다.

```bash
curl -sS "https://api.manus.ai/v2/task.detail?task_id=$TASK_ID" \
  -H "x-manus-api-key: $MANUS_API_KEY"
```

```bash
curl -sS "https://api.manus.ai/v2/task.listMessages?task_id=$TASK_ID&order=asc&limit=50" \
  -H "x-manus-api-key: $MANUS_API_KEY"
```

## 3. Claude Code MCP 설정

Claude Code는 HTTP, SSE, stdio MCP 서버를 지원한다. 로컬 MCP 서버는 stdio 방식으로 실행된다.

커뮤니티 `manus-mcp`를 테스트할 경우:

```bash
claude mcp add --transport stdio --scope user \
  --env MANUS_MCP_API_KEY="$MANUS_API_KEY" \
  manus-mcp -- npx -y manus-mcp
```

확인:

```bash
claude mcp list
claude mcp get manus-mcp
```

Claude Code 세션 안에서는:

```text
/mcp
```

제거:

```bash
claude mcp remove manus-mcp
```

주의:

- `--env`, `--scope`, `--transport` 같은 옵션은 서버 이름 앞에 둔다.
- 커뮤니티 README의 예시는 v1 기본 URL을 언급할 수 있으므로 실제 호출이 v2인지 확인한다.
- 팀 공유 설정은 `--scope project` 또는 `.mcp.json`을 검토하되, API 키를 repo에 커밋하지 않는다.

## 4. opencode MCP 설정

opencode CLI:

```bash
opencode mcp add
opencode mcp list
```

전역 설정 파일 후보:

- `~/.opencode.json`
- `$XDG_CONFIG_HOME/opencode/.opencode.json`
- `~/.config/opencode/.opencode.json`

프로젝트 설정:

- `.opencode.json`

예시:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "manus-mcp": {
      "type": "local",
      "command": ["npx", "-y", "manus-mcp"],
      "enabled": true,
      "env": {
        "MANUS_MCP_API_KEY": "your-api-key"
      }
    }
  }
}
```

실제 운영에서는 `"your-api-key"`를 직접 파일에 쓰지 말고, 개인 로컬 설정 또는 secret injection 방식을 사용한다.

## 5. 사내용 최소 MCP 서버를 만들 때의 도구 범위

초기에는 아래 4개만 노출하는 것이 좋다.

- `create_manus_task`: `POST /v2/task.create`
- `get_manus_task`: `GET /v2/task.detail`
- `list_manus_messages`: `GET /v2/task.listMessages`
- `send_manus_message`: `POST /v2/task.sendMessage`

파일 업로드, connector, webhook은 PoC 이후 추가한다.

## 6. 보안 기준

- API 키는 환경변수 또는 secret manager에서 주입한다.
- MCP 서버 로그에 프롬프트, 파일 URL, 결과 전문이 남는지 확인한다.
- 커뮤니티 MCP 서버는 버전 고정 후 lockfile과 소스코드를 리뷰한다.
- `share_visibility`는 기본 `private`로 둔다.
- 파일 첨부는 만료 시간, 다운로드 URL 노출, 개인정보 포함 여부를 확인한다.
