"""Density and safety gates for the expanded editorial layout."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent


class DenseLayoutContract(unittest.TestCase):
    def runtime(self):
        path = ROOT / "render_dense.py"
        self.assertTrue(path.is_file(), "Expanded layout renderer is not implemented")
        spec = importlib.util.spec_from_file_location("dense_layout", path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_twelve_slots_stay_inside_canvas_and_do_not_overlap(self):
        module = self.runtime()
        boxes = module.layout_boxes()
        self.assertEqual(len(boxes), 12)
        for x0, y0, x1, y1 in boxes:
            self.assertGreaterEqual(x0, 0)
            self.assertGreaterEqual(y0, 0)
            self.assertLessEqual(x1, 1024)
            self.assertLessEqual(y1, 1024)
            self.assertGreater(x1, x0)
            self.assertGreater(y1, y0)
        for index, a in enumerate(boxes):
            for b in boxes[index + 1:]:
                self.assertFalse(a[0] < b[2] and b[0] < a[2]
                                 and a[1] < b[3] and b[1] < a[3])

    def test_incomplete_real_selection_cannot_be_published_as_twelve(self):
        module = self.runtime()
        document = json.loads((ROOT / "news.json").read_text())
        document["stories"] = document["stories"][:5]
        with self.assertRaisesRegex(ValueError, "12"):
            module.validate_selection(document)

    def test_provisional_full_selection_needs_explicit_qa_mode(self):
        module = self.runtime()
        document = json.loads((ROOT / "news.json").read_text())
        self.assertEqual(len(document["stories"]), 12)
        document["selection_status"] = "provisional"
        with self.assertRaisesRegex(ValueError, "final"):
            module.validate_selection(document)


if __name__ == "__main__":
    unittest.main()
