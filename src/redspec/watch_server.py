"""Minimal HTTP server for watch mode live-reload."""

from __future__ import annotations

import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


class _WatchHandler(SimpleHTTPRequestHandler):
    """HTTP handler that serves a live-reload wrapper page."""

    diagram_path: Path | None = None
    diagram_format: str = "svg"

    def do_GET(self) -> None:
        if self.path == "/":
            self._serve_wrapper()
        elif self.path == "/diagram":
            self._serve_diagram()
        else:
            self.send_error(404)

    def _serve_wrapper(self) -> None:
        fmt = self.__class__.diagram_format
        if self.__class__.diagram_path is None:
            body = "<html><head><meta http-equiv='refresh' content='2'></head><body><h3>Waiting for first build...</h3></body></html>"
        else:
            if fmt == "svg":
                embed = f'<object data="/diagram" type="image/svg+xml" width="100%" height="90%"></object>'
            else:
                embed = f'<img src="/diagram" style="max-width:100%;max-height:90%">'
            body = (
                f"<html><head><meta http-equiv='refresh' content='2'>"
                f"<title>Redspec Watch</title></head>"
                f"<body style='background:#1e1e2e;color:#cdd6f4;font-family:sans-serif;text-align:center;padding:1rem'>"
                f"<h3>Redspec Watch Mode</h3>"
                f"{embed}</body></html>"
            )

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body.encode())

    def _serve_diagram(self) -> None:
        path = self.__class__.diagram_path
        if path is None or not path.exists():
            self.send_error(404, "No diagram generated yet")
            return

        media_types = {
            "svg": "image/svg+xml",
            "png": "image/png",
            "pdf": "application/pdf",
        }
        content_type = media_types.get(self.__class__.diagram_format, "application/octet-stream")

        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: object) -> None:
        """Suppress request logging."""
        pass


class WatchServer:
    """Wrapper around HTTPServer for watch mode."""

    def __init__(self, host: str = "127.0.0.1", port: int = 9876, diagram_format: str = "svg") -> None:
        self.host = host
        self.port = port
        self.diagram_format = diagram_format

        # Create a new handler class per server instance
        self._handler_class = type(
            "_BoundHandler",
            (_WatchHandler,),
            {"diagram_path": None, "diagram_format": diagram_format},
        )
        self._server = HTTPServer((host, port), self._handler_class)
        self._thread: threading.Thread | None = None

    def update_diagram(self, path: Path) -> None:
        """Update the served diagram path."""
        self._handler_class.diagram_path = path

    def start(self) -> None:
        """Start serving in a daemon thread."""
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def shutdown(self) -> None:
        """Stop the server."""
        self._server.shutdown()

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def actual_port(self) -> int:
        return self._server.server_address[1]
