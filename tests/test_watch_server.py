"""Tests for the watch mode HTTP server (D1)."""

import urllib.request
from pathlib import Path

from redspec.watch_server import WatchServer


class TestWatchServer:
    def test_serves_waiting_page(self):
        server = WatchServer(port=0)
        server.start()
        try:
            url = f"http://127.0.0.1:{server.actual_port}/"
            with urllib.request.urlopen(url, timeout=2) as resp:
                body = resp.read().decode()
            assert "Waiting" in body
            assert "meta" in body
        finally:
            server.shutdown()

    def test_serves_diagram_after_update(self, tmp_path):
        svg = tmp_path / "diagram.svg"
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>')

        server = WatchServer(port=0, diagram_format="svg")
        server.update_diagram(svg)
        server.start()
        try:
            url = f"http://127.0.0.1:{server.actual_port}/diagram"
            with urllib.request.urlopen(url, timeout=2) as resp:
                body = resp.read().decode()
            assert "<svg" in body
        finally:
            server.shutdown()

    def test_wrapper_has_meta_refresh(self):
        server = WatchServer(port=0)
        server.start()
        try:
            url = f"http://127.0.0.1:{server.actual_port}/"
            with urllib.request.urlopen(url, timeout=2) as resp:
                body = resp.read().decode()
            assert "http-equiv='refresh'" in body or 'http-equiv="refresh"' in body
        finally:
            server.shutdown()

    def test_svg_uses_object_tag(self, tmp_path):
        svg = tmp_path / "diagram.svg"
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>')

        server = WatchServer(port=0, diagram_format="svg")
        server.update_diagram(svg)
        server.start()
        try:
            url = f"http://127.0.0.1:{server.actual_port}/"
            with urllib.request.urlopen(url, timeout=2) as resp:
                body = resp.read().decode()
            assert "<object" in body
        finally:
            server.shutdown()

    def test_404_when_no_diagram(self):
        server = WatchServer(port=0)
        server.start()
        try:
            url = f"http://127.0.0.1:{server.actual_port}/diagram"
            try:
                urllib.request.urlopen(url, timeout=2)
                assert False, "Should have raised"
            except urllib.error.HTTPError as e:
                assert e.code == 404
        finally:
            server.shutdown()
