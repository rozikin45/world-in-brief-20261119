"""The runtime contract is exercised without third-party site packages."""
import hashlib
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
PROGRAM = ROOT / "main.py"


class RuntimeContract(unittest.TestCase):
    def test_two_isolated_runs_write_identical_valid_bounded_png(self):
        self.assertTrue(PROGRAM.is_file(), "The Python entrypoint has not been implemented")
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR", str(ROOT))) as temp:
            outputs = []
            for name in ("first", "second"):
                destination = Path(temp) / name
                result = subprocess.run(
                    [sys.executable, "-I", "-S", str(PROGRAM),
                     "--output-dir", str(destination)],
                    check=True, capture_output=True, text=True, timeout=20,
                )
                self.assertEqual(result.returncode, 0)
                self.assertEqual(sorted(p.name for p in destination.iterdir()), ["entry.png"])
                data = (destination / "entry.png").read_bytes()
                self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                width, height = struct.unpack(">II", data[16:24])
                self.assertGreater(width, 0)
                self.assertGreater(height, 0)
                self.assertLessEqual(width, 1024)
                self.assertLessEqual(height, 1024)
                self.assertLessEqual(len(data), 1_048_576)
                outputs.append(data)
            self.assertEqual(outputs[0], outputs[1])
            self.assertEqual(outputs[0], (ROOT / "entry.png").read_bytes())
            self.assertEqual(hashlib.sha256(outputs[0]).digest(),
                             hashlib.sha256(outputs[1]).digest())

    def test_corrupted_png_chunk_is_rejected_before_output(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("entry_runtime", PROGRAM)
        assert spec is not None and spec.loader is not None
        runtime = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runtime)
        data = bytearray((ROOT / "entry.png").read_bytes())
        offset = 8
        while offset + 12 <= len(data):
            length = struct.unpack(">I", data[offset:offset + 4])[0]
            if data[offset + 4:offset + 8] == b"IDAT" and length:
                data[offset + 8] ^= 1
                break
            offset += length + 12
        else:
            self.fail("The real image unexpectedly has no IDAT payload")
        with self.assertRaisesRegex(ValueError, "CRC"):
            runtime.validate_png(bytes(data))


if __name__ == "__main__":
    unittest.main()
