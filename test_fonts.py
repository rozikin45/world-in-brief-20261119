"""Development font lookup; the submitted runtime never loads a font."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import render


class ExternalFontLookup(unittest.TestCase):
    def resolver(self):
        self.assertTrue(hasattr(render, "resolve_font_path"),
                        "An external development-font resolver has not been implemented")
        return getattr(render, "resolve_font_path")

    def test_explicit_installed_font_directory_is_honoured(self):
        resolve = self.resolver()
        directory = Path("/usr/share/fonts/truetype/noto")
        expected = directory / render.FONTS["bold"]
        if not expected.is_file():
            self.skipTest("Install the documented Noto development fonts for this test")
        with patch.dict(os.environ, {"NEWS_FONT_DIR": str(directory)}):
            self.assertEqual(resolve("bold").resolve(), expected.resolve())

    def test_missing_explicit_font_directory_fails_clearly(self):
        resolve = self.resolver()
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as directory:
            with patch.dict(os.environ, {"NEWS_FONT_DIR": directory}):
                with self.assertRaisesRegex(FileNotFoundError, "Noto"):
                    resolve("bold")


if __name__ == "__main__":
    unittest.main()
