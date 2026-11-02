import json
import os
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote

from practices.practice_05.service import redact
from urllib import request as urlrequest
from urllib import error as urlerror
import ssl


STATIC_ROOT = os.path.join(os.getcwd(), "practices", "practice_05", "web")

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".htm": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".mjs": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
}


class Handler(BaseHTTPRequestHandler):
    server_version = "RedactionService/1.0"

    def _write_json(self, status, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except BrokenPipeError:
            # Client aborted; avoid traceback and never log sensitive data
            pass

    def log_message(self, format, *args):
        # Override to avoid logging raw request bodies; do nothing
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/provider":
            # Provider status without secrets
            provider = "VseLLM"
            model = "openai/gpt-5"
            configured = bool(os.environ.get("VSELLM_API_KEY"))
            return self._write_json(200, {"provider": provider, "model": model, "configured": configured})
        # Serve static files from STATIC_ROOT with containment
        req_path = parsed.path
        # Default to index.html
        rel = "index.html" if req_path == "/" else req_path.lstrip("/")
        # Decode percent-encoding and normalize
        rel_decoded = unquote(rel)
        safe_path = os.path.normpath(os.path.join(STATIC_ROOT, rel_decoded))
        # Containment: must be within STATIC_ROOT
        if not safe_path.startswith(os.path.abspath(STATIC_ROOT) + os.sep) and os.path.abspath(STATIC_ROOT) != safe_path:
            return self._write_json(404, {"error": {"code": "NOT_FOUND", "message": "Not found"}})
        if os.path.isdir(safe_path):
            safe_path = os.path.join(safe_path, "index.html")
        if os.path.isfile(safe_path):
            _, ext = os.path.splitext(safe_path)
            ctype = CONTENT_TYPES.get(ext.lower(), "application/octet-stream")
            with open(safe_path, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self._write_json(200, {"message": "UI placeholder. Place static files in practices/practice_05/web/"})

    def _cors_block(self):
        # Allow only same-origin (no Origin) or exact http://127.0.0.1:<port> / http://localhost:<port>
        origin = self.headers.get("Origin")
        if not origin:
            return False
        parsed = urlparse(origin)
        if parsed.scheme != "http":
            return True
        host = parsed.hostname
        try:
            port = parsed.port if parsed.port is not None else (80 if parsed.scheme == "http" else 443)
        except ValueError:
            return True
        server_host, server_port = self.server.server_address[0], self.server.server_address[1]
        allowed = ((host in ("127.0.0.1", "localhost")) and (port == server_port))
        return not allowed

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/preview":
            if self._cors_block():
                return self._write_json(403, {"error": {"code": "FORBIDDEN", "message": "Cross-origin blocked"}})
            # Require JSON Content-Type
            ctype = self.headers.get("Content-Type", "")
            if not ctype.startswith("application/json"):
                return self._write_json(422, {"error": {"code": "UNPROCESSABLE_CONTENT", "message": "Content-Type must be application/json"}})
            # Content-Length validation
            try:
                length = int(self.headers.get("Content-Length", "0") or 0)
            except ValueError:
                return self._write_json(422, {"error": {"code": "UNPROCESSABLE_CONTENT", "message": "Invalid Content-Length"}})
            if length < 0 or length > 262144:
                return self._write_json(413, {"error": {"code": "CONTENT_TOO_LARGE", "message": "Body too large"}})
            try:
                raw = self.rfile.read(length)
                data = json.loads(raw.decode("utf-8"))
            except Exception:
                return self._write_json(422, {"error": {"code": "UNPROCESSABLE_CONTENT", "message": "Invalid JSON"}})
            diff = data.get("diff") if isinstance(data, dict) else None
            if not isinstance(diff, str) or not diff.strip():
                return self._write_json(422, {"error": {"code": "UNPROCESSABLE_CONTENT", "message": "Field 'diff' is required"}})
            if len(diff) > 20000:
                return self._write_json(413, {"error": {"code": "CONTENT_TOO_LARGE", "message": "diff exceeds 20000 characters"}})
            redacted, count = redact.redact_and_count(diff)
            return self._write_json(200, {"redacted": redacted, "redactions_count": count})
        elif parsed.path == "/api/reviews":
            if self._cors_block():
                return self._write_json(403, {"error": {"code": "FORBIDDEN", "message": "Cross-origin blocked"}})
            ctype = self.headers.get("Content-Type", "")
            if not ctype.startswith("application/json"):
                return self._write_json(422, {"error": {"code": "UNPROCESSABLE_CONTENT", "message": "Content-Type must be application/json"}})
        else:
            self._write_json(404, {"error": {"code": "NOT_FOUND", "message": "Not found"}})
            return

        try:
            length = int(self.headers.get("Content-Length", "0") or 0)
        except ValueError:
            return self._write_json(422, {"error": {"code": "UNPROCESSABLE_CONTENT", "message": "Invalid Content-Length"}})
        if length < 0 or length > 262144:
            return self._write_json(413, {"error": {"code": "CONTENT_TOO_LARGE", "message": "Body too large"}})
        try:
            raw = self.rfile.read(length)
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            return self._write_json(422, {"error": {"code": "UNPROCESSABLE_CONTENT", "message": "Invalid JSON"}})

        diff = data.get("diff") if isinstance(data, dict) else None
        if not isinstance(diff, str) or not diff.strip():
            return self._write_json(422, {"error": {"code": "UNPROCESSABLE_CONTENT", "message": "Field 'diff' is required"}})
        if len(diff) > 20000:
            return self._write_json(413, {"error": {"code": "CONTENT_TOO_LARGE", "message": "diff exceeds 20000 characters"}})

        # Apply redaction before any logging or LLM
        redacted = redact.redact_diff(diff)

        # Real LLM call via VseLLM if configured, otherwise 503
        api_key = os.environ.get("VSELLM_API_KEY")
        if not api_key:
            return self._write_json(503, {"error": {"code": "PROVIDER_NOT_CONFIGURED", "message": "LLM provider not configured"}})

        # Build messages: system rules + user diff as data; ask for strict JSON
        system_msg = (
            "Ты — ревьюер кода. Верни ТОЛЬКО JSON с полями summary (string), risks (array of up to 3 objects: {file?:string,line?:integer,evidence?:string,risk:string}), checks (array of strings)."
            " Не включай исходные секреты."
        )
        user_msg = "Данные unified diff ниже (как есть):\n\n" + redacted
        payload = json.dumps({
            "model": "openai/gpt-5",
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            "stream": False,
        }).encode("utf-8")
        req = urlrequest.Request(
            url="https://litellm.data-light.ru/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        ctx = ssl.create_default_context()
        try:
            with urlrequest.urlopen(req, context=ctx, timeout=90) as resp:
                body = resp.read().decode("utf-8")
        except urlerror.HTTPError as e:
            try:
                e.close()
            except Exception:
                pass
            return self._write_json(502, {"error": {"code": "LLM_UPSTREAM_ERROR", "message": "Upstream HTTP error"}})
        except Exception:
            return self._write_json(502, {"error": {"code": "LLM_UPSTREAM_ERROR", "message": "Upstream error"}})

        # Parse and validate model JSON response
        try:
            model_resp = json.loads(body)
            # Expect OpenAI-like response: choices[0].message.content -> JSON string
            if not isinstance(model_resp, dict):
                raise ValueError("root not dict")
            choices = model_resp.get("choices")
            if not isinstance(choices, list) or not choices:
                raise ValueError("choices invalid")
            msg = choices[0].get("message")
            if not isinstance(msg, dict) or "content" not in msg:
                raise ValueError("message invalid")
            content = msg["content"]
            if not isinstance(content, str):
                raise ValueError("content not str")
            parsed = json.loads(content)
        except Exception:
            return self._write_json(502, {"error": {"code": "LLM_UPSTREAM_ERROR", "message": "Invalid provider response"}})

        if not isinstance(parsed, dict):
            return self._write_json(502, {"error": {"code": "LLM_UPSTREAM_ERROR", "message": "Invalid fields"}})
        summary = parsed.get("summary")
        risks = parsed.get("risks")
        checks = parsed.get("checks")
        if not isinstance(summary, str) or not isinstance(risks, list) or not isinstance(checks, list):
            return self._write_json(502, {"error": {"code": "LLM_UPSTREAM_ERROR", "message": "Invalid fields"}})
        # Strict validation: every risk item must be valid; every check must be string; else -> 502
        validated_risks = []
        for r in risks:
            if not isinstance(r, dict):
                return self._write_json(502, {"error": {"code": "LLM_UPSTREAM_ERROR", "message": "Invalid risk entry"}})
            if "risk" not in r or not isinstance(r["risk"], str):
                return self._write_json(502, {"error": {"code": "LLM_UPSTREAM_ERROR", "message": "Invalid risk fields"}})
            if "file" in r and not isinstance(r["file"], str):
                return self._write_json(502, {"error": {"code": "LLM_UPSTREAM_ERROR", "message": "Invalid risk.file"}})
            if "line" in r and (not isinstance(r["line"], int) or isinstance(r["line"], bool)):
                return self._write_json(502, {"error": {"code": "LLM_UPSTREAM_ERROR", "message": "Invalid risk.line"}})
            if "evidence" in r and not isinstance(r["evidence"], str):
                return self._write_json(502, {"error": {"code": "LLM_UPSTREAM_ERROR", "message": "Invalid risk.evidence"}})
            validated_risks.append({k: r[k] for k in ("risk", "file", "line", "evidence") if k in r})
        for c in checks:
            if not isinstance(c, str):
                return self._write_json(502, {"error": {"code": "LLM_UPSTREAM_ERROR", "message": "Invalid check type"}})
        # Max 3 risks after full validation
        safe_risks = validated_risks[:3]
        safe_checks = checks
        return self._write_json(200, {"summary": summary, "risks": safe_risks, "checks": safe_checks})

        # Ensure max 3 risks
        risks = (result.get("risks") or [])[:3]
        checks = result.get("checks") or []
        summary = result.get("summary") or ""
        return self._write_json(200, {"summary": summary, "risks": risks, "checks": checks})


def make_server(host="127.0.0.1", port=8000):
    srv = ThreadingHTTPServer((host, port), Handler)
    srv.daemon_threads = True
    return srv


def serve(host="127.0.0.1", port=8000):
    # Best-effort: load .env without printing or logging secrets
    try:
        env_path = os.path.join(os.getcwd(), ".env")
        if os.path.isfile(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    if k != "VSELLM_API_KEY":
                        continue
                    v = v.strip().strip('"').strip("'")
                    if k and (k not in os.environ):
                        os.environ[k] = v
    except Exception:
        pass
    httpd = make_server(host, port)
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()
