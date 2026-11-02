import json
import threading
import time
import unittest
from http.client import HTTPConnection
import os
import tempfile
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from unittest import mock

from practices.practice_05.service import app


class ServerThread(threading.Thread):
    def __init__(self, host="127.0.0.1", port=0):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.httpd = app.make_server(host, port)
        # Capture the actual bound port (for port=0 ephemeral)
        self.port = self.httpd.server_address[1]

    def run(self):
        self.httpd.serve_forever()

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()


class TestHTTP(unittest.TestCase):
    def setUp(self):
        self.server = ServerThread()
        self.server.start()
        time.sleep(0.2)

    def tearDown(self):
        self.server.stop()
        # Join server thread to ensure socket released
        self.server.join(timeout=1.0)

    def _post(self, path, payload):
        conn = HTTPConnection("127.0.0.1", self.server.port, timeout=5)
        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        conn.request("POST", path, body=body, headers=headers)
        resp = conn.getresponse()
        data = resp.read()
        try:
            parsed = json.loads(data.decode("utf-8"))
            return resp.status, parsed
        except Exception:
            return resp.status, data.decode("utf-8")
        finally:
            try:
                resp.close()
            except Exception:
                pass
            conn.close()

    def test_200_redaction_and_stub(self):
        # Preview then real review with fake provider
        payload = {
            "diff": "diff --git a/a b/b\n+ token sk-XYZ\n+ -----BEGIN PRIVATE KEY-----\nABC\n-----END PRIVATE KEY-----\n"
        }
        status_prev, data_prev = self._post("/api/preview", payload)
        self.assertEqual(status_prev, 200)
        self.assertIn("redacted", data_prev)
        self.assertIn("redactions_count", data_prev)
        self.assertGreaterEqual(data_prev["redactions_count"], 1)
        # Idempotency: repeated preview shouldn't increase marker count
        status_prev2, data_prev2 = self._post("/api/preview", {"diff": data_prev["redacted"]})
        self.assertEqual(status_prev2, 200)
        self.assertEqual(data_prev2["redactions_count"], 0)

        with mock.patch("practices.practice_05.service.app.urlrequest.urlopen") as fake_urlopen:
            class Resp:
                def __init__(self, body):
                    self._b = body
                def read(self):
                    return self._b
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    return False
            fake_body = json.dumps({
                "choices": [{"message": {"content": json.dumps({
                    "summary": "Review completed",
                    "risks": [{"risk": "Example risk", "file": "a.py", "line": 10, "evidence": "changed code"}],
                    "checks": ["unit_tests"]
                })}}]
            }).encode("utf-8")
            fake_urlopen.return_value = Resp(fake_body)
            # Ensure env is set to simulate configured provider
            os.environ["VSELLM_API_KEY"] = "DUMMY"
            status, data = self._post("/api/reviews", payload)
        self.assertEqual(status, 200)
        self.assertIn("summary", data)
        self.assertIn("risks", data)
        self.assertIn("checks", data)

    def test_422_invalid(self):
        # Capture stdout/stderr to ensure no raw diff leaks
        buf_out, buf_err = StringIO(), StringIO()
        with redirect_stdout(buf_out), redirect_stderr(buf_err):
            status, data = self._post("/api/reviews", {"diff": 123})
        self.assertEqual(status, 422)
        self.assertEqual(data.get("error", {}).get("code"), "UNPROCESSABLE_CONTENT")
        status2, data2 = self._post("/api/reviews", {"diff": "   "})
        self.assertEqual(status2, 422)
        self.assertEqual(data2.get("error", {}).get("code"), "UNPROCESSABLE_CONTENT")
        # malformed JSON
        conn = HTTPConnection("127.0.0.1", self.server.port, timeout=5)
        with redirect_stdout(buf_out), redirect_stderr(buf_err):
            conn.request("POST", "/api/reviews", body=b"{not json", headers={"Content-Type": "application/json"})
            resp = conn.getresponse()
            data = resp.read().decode("utf-8")
        self.assertEqual(resp.status, 422)
        self.assertIn("UNPROCESSABLE_CONTENT", data)
        resp.close(); conn.close()
        # Ensure no secret/raw diff printed
        self.assertNotIn("sk-", buf_out.getvalue() + buf_err.getvalue())

    def test_provider_strict_validation(self):
        # Root list/null -> 502
        os.environ["VSELLM_API_KEY"] = "DUMMY"
        with mock.patch("practices.practice_05.service.app.urlrequest.urlopen") as fake_urlopen:
            class Resp:
                def __init__(self, body): self._b = body
                def read(self): return self._b
                def __enter__(self): return self
                def __exit__(self,*a): return False
            bad_root = json.dumps(["not", "dict"]).encode("utf-8")
            fake_urlopen.return_value = Resp(bad_root)
            status, data = self._post("/api/reviews", {"diff":"diff --git a a\n+ change"})
            self.assertEqual(status, 502)
        # Risks wrong type -> 502
        with mock.patch("practices.practice_05.service.app.urlrequest.urlopen") as fake_urlopen:
            bad_body = json.dumps({
                "choices": [{"message": {"content": json.dumps({
                    "summary": "S", "risks": ["bad"], "checks": ["ok"]
                })}}]
            }).encode("utf-8")
            fake_urlopen.return_value = Resp(bad_body)
            status, data = self._post("/api/reviews", {"diff":"diff --git a a\n+ change"})
            self.assertEqual(status, 502)
        # Checks wrong type -> 502
        with mock.patch("practices.practice_05.service.app.urlrequest.urlopen") as fake_urlopen:
            bad_body = json.dumps({
                "choices": [{"message": {"content": json.dumps({
                    "summary": "S", "risks": [{"risk":"r"}], "checks": [1]
                })}}]
            }).encode("utf-8")
            fake_urlopen.return_value = Resp(bad_body)
            status, data = self._post("/api/reviews", {"diff":"diff --git a a\n+ change"})
            self.assertEqual(status, 502)

    def test_413_limit(self):
        payload = {"diff": "x" * 20001}
        status, data = self._post("/api/reviews", payload)
        self.assertEqual(status, 413)
        self.assertEqual(data.get("error", {}).get("code"), "CONTENT_TOO_LARGE")
        # Exactly 20000 passes
        with mock.patch("practices.practice_05.service.app.urlrequest.urlopen") as fake_urlopen:
            class Resp:
                def __init__(self, body):
                    self._b = body
                def read(self):
                    return self._b
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    return False
            fake_body = json.dumps({
                "choices": [{"message": {"content": json.dumps({
                    "summary": "OK",
                    "risks": [],
                    "checks": ["boundary"]
                })}}]
            }).encode("utf-8")
            fake_urlopen.return_value = Resp(fake_body)
            os.environ["VSELLM_API_KEY"] = "DUMMY"
            status_ok, data_ok = self._post("/api/reviews", {"diff": "x" * 20000})
        self.assertEqual(status_ok, 200)

    def test_502_provider_error(self):
        payload = {"diff": "diff --git a a\n+ change"}
        os.environ["VSELLM_API_KEY"] = "DUMMY"
        with mock.patch("practices.practice_05.service.app.urlrequest.urlopen", side_effect=Exception("timeout")):
            status, data = self._post("/api/reviews", payload)
        self.assertEqual(status, 502)
        self.assertEqual(data.get("error", {}).get("code"), "LLM_UPSTREAM_ERROR")

    def test_static_serving_and_containment(self):
        # Use a temporary directory as STATIC_ROOT without touching real UI files
        with tempfile.TemporaryDirectory() as static_root:
            old_root = app.STATIC_ROOT
            app.STATIC_ROOT = static_root
            index = os.path.join(static_root, "index.html")
            app_js = os.path.join(static_root, "app.js")
            css = os.path.join(static_root, "style.css")

            with open(index, "w", encoding="utf-8") as f:
                f.write("<html><body>Hello</body></html>")
            with open(app_js, "w", encoding="utf-8") as f:
                f.write("console.log('ok');")
            with open(css, "w", encoding="utf-8") as f:
                f.write("body{}")

            # GET /
            conn = HTTPConnection("127.0.0.1", self.server.port, timeout=5)
            conn.request("GET", "/")
            resp = conn.getresponse(); data = resp.read();
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.getheader("Content-Type"), "text/html; charset=utf-8")
            resp.close(); conn.close()

            # GET /app.js
            conn = HTTPConnection("127.0.0.1", self.server.port, timeout=5)
            conn.request("GET", "/app.js")
            resp = conn.getresponse(); data = resp.read();
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.getheader("Content-Type"), "application/javascript; charset=utf-8")
            resp.close(); conn.close()

            # GET /style.css
            conn = HTTPConnection("127.0.0.1", self.server.port, timeout=5)
            conn.request("GET", "/style.css")
            resp = conn.getresponse(); data = resp.read();
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.getheader("Content-Type"), "text/css; charset=utf-8")
            resp.close(); conn.close()

            # Traversal attempt (percent-encoded)
            conn = HTTPConnection("127.0.0.1", self.server.port, timeout=5)
            conn.request("GET", "/..%2f..%2fetc%2fpasswd")
            resp = conn.getresponse(); data = resp.read().decode();
            self.assertIn(resp.status, (200, 404))
            # Should not return file contents of system files; expect placeholder or not found
            self.assertNotIn("root:", data)
            resp.close(); conn.close()

            app.STATIC_ROOT = old_root

    def test_origin_and_mime_and_length(self):
        # Wrong origin
        conn = HTTPConnection("127.0.0.1", self.server.port, timeout=5)
        conn.request("POST", "/api/preview", body=json.dumps({"diff":"x"}).encode(), headers={"Content-Type":"application/json","Origin":f"http://localhost.evil:{self.server.port}"})
        resp = conn.getresponse(); data = resp.read().decode(); self.assertEqual(resp.status, 403); conn.close()
        # Right origin with different port
        conn = HTTPConnection("127.0.0.1", self.server.port, timeout=5)
        conn.request("POST", "/api/preview", body=json.dumps({"diff":"x"}).encode(), headers={"Content-Type":"application/json","Origin":f"http://127.0.0.1:{self.server.port+1}"})
        resp = conn.getresponse(); _ = resp.read(); self.assertEqual(resp.status, 403); conn.close()
        # Missing JSON content type
        conn = HTTPConnection("127.0.0.1", self.server.port, timeout=5)
        conn.request("POST", "/api/preview", body=b"x", headers={"Content-Type":"text/plain"})
        resp = conn.getresponse(); _ = resp.read(); self.assertEqual(resp.status, 422); conn.close()
        # Invalid Content-Length
        conn = HTTPConnection("127.0.0.1", self.server.port, timeout=5)
        conn.putrequest("POST", "/api/preview")
        conn.putheader("Content-Type","application/json")
        conn.putheader("Content-Length","abc")
        conn.endheaders()
        resp = conn.getresponse(); _ = resp.read(); self.assertEqual(resp.status, 422); conn.close()
        # Body too large
        conn = HTTPConnection("127.0.0.1", self.server.port, timeout=5)
        conn.putrequest("POST", "/api/preview")
        conn.putheader("Content-Type","application/json")
        conn.putheader("Content-Length","300000")
        conn.endheaders()
        resp = conn.getresponse(); _ = resp.read(); self.assertEqual(resp.status, 413); conn.close()

        # Correct origin same port
        conn = HTTPConnection("127.0.0.1", self.server.port, timeout=5)
        conn.request("POST", "/api/preview", body=json.dumps({"diff":"x"}).encode(), headers={"Content-Type":"application/json","Origin":f"http://127.0.0.1:{self.server.port}"})
        resp = conn.getresponse(); _ = resp.read(); self.assertEqual(resp.status, 200); conn.close()

    def test_provider_endpoint(self):
        conn = HTTPConnection("127.0.0.1", self.server.port, timeout=5)
        conn.request("GET", "/api/provider")
        resp = conn.getresponse(); data = json.loads(resp.read().decode("utf-8"))
        self.assertEqual(resp.status, 200)
        self.assertEqual(data.get("provider"), "VseLLM")
        self.assertIn("model", data)
        self.assertIn("configured", data)
        resp.close(); conn.close()


if __name__ == "__main__":
    unittest.main()
