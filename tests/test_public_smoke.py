import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicSmokeTest(unittest.TestCase):
    def test_public_smoke_script(self) -> None:
        result = subprocess.run(
            [str(ROOT / "scripts" / "raw-os-smoke")],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn("raw-os smoke ok", result.stdout)

    def test_community_config_is_synthetic(self) -> None:
        config = json.loads((ROOT / "examples" / "community.raw-os.example.json").read_text())
        self.assertEqual(config["agent"]["agentId"], "example-agent")
        self.assertEqual(config["mainlines"][0]["senderIds"], ["replace-with-human-sender-id"])

    def test_cli_doctor_with_synthetic_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.json"
            config = json.loads((ROOT / "examples" / "community.raw-os.example.json").read_text())
            config["agent"]["workspaceRoot"] = str(Path(tmp) / "workspace")
            config_path.write_text(json.dumps(config), encoding="utf-8")

            result = subprocess.run(
                [str(ROOT / "scripts" / "raw-os"), "doctor", "--config", str(config_path)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            doctor = json.loads(result.stdout)
            self.assertTrue(doctor["ok"])
            self.assertFalse(doctor["is_protected_workspace"])


if __name__ == "__main__":
    unittest.main()
