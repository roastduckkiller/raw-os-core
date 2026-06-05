import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raw_os_core import normalized_event_from_transcript_message, sender_id_from_event  # noqa: E402


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

    def test_transcript_plain_string_content_and_sender_id(self) -> None:
        obj = {
            "type": "message",
            "id": "rec-plain",
            "timestamp": "2026-06-04T01:00:00.000Z",
            "message": {
                "role": "user",
                "content": "plain string body",
                "senderId": "example-user-1",
                "sourceChannel": "telegram",
            },
        }
        event = normalized_event_from_transcript_message(obj, default_channel="telegram", default_provider="telegram")
        assert event is not None
        self.assertEqual(event["event_id"], "telegram_example-user-1_rec-plain")
        self.assertEqual(sender_id_from_event(event), "example-user-1")
        self.assertEqual(event["content_parts"][0]["text"], "plain string body")

    def test_assistant_plain_string_content(self) -> None:
        obj = {
            "type": "message",
            "id": "assist-plain",
            "timestamp": "2026-06-04T01:01:00.000Z",
            "message": {
                "role": "assistant",
                "content": "assistant plain string",
            },
        }
        event = normalized_event_from_transcript_message(
            obj,
            default_channel="telegram",
            default_provider="telegram",
            default_chat_id="telegram:example-user-1",
        )
        assert event is not None
        self.assertEqual(event["event_id"], "telegram_assistant_assist-plain")
        self.assertEqual(event["content_parts"][0]["text"], "assistant plain string")


if __name__ == "__main__":
    unittest.main()
