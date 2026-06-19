from __future__ import annotations

import threading
from contextlib import contextmanager
from socketserver import TCPServer
from typing import Iterator

import pytest
from werkzeug.serving import make_server

from app import create_app


class ThreadedWSGIServer(TCPServer):
    allow_reuse_address = True


@contextmanager
def run_server() -> Iterator[str]:
    app = create_app()
    server = make_server("127.0.0.1", 0, app, threaded=True)
    host, port = server.socket.getsockname()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)


@pytest.fixture()
def app_client():
    app = create_app()
    return app.test_client()


@pytest.fixture()
def live_server_url() -> Iterator[str]:
    with run_server() as url:
        yield url
