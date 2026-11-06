import contextlib
import io
import unittest

from request_system.__main__ import main


class MainTests(unittest.TestCase):
    def test_main_prints_ready_message(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(output.getvalue(), "Request System is ready.\n")


if __name__ == "__main__":
    unittest.main()
