"""Tests for rocket_file_browser.py — payload construction, fs resolution,
restricted-path guard, and the HTTP 420 upload-commit retry. No network: the
module-level ``request`` is monkeypatched."""

import argparse
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rocket_file_browser as rfb  # noqa: E402


def ns(**kw) -> argparse.Namespace:
    return argparse.Namespace(**kw)


class FakeResp:
    def __init__(self, ok=True, status_code=200, json_data=None, text="", headers=None):
        self.ok = ok
        self.status_code = status_code
        self._json = json_data if json_data is not None else {}
        self.text = text
        self.headers = headers or {"content-type": "application/json"}
        self.request = types.SimpleNamespace(method="POST", url="https://rocket/x")

    def json(self):
        return self._json

    def iter_content(self, chunk_size=1):
        yield b""


def _recorder(monkeypatch, resp=None):
    calls = []

    def fake_request(method, path, **kwargs):
        calls.append((method, path, kwargs))
        return resp if resp is not None else FakeResp()

    monkeypatch.setattr(rfb, "request", fake_request)
    return calls


# --- parse_fs / resolve_target_fs ------------------------------------------


def test_parse_fs():
    assert rfb.parse_fs("hdfs1:HDFS") == {"id": "hdfs1", "type": "HDFS"}
    assert rfb.parse_fs(None) is None


def test_parse_fs_invalid_exits():
    with pytest.raises(SystemExit):
        rfb.parse_fs("no-colon")


def test_resolve_fs_auto_single(monkeypatch):
    monkeypatch.setattr(rfb, "list_filesystems", lambda: [{"id": "x", "type": "HDFS"}])
    assert rfb.resolve_target_fs(None) == {"id": "x", "type": "HDFS"}


def test_resolve_fs_multiple_requires_explicit(monkeypatch):
    monkeypatch.setattr(
        rfb, "list_filesystems",
        lambda: [{"id": "a", "type": "HDFS"}, {"id": "b", "type": "S3"}],
    )
    with pytest.raises(SystemExit):
        rfb.resolve_target_fs(None)


# --- restricted-path guard --------------------------------------------------


@pytest.mark.parametrize("bad", ["/backups", "/backups/x", "/mlProjectModelArtifacts/y"])
def test_guard_rejects_restricted(bad):
    with pytest.raises(SystemExit):
        rfb.cmd_ls(ns(hdfs_path=bad, fs="hdfs1:HDFS"))


# --- payload construction ---------------------------------------------------


def test_ls_payload(monkeypatch):
    calls = _recorder(monkeypatch, FakeResp(json_data=[]))
    rfb.cmd_ls(ns(hdfs_path="/data/x", fs="hdfs1:HDFS"))
    method, path, kwargs = calls[0]
    assert (method, path) == ("POST", "/fileBrowser/findByPath")
    assert kwargs["json"] == {
        "pathHdfs": "/data/x",
        "targetFilesystem": {"id": "hdfs1", "type": "HDFS"},
    }


def test_mkdir_payload(monkeypatch):
    calls = _recorder(monkeypatch)
    rfb.cmd_mkdir(ns(hdfs_path="/data/new", fs="hdfs1:HDFS"))
    method, path, kwargs = calls[0]
    assert (method, path) == ("POST", "/fileBrowser/createDir")
    assert kwargs["json"]["pathHdfs"] == "/data/new"


def test_rm_multi_payload(monkeypatch):
    calls = _recorder(monkeypatch)
    rfb.cmd_rm(ns(hdfs_paths=["/data/a", "/data/b"], fs="hdfs1:HDFS"))
    method, path, kwargs = calls[0]
    assert (method, path) == ("DELETE", "/fileBrowser/delete")
    assert kwargs["json"]["files"] == [{"path": "/data/a"}, {"path": "/data/b"}]


def test_cp_payload(monkeypatch):
    calls = _recorder(monkeypatch)
    rfb.cmd_cp(ns(src="/data/a", dst="/data/b", fs="hdfs1:HDFS"))
    method, path, kwargs = calls[0]
    assert (method, path) == ("PUT", "/fileBrowser/copy")
    assert kwargs["json"]["files"] == [{"path": "/data/a", "newPath": "/data/b"}]


def test_mv_payload(monkeypatch):
    calls = _recorder(monkeypatch)
    rfb.cmd_mv(ns(src="/data/a", dst="/data/b", fs="hdfs1:HDFS"))
    method, path, _ = calls[0]
    assert (method, path) == ("PUT", "/fileBrowser/update")


def test_compress_payload(monkeypatch):
    calls = _recorder(monkeypatch)
    rfb.cmd_compress(
        ns(archive="/data/out.zip", sources=["/data/a", "/data/b"], codec="Zip", fs="hdfs1:HDFS")
    )
    method, path, kwargs = calls[0]
    assert (method, path) == ("PUT", "/fileBrowser/compress")
    assert kwargs["json"] == {
        "files": ["/data/a", "/data/b"],
        "compressedFile": "/data/out.zip",
        "compressionCodec": "Zip",
        "targetFilesystem": {"id": "hdfs1", "type": "HDFS"},
    }


def test_extract_payload_with_dest(monkeypatch):
    calls = _recorder(monkeypatch)
    rfb.cmd_extract(ns(archive="/data/a.zip", dest="/data/out", fs="hdfs1:HDFS"))
    method, path, kwargs = calls[0]
    assert (method, path) == ("PUT", "/fileBrowser/extract")
    assert kwargs["json"]["files"] == [{"path": "/data/a.zip", "newPath": "/data/out"}]


# --- error surfacing --------------------------------------------------------


def test_non_ok_exits(monkeypatch):
    _recorder(monkeypatch, FakeResp(ok=False, status_code=403, text="forbidden"))
    with pytest.raises(SystemExit):
        rfb.cmd_ls(ns(hdfs_path="/data/x", fs="hdfs1:HDFS"))


# --- upload two-phase + 420 retry ------------------------------------------


def test_upload_retries_on_420(monkeypatch, tmp_path):
    src = tmp_path / "f.txt"
    src.write_text("hi")
    seq = [
        FakeResp(json_data="/tmp/uploads/u/f.txt"),     # phase 1: staged path
        FakeResp(ok=False, status_code=420),            # phase 2: busy
        FakeResp(ok=True, status_code=200),             # phase 2: ok
    ]
    calls = []

    def fr(method, path, **kwargs):
        calls.append((method, path, kwargs))
        return seq.pop(0)

    monkeypatch.setattr(rfb, "request", fr)
    monkeypatch.setattr(rfb.time, "sleep", lambda _s: None)

    rfb.cmd_upload(ns(local_src=str(src), hdfs_dir="/data", fs="hdfs1:HDFS"))

    assert len(calls) == 3
    assert calls[0][1] == "/fileBrowser/uploadLocalFile"
    assert calls[1][1] == "/fileBrowser/putLocalFileToHadoopFs"
    assert calls[2][1] == "/fileBrowser/putLocalFileToHadoopFs"
    assert calls[2][2]["json"]["dockerPath"] == "/tmp/uploads/u/f.txt"
