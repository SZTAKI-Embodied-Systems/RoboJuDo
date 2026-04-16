import json
import socket
import time
import unittest
from urllib import error, request

from robojudo.controller.ctrl_cfgs import ApiCtrlCfg
from robojudo.controller.api_ctrl import ApiCtrl


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class TestApiCtrl(unittest.TestCase):
    def setUp(self):
        self.port = _find_free_port()
        self.passkey = "test-passkey"
        self.cfg = ApiCtrlCfg(
            host="127.0.0.1",
            port=self.port,
            path="/command",
            passkey=self.passkey,
            allowed_commands=["[SHUTDOWN]", "[MOTION_SET]"],
            command_args={"[MOTION_SET]": [0, 1, 2, 18]},
        )
        self.ctrl = ApiCtrl(cfg_ctrl=self.cfg)
        self.url = f"http://127.0.0.1:{self.port}/command"
        self._wait_for_server_ready()

    def tearDown(self):
        self.ctrl._stop_server()  # noqa: SLF001

    def _wait_for_server_ready(self, timeout_s: float = 5.0):
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            try:
                self._post_json({"command": "[SHUTDOWN]", "passkey": self.passkey})
                # The command above is consumed in tests; clear to avoid leakage.
                self.ctrl.reset()
                return
            except Exception:
                time.sleep(0.05)
        self.fail("HTTP server did not start in time")

    def _post_json(self, payload: dict):
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=2) as resp:
                body = resp.read().decode("utf-8")
                return resp.getcode(), body
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8")
            return exc.code, body

    def test_accepts_command_without_arg(self):
        status, body = self._post_json({"command": "[SHUTDOWN]", "passkey": self.passkey})
        self.assertEqual(status, 200)
        self.assertIn("[SHUTDOWN]", body)

        ctrl_data = self.ctrl.get_data()
        _, commands = self.ctrl.process_triggers(ctrl_data)
        self.assertEqual(commands, ["[SHUTDOWN]"])

    def test_accepts_motion_set_with_allowed_index(self):
        status, body = self._post_json({"command": "[MOTION_SET]", "arg": 18, "passkey": self.passkey})
        self.assertEqual(status, 200)
        self.assertIn("[MOTION_SET],18", body)

        ctrl_data = self.ctrl.get_data()
        _, commands = self.ctrl.process_triggers(ctrl_data)
        self.assertEqual(commands, ["[MOTION_SET],18"])

    def test_rejects_unknown_command(self):
        status, body = self._post_json({"command": "[UNKNOWN]", "passkey": self.passkey})
        self.assertEqual(status, 422)
        self.assertIn("not allowed", body)

        ctrl_data = self.ctrl.get_data()
        _, commands = self.ctrl.process_triggers(ctrl_data)
        self.assertEqual(commands, [])

    def test_rejects_disallowed_motion_set_index(self):
        status, body = self._post_json({"command": "[MOTION_SET]", "arg": 99, "passkey": self.passkey})
        self.assertEqual(status, 422)
        self.assertIn("not allowed", body)

        ctrl_data = self.ctrl.get_data()
        _, commands = self.ctrl.process_triggers(ctrl_data)
        self.assertEqual(commands, [])

    def test_accepts_any_motion_set_index_when_none(self):
        """Test that None (default) allows any integer arg value."""
        # Create a new controller with default config (command_args has None for [MOTION_SET])
        port = _find_free_port()
        passkey = "test-passkey"
        cfg = ApiCtrlCfg(
            host="127.0.0.1",
            port=port,
            path="/command",
            passkey=passkey,
            allowed_commands=["[SHUTDOWN]", "[MOTION_SET]"],
            # command_args defaults to {"[MOTION_SET]": None}
        )
        ctrl = ApiCtrl(cfg_ctrl=cfg)
        url = f"http://127.0.0.1:{port}/command"
        
        # Wait for server ready
        deadline = time.time() + 5.0
        while time.time() < deadline:
            try:
                data = json.dumps({"command": "[SHUTDOWN]", "passkey": passkey}).encode("utf-8")
                req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
                with request.urlopen(req, timeout=2):
                    pass
                ctrl.reset()
                break
            except Exception:
                time.sleep(0.05)
        
        try:
            # Test with a very large index (should be accepted with None)
            data = json.dumps({"command": "[MOTION_SET]", "arg": 9999, "passkey": passkey}).encode("utf-8")
            req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
            with request.urlopen(req, timeout=2) as resp:
                status = resp.getcode()
            self.assertEqual(status, 200)
            
            ctrl_data = ctrl.get_data()
            _, commands = ctrl.process_triggers(ctrl_data)
            self.assertEqual(commands, ["[MOTION_SET],9999"])
        finally:
            ctrl._stop_server()  # noqa: SLF001

    def test_cfg_validation_rejects_unknown_command_args_key(self):
        with self.assertRaises(Exception):
            ApiCtrlCfg(
                passkey="test-passkey",
                allowed_commands=["[SHUTDOWN]"],
                command_args={"[MOTION_SET]": [0]},
            )

    def test_rejects_missing_passkey(self):
        status, body = self._post_json({"command": "[SHUTDOWN]"})
        self.assertEqual(status, 401)
        self.assertIn("passkey", body)

        ctrl_data = self.ctrl.get_data()
        _, commands = self.ctrl.process_triggers(ctrl_data)
        self.assertEqual(commands, [])

    def test_rejects_invalid_passkey(self):
        status, body = self._post_json({"command": "[SHUTDOWN]", "passkey": "wrong"})
        self.assertEqual(status, 401)
        self.assertIn("passkey", body)

        ctrl_data = self.ctrl.get_data()
        _, commands = self.ctrl.process_triggers(ctrl_data)
        self.assertEqual(commands, [])


if __name__ == "__main__":
    unittest.main()
