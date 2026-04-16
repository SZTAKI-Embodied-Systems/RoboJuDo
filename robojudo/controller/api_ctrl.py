"""API command controller for RoboJuDo.

Runs an in-process FastAPI server in a daemon thread.  POST requests are
validated against the configured ``allowed_commands`` / ``command_args`` lists
and enqueued for consumption by the pipeline's ``CtrlManager``.

Example POST requests::

    curl -sX POST http://localhost:8000/command \\
         -H 'Content-Type: application/json' \\
        -d '{"command": "[SHUTDOWN]", "passkey": "CHANGE_ME"}'

    curl -sX POST http://localhost:8000/command \\
         -H 'Content-Type: application/json' \\
        -d '{"command": "[MOTION_SET]", "arg": 18, "passkey": "CHANGE_ME"}'
"""

import logging
import threading
from queue import Empty, Queue
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from robojudo.controller import Controller, ctrl_registry
from robojudo.controller.ctrl_cfgs import ApiCtrlCfg

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Request model
# ---------------------------------------------------------------------------


class CommandRequest(BaseModel):
    command: str
    arg: int | None = None
    passkey: str | None = None


# ---------------------------------------------------------------------------
# Controller
# ---------------------------------------------------------------------------


@ctrl_registry.register
class ApiCtrl(Controller):
    """Controller that receives COMMANDS from API requests via FastAPI."""

    cfg_ctrl: ApiCtrlCfg

    def __init__(self, cfg_ctrl: ApiCtrlCfg, env=None, device="cpu"):
        super().__init__(cfg_ctrl=cfg_ctrl, env=env, device=device)

        self._command_queue: Queue[str] = Queue(maxsize=cfg_ctrl.queue_size)
        self._server: uvicorn.Server | None = None
        self._server_thread: threading.Thread | None = None

        self._start_server()
        self.reset()

    # ------------------------------------------------------------------
    # Server lifecycle
    # ------------------------------------------------------------------

    def _build_app(self) -> FastAPI:
        """Build the FastAPI application with a single POST endpoint."""
        app = FastAPI(title="RoboJuDo HTTP Command Controller", docs_url=None, redoc_url=None)
        cfg = self.cfg_ctrl
        command_queue = self._command_queue

        @app.post(cfg.path, status_code=200)
        def post_command(req: CommandRequest) -> dict[str, Any]:
            if req.passkey is None or req.passkey != cfg.passkey:
                raise HTTPException(status_code=401, detail="Invalid or missing passkey")

            command = req.command

            # Validate command is in the allowed list
            if command not in cfg.allowed_commands:
                raise HTTPException(
                    status_code=422,
                    detail=f"Command '{command}' is not allowed. "
                    f"Allowed commands: {sorted(cfg.allowed_commands)}",
                )

            needs_arg = command in cfg.command_args
            if needs_arg:
                if req.arg is None:
                    allowed_str = "all values" if cfg.command_args[command] is None else cfg.command_args[command]
                    raise HTTPException(
                        status_code=422,
                        detail=f"Command '{command}' requires an 'arg' field. "
                        f"Allowed values: {allowed_str}",
                    )
                # If command_args[command] is None, all args are accepted
                if cfg.command_args[command] is not None and req.arg not in cfg.command_args[command]:
                    raise HTTPException(
                        status_code=422,
                        detail=f"Argument {req.arg} is not allowed for command "
                        f"'{command}'. Allowed values: {cfg.command_args[command]}",
                    )
                cmd_str = f"{command},{req.arg}"
            else:
                if req.arg is not None:
                    raise HTTPException(
                        status_code=422,
                        detail=f"Command '{command}' does not accept an 'arg' field.",
                    )
                cmd_str = command

            try:
                command_queue.put_nowait(cmd_str)
            except Exception:
                raise HTTPException(
                    status_code=503,
                    detail="Command queue is full; try again later.",
                )

            logger.info(f"[ApiCtrl] Enqueued command: {cmd_str}")
            return {"status": "ok", "command": cmd_str}

        return app

    def _start_server(self):
        cfg = self.cfg_ctrl
        app = self._build_app()

        uvi_cfg = uvicorn.Config(
            app,
            host=cfg.host,
            port=cfg.port,
            log_level="warning",
            access_log=False,
        )
        self._server = uvicorn.Server(uvi_cfg)
        self._server.install_signal_handlers = lambda: None  # prevent signal hijack in thread

        self._server_thread = threading.Thread(
            target=self._server.run,
            name="ApiCtrlServer",
            daemon=True,
        )
        self._server_thread.start()
        logger.info(f"[ApiCtrl] HTTP server started on {cfg.host}:{cfg.port}{cfg.path}")

    def _stop_server(self):
        if self._server is not None:
            self._server.should_exit = True
        if self._server_thread is not None:
            self._server_thread.join(timeout=3.0)

    # ------------------------------------------------------------------
    # Controller interface
    # ------------------------------------------------------------------

    def reset(self):
        while not self._command_queue.empty():
            try:
                self._command_queue.get_nowait()
            except Empty:
                break

    def get_data(self) -> dict[str, list[str]]:
        events: list[str] = []
        while not self._command_queue.empty():
            try:
                events.append(self._command_queue.get_nowait())
            except Empty:
                break
        return {"http_commands": events}

    def process_triggers(self, ctrl_data: dict) -> tuple[dict, list[str]]:
        """Pass HTTP commands directly as pipeline COMMANDS (no trigger mapping needed)."""
        commands = list(ctrl_data.get("http_commands", []))
        return ctrl_data, commands

    def post_step_callback(self, commands=None):
        """No action needed on each step; server runs independently."""


if __name__ == "__main__":
    import time

    ctrl = ApiCtrl(
        cfg_ctrl=ApiCtrlCfg(
            host="0.0.0.0",
            port=8000,
            passkey="CHANGE_ME",
            allowed_commands=["[SHUTDOWN]", "[MOTION_SET]"],
            command_args={"[MOTION_SET]": list(range(32))},
        )
    )
    while True:
        data = ctrl.get_data()
        _, commands = ctrl.process_triggers(data)
        if commands:
            print("Commands:", commands)
        time.sleep(0.1)
