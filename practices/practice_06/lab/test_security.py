"""The same real HTTP attacks must be rejected without breaking ordinary actions."""

import unittest

from security_audit import audit
from service import Shop


class SecurityTest(unittest.TestCase):
    def test_http_attack_matrix(self):
        result = audit()
        for check in result["checks"]:
            with self.subTest(attack=check["name"]):
                self.assertTrue(check["passed"], str(check)[:1500])


class AuthorizationTest(unittest.TestCase):
    def setUp(self):
        self.shop = Shop()
        self.addCleanup(self.shop.close)
        _, result = self.shop.dispatch("POST", "/login", {"username": "alice", "password": "learn-alice"}, {})
        self.auth = {"X-Token": result["token"]}

    def call(self, method, path, body=None):
        return self.shop.dispatch(method, path, body or {}, self.auth)

    def test_expired_session_cannot_authorize(self):
        self.shop.sessions[self.auth["X-Token"]]["expires"] = 0
        self.assertEqual(self.call("GET", "/orders")[0], 401)

    def test_symlink_cannot_cross_owner_boundary(self):
        link = self.shop.sandbox.root / "files/alice/other"
        link.symlink_to(self.shop.sandbox.root / "files/bob", target_is_directory=True)
        for method, path, body in (
            ("GET", "/files?path=other/receipt.txt", None),
            ("POST", "/assistant/execute", {"decision": {"tool": "read_file", "arguments": {"path": "files/alice/other/receipt.txt"}}}),
        ):
            with self.subTest(path=path):
                self.assertEqual(self.call(method, path, body)[0], 403)

    def test_absolute_and_parent_tool_paths_rejected(self):
        for path in ("/etc/passwd", "../../outside", "files/alice/../bob/receipt.txt", "private/operator-note.txt"):
            with self.subTest(path=path):
                self.assertEqual(self.call("POST", "/assistant/execute", {
                    "decision": {"tool": "read_file", "arguments": {"path": path}}
                })[0], 403)

    def test_malformed_tool_schema_rejected(self):
        for decision in (None, [], {"tool": []}, {"tool": "read_file", "arguments": []},
                         {"tool": "read_file", "arguments": {"path": 1}},
                         {"tool": "read_file", "arguments": {"path": "files/alice/receipt.txt", "role": "staff"}},
                         {"tool": "refuse", "arguments": {}}, {"tool": "shell", "arguments": {}}):
            with self.subTest(decision=decision):
                self.assertEqual(self.call("POST", "/assistant/execute", {"decision": decision})[0], 400)

    def test_logs_and_reviews_bounded(self):
        for _ in range(220):
            self.call("POST", "/reviews", {"product": "chair", "text": "ok"})
        self.assertEqual(len(self.shop.logs), 200)
        self.assertEqual(len(self.shop.reviews), 200)

    def test_missing_order_and_file_return_404(self):
        self.assertEqual(self.call("GET", "/assistant/context?order_id=999")[0], 404)
        self.assertEqual(self.call("GET", "/files?path=missing.txt")[0], 404)

    def test_context_keeps_reviews_as_data_and_filters_products(self):
        self.call("POST", "/reviews", {"product": "lamp", "text": "OTHER_PRODUCT_REVIEW"})
        status, context = self.call("GET", "/assistant/context?order_id=1")
        self.assertEqual(status, 200)
        self.assertIn("untrusted_reviews", context["prompt"])
        self.assertNotIn("OTHER_PRODUCT_REVIEW", context["prompt"])
        self.assertIn("files/alice/receipt.txt", context["prompt"])


if __name__ == "__main__":
    unittest.main()
