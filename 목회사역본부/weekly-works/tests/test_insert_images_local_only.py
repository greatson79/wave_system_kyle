import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
INSERT_IMAGES_SCRIPT = Path(os.environ.get(
    "INSERT_IMAGES_SCRIPT", REPO / "src" / "scripts" / "insert-images.py"
))
DAYS = ("mon", "tue", "wed", "thu", "fri")
VARIANTS = ("adult-a4", "youth-a4", "adult-wordpress")


class InsertImagesWithoutWordPressE2E(unittest.TestCase):
    def make_fixture(self, with_legacy_config: bool):
        temp = tempfile.TemporaryDirectory(prefix="insert-images-local-only-")
        root = Path(temp.name)
        script = root / "src" / "scripts" / "insert-images.py"
        script.parent.mkdir(parents=True)
        shutil.copy2(INSERT_IMAGES_SCRIPT, script)
        # The legacy implementation imports this local module; any HTTP capability use is fatal.
        (script.parent / "requests.py").write_text(
            "def post(*args, **kwargs):\n    raise AssertionError('NETWORK_POST_CALLED')\n",
            encoding="utf-8",
        )
        if with_legacy_config:
            (root / ".wp-config.json").write_text(
                '{"site_url":"http://invalid.test","username":"test","app_password":"test"}',
                encoding="utf-8",
            )
        devotion = root / "output" / "week" / "매일묵상"
        images, original = devotion / "images", devotion / "html-original"
        images.mkdir(parents=True)
        original.mkdir()
        for day in DAYS:
            (images / f"{day}.png").write_bytes(b"\x89PNG\r\n\x1a\n")
            for variant in VARIANTS:
                (original / f"{day}-{variant}.html").write_text(
                    '<img src="[이미지_URL]"><a href="[이미지_원본_URL]">x</a>',
                    encoding="utf-8",
                )
        fake_bin = root / "bin"
        fake_bin.mkdir()
        fake_node = fake_bin / "node"
        fake_node.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        fake_node.chmod(0o755)
        return temp, root, script, devotion, fake_bin

    def run_fixture(self, with_legacy_config: bool):
        temp, root, script, devotion, fake_bin = self.make_fixture(with_legacy_config)
        self.addCleanup(temp.cleanup)
        env = os.environ | {"PATH": f"{fake_bin}:{os.environ['PATH']}"}
        proc = subprocess.run(
            [sys.executable, str(script), "1", "output/week"],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
        )
        return proc, devotion

    def assert_local_html_contract(self, devotion: Path):
        for day in DAYS:
            for variant in VARIANTS:
                html = (devotion / "html-with-images" / f"{day}-{variant}.html").read_text(encoding="utf-8")
                self.assertNotIn("[이미지_URL]", html)
                self.assertNotIn("[이미지_원본_URL]", html)
                self.assertIn(f"../images/{day}.png", html)

    def assert_success_without_network(self, proc, devotion: Path):
        output = proc.stdout + proc.stderr
        self.assertEqual(proc.returncode, 0, output)
        self.assertNotIn("NETWORK_POST_CALLED", output)
        self.assertNotIn("WordPress 업로드", output)
        self.assert_local_html_contract(devotion)

    def test_a_succeeds_without_wp_config(self):
        proc, devotion = self.run_fixture(with_legacy_config=False)
        self.assert_success_without_network(proc, devotion)

    def test_b_does_not_use_network_with_legacy_config_present(self):
        proc, devotion = self.run_fixture(with_legacy_config=True)
        self.assert_success_without_network(proc, devotion)


if __name__ == "__main__":
    unittest.main(verbosity=2)
