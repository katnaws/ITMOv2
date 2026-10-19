"""Small MCP 2025-06-18 stdio transport, using only the standard library."""
import json
import sys
import sqlite3


def serve(name, tools, handlers):
    initialized = False
    for line in sys.stdin:
        request = None
        try:
            request = json.loads(line)
            if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
                raise ValueError("Expected a JSON-RPC 2.0 object")
            method = request.get("method")
            if "id" not in request:
                continue  # notifications never receive responses
            error = None
            if method == "initialize":
                initialized = True
                result = {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}},
                          "serverInfo": {"name": name, "version": "1.0.0"}}
            elif method == "ping":
                result = {}
            elif not initialized:
                error = {"code": -32600, "message": "Initialize first"}
            elif method == "tools/list":
                result = {"tools": tools}
            elif method == "tools/call":
                params = request.get("params", {})
                if not isinstance(params, dict) or params.get("name") not in handlers:
                    error = {"code": -32602, "message": "Unknown tool"}
                else:
                    try:
                        arguments = params.get("arguments", {})
                        if not isinstance(arguments, dict):
                            raise ValueError("arguments must be an object")
                        value = handlers[params["name"]](**arguments)
                        result = {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}],
                                  "isError": False}
                    except (ValueError, TypeError, OSError, sqlite3.Error) as exc:
                        result = {"content": [{"type": "text", "text": str(exc)}], "isError": True}
            else:
                error = {"code": -32601, "message": "Method not found"}
            response = {"jsonrpc": "2.0", "id": request["id"]}
            response["error" if error else "result"] = error if error else result
        except (ValueError, TypeError) as exc:
            response = {"jsonrpc": "2.0", "id": request.get("id") if isinstance(request, dict) else None,
                        "error": {"code": -32700, "message": str(exc)}}
        print(json.dumps(response, ensure_ascii=False), flush=True)
