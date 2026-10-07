"""Real subprocess MCP client for demos, tests and metrics (no direct imports)."""
import json
from pathlib import Path
import subprocess
import sys
import select

ROOT = Path(__file__).resolve().parents[3]


class Client:
    def __init__(self, server, environment=None):
        self.process = subprocess.Popen(
            [sys.executable, str(ROOT / server)], cwd=ROOT, env=environment,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding="utf-8")
        self.sequence = 0

    def __enter__(self):
        self.request("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                   "clientInfo": {"name": "practice-04-demo", "version": "1.0.0"}})
        self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return self

    def __exit__(self, *args):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        self.process.stdout.close()

    def send(self, message):
        self.process.stdin.write(json.dumps(message, ensure_ascii=False) + "\n")
        self.process.stdin.flush()

    def request(self, method, params=None):
        self.sequence += 1
        self.send({"jsonrpc": "2.0", "id": self.sequence, "method": method, "params": params or {}})
        if not select.select([self.process.stdout], [], [], 10)[0]:
            raise TimeoutError(f"MCP server did not respond to {method} within 10 seconds")
        response = json.loads(self.process.stdout.readline())
        if response.get("id") != self.sequence or "error" in response:
            raise RuntimeError(response)
        return response["result"]

    def call(self, name, **arguments):
        return self.request("tools/call", {"name": name, "arguments": arguments})


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Usage: python3 practices/practice_04/mcp/client.py SERVER TOOL 'JSON_ARGUMENTS'")
    with Client(sys.argv[1]) as client:
        result = client.call(sys.argv[2], **json.loads(sys.argv[3]))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1 if result.get("isError") else 0)
