import unittest

from practices.practice_05.service import redact as red


class TestRedaction(unittest.TestCase):
    def test_pem_private_key(self):
        text = (
            "-----BEGIN PRIVATE KEY-----\n"
            "ABCDEF\n"
            "-----END PRIVATE KEY-----\n"
        )
        out = red.redact_diff(text)
        self.assertNotIn("BEGIN PRIVATE KEY", out)
        self.assertEqual(out.strip(), "[REDACTED]")

    def test_prefix_tokens_and_jwt(self):
        text = "sk-THISISASECRET12345 jwtToken header.payload.signature ghp_ABCDEF1234567890XYZ"
        out = red.redact_diff(text)
        self.assertNotIn("sk-THISISASECRET", out)
        self.assertNotIn("ghp_ABCDEF", out)
        self.assertIn("[REDACTED]", out)

    def test_env_pairs_and_aws(self):
        text = (
            "PASSWORD=foo SECRET='two words' TOKEN=\"three words value\" KEY=aaa "
            "AWS_ACCESS_KEY_ID='AKIA 1234' AWS_SECRET_ACCESS_KEY=SECRET KEY"
        )
        out = red.redact_diff(text)
        self.assertIn("PASSWORD=[REDACTED]", out)
        self.assertIn("SECRET=[REDACTED]", out)
        self.assertIn("TOKEN=[REDACTED]", out)
        self.assertIn("KEY=[REDACTED]", out)
        self.assertIn("AWS_ACCESS_KEY_ID=[REDACTED]", out)
        self.assertIn("AWS_SECRET_ACCESS_KEY=[REDACTED]", out)

    def test_jwt_positive_and_negative(self):
        # Positive: typical JWT starting with 'eyJ' in header
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0" \
              ".NTY3ODkwIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        out = red.redact_diff("token=" + jwt)
        self.assertNotIn(jwt, out)
        self.assertIn("[REDACTED]", out)

        # Negative: domains and dotted names should remain
        domain = "visit www.example.com and module.name.space"
        out2 = red.redact_diff(domain)
        self.assertIn("www.example.com", out2)
        self.assertIn("module.name.space", out2)


if __name__ == "__main__":
    unittest.main()
