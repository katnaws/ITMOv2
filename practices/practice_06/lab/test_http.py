"""Exercise the real HTTP transport without an LLM or third-party packages."""

import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from service import Shop, make_handler


class HttpTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shop = Shop()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(cls.shop))
        cls.server.daemon_threads = True
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=5)
        cls.server.server_close()
        cls.shop.close()

    def call(self, method, path, body=None, headers=None):
        headers = {"Content-Type": "application/json", **(headers or {})}
        request = Request(self.base + path, data=json.dumps(body).encode() if body is not None else None,
                          headers=headers, method=method)
        try:
            response = urlopen(request, timeout=5)
        except HTTPError as exc:
            response = exc
        with response:
            return response.status, response.headers, response.read().decode()

    def test_login_and_purchase_over_http(self):
        status, _, body = self.call("POST", "/login", {"username": "alice", "password": "learn-alice"})
        self.assertEqual(status, 200)
        token = json.loads(body)["token"]
        status, headers, body = self.call("POST", "/orders", {"product": "chair"}, {"X-Token": token})
        self.assertEqual(status, 201)
        self.assertIn("application/json", headers["Content-Type"])
        self.assertEqual(json.loads(body)["price"], 5000)

    def test_health_and_not_found(self):
        status, _, body = self.call("GET", "/health")
        self.assertEqual((status, json.loads(body)), (200, {"status": "ok"}))
        self.assertEqual(self.call("GET", "/missing")[0], 404)

    def test_transport_only_binds_loopback(self):
        self.assertEqual(self.server.server_address[0], "127.0.0.1")

    def test_invalid_json_types_and_duplicates(self):
        for raw in (b'{', b'[]', b'null', b'1', b'{"username":NaN}',
                    b'{"username":"alice","username":"staff"}', b'\xff'):
            with self.subTest(raw=raw):
                connection = HTTPConnection(*self.server.server_address, timeout=5)
                try:
                    connection.request("POST", "/login", body=raw, headers={"Content-Type": "application/json"})
                    response = connection.getresponse()
                    self.assertEqual(response.status, 400)
                    self.assertNotIn("type", json.loads(response.read()))
                finally:
                    connection.close()

    def test_invalid_content_lengths_and_transfer_encoding(self):
        for fields, expected in (([("Content-Length", "-1")], 400),
                                 ([("Content-Length", "bad")], 400),
                                 ([("Content-Length", "65537")], 413),
                                 ([("Content-Length", "0"), ("Content-Length", "1")], 400),
                                 ([("Transfer-Encoding", "chunked")], 400)):
            with self.subTest(fields=fields):
                connection = HTTPConnection(*self.server.server_address, timeout=5)
                try:
                    connection.putrequest("POST", "/login")
                    connection.putheader("Content-Type", "application/json")
                    for key, value in fields:
                        connection.putheader(key, value)
                    connection.endheaders()
                    response = connection.getresponse()
                    self.assertEqual(response.status, expected)
                    response.read()
                finally:
                    connection.close()

    def test_json_content_type_required(self):
        self.assertEqual(self.call("POST", "/login", {}, {"Content-Type": "text/plain"})[0], 415)

    def test_unpaired_surrogate_cannot_poison_public_reviews(self):
        _, _, body = self.call("POST", "/login", {"username": "alice", "password": "learn-alice"})
        auth = {"X-Token": json.loads(body)["token"]}
        for text in ("\ud800", "\udfff"):
            with self.subTest(text=repr(text)):
                status, _, _ = self.call("POST", "/reviews", {"product": "chair", "text": text}, auth)
                self.assertEqual(status, 400)
        self.assertEqual(self.call("GET", "/reviews/view")[0], 200)

    def test_duplicate_and_excessive_query_parameters(self):
        self.assertEqual(self.call("GET", "/profile?id=1&id=2")[0], 400)
        query = "&".join(f"p{i}=x" for i in range(21))
        self.assertEqual(self.call("GET", "/health?" + query)[0], 400)

    def test_response_security_headers(self):
        _, headers, _ = self.call("GET", "/reviews/view")
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertIn("default-src 'none'", headers["Content-Security-Policy"])


if __name__ == "__main__":
    unittest.main()
