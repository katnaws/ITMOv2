"""Test/demo runtime: both data modes are isolated from personal study data."""
from pathlib import Path
import argparse
import json
import os
import signal
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "practices/practice_04/dashboard"))
from server import create_server


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--meta", required=True)
    args = parser.parse_args()
    def stop(*_):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop)
    with tempfile.TemporaryDirectory(prefix="study-space-framework-demo-") as directory:
        folder = Path(directory)
        os.environ["STUDY_TRACKER_DB"] = str(folder / "real.sqlite3")
        server = create_server(args.port, folder / "demo.sqlite3")
        server.bridge.log = folder / "calls.jsonl"
        metadata = {"pid": os.getpid(), "root": str(ROOT), "port": server.server_port,
                    "url": f"http://127.0.0.1:{server.server_port}",
                    "real_db": os.environ["STUDY_TRACKER_DB"], "demo_db": str(folder / "demo.sqlite3")}
        Path(args.meta).write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
        print(json.dumps(metadata, ensure_ascii=False), flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
