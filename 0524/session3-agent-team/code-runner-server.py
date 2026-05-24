#!/usr/bin/env python3
"""
Deepagent Code Execution Server
n8n → HTTP POST → 이 서버 → subprocess 실행 → 결과 반환
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess, uuid, time, os
from datetime import datetime
from typing import Optional

app = FastAPI(title="Deepagent Code Runner", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class RunRequest(BaseModel):
    script: str
    lang: str = "bash"          # bash | python | python3 | node | js
    description: str = ""
    task_id: Optional[str] = None
    timeout: int = 30           # seconds

class RunResult(BaseModel):
    task_id: str
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    elapsed_ms: int
    lang: str
    description: str
    start_time: str
    end_time: str

@app.post("/run", response_model=RunResult)
async def run_code(req: RunRequest):
    task_id = req.task_id or f"task-{uuid.uuid4().hex[:8]}"
    start = time.time()
    start_time = datetime.utcnow().isoformat()

    # 언어별 실행 명령 구성
    lang = req.lang.lower()
    if lang in ("python", "python3"):
        cmd = ["python3", "-c", req.script]
    elif lang in ("node", "javascript", "js"):
        cmd = ["node", "-e", req.script]
    elif lang in ("bash", "sh"):
        cmd = ["bash", "-c", req.script]
    else:
        # 파일 경로로 실행
        cmd = ["bash", "-c", req.script]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=req.timeout
        )
        elapsed_ms = int((time.time() - start) * 1000)
        return RunResult(
            task_id=task_id,
            success=result.returncode == 0,
            stdout=result.stdout.strip(),
            stderr=result.stderr.strip(),
            exit_code=result.returncode,
            elapsed_ms=elapsed_ms,
            lang=lang,
            description=req.description,
            start_time=start_time,
            end_time=datetime.utcnow().isoformat(),
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail=f"실행 타임아웃 ({req.timeout}초)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8899))
    print(f"🚀 Deepagent Code Runner 시작: http://localhost:{port}")
    print(f"   n8n webhook → POST http://localhost:{port}/run")
    uvicorn.run(app, host="0.0.0.0", port=port)
