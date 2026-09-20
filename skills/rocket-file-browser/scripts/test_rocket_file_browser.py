"""Tests for rocket_file_browser.py — payload construction, fs resolution,
restricted-path guard, the one-request upload with its legacy fallback, and the
HTTP 420 retry of that legacy commit. No network: the module-level ``request`` is
monkeypatched."""

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
        self.url = "https://rocket/x"
        self.request = types.SimpleNamespace(method="POST", url=self.url)

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


@pytest.mark.parametrize(
    "bad",
    [
        "/data/../backups/x",
        "/data/./../backups",
        "//backups",
        "/data/..//backups/../../backups/x",
    ],
)
def test_guard_rejects_restricted_via_traversal(bad):
    """A raw string comparison would miss these; normpath must collapse them first."""
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


def test_compress_rejects_several_sources_with_a_stream_codec():
    """Gzip & co. compress one file; Rocket would refuse the request."""
    with pytest.raises(SystemExit):
        rfb.cmd_compress(
            ns(archive="/data/out", sources=["/data/a", "/data/b"], codec="Gzip", fs="hdfs1:HDFS")
        )


def test_compress_accepts_tarzstd(monkeypatch):
    calls = _recorder(monkeypatch)
    rfb.cmd_compress(
        ns(archive="/data/out", sources=["/data/a", "/data/b"], codec="TarZstd", fs="hdfs1:HDFS")
    )
    assert calls[0][2]["json"]["compressionCodec"] == "TarZstd"


def test_extract_payload_with_dest(monkeypatch):
    calls = _recorder(monkeypatch)
    rfb.cmd_extract(ns(archive="/data/a.zip", dest="/data/out", fs="hdfs1:HDFS"))
    method, path, kwargs = calls[0]
    assert (method, path) == ("PUT", "/fileBrowser/extract")
    assert kwargs["json"]["files"] == [{"path": "/data/a.zip", "newPath": "/data/out"}]


def test_extract_defaults_dest_to_the_archive_directory(monkeypatch):
    """Rocket requires newPath; without --dest the archive's own directory is used."""
    calls = _recorder(monkeypatch)
    rfb.cmd_extract(ns(archive="/data/in/a.zip", dest=None, fs="hdfs1:HDFS"))
    assert calls[0][2]["json"]["files"] == [{"path": "/data/in/a.zip", "newPath": "/data/in"}]


# --- error surfacing --------------------------------------------------------


def test_non_ok_exits(monkeypatch):
    _recorder(monkeypatch, FakeResp(ok=False, status_code=403, text="forbidden"))
    with pytest.raises(SystemExit):
        rfb.cmd_ls(ns(hdfs_path="/data/x", fs="hdfs1:HDFS"))


# --- relative paths ---------------------------------------------------------


def test_guard_rejects_relative_path():
    """ProvidedPath.fromApi refuses a non-absolute path, body or query parameter."""
    with pytest.raises(SystemExit):
        rfb.cmd_ls(ns(hdfs_path="data/x", fs="hdfs1:HDFS"))


# --- upload: one request, legacy fallback, 420 retry ------------------------


def test_upload_single_request(monkeypatch, tmp_path):
    src = tmp_path / "f.txt"
    src.write_text("hi")
    calls = _recorder(monkeypatch, FakeResp(json_data="/data/f.txt"))

    rfb.cmd_upload(ns(local_src=str(src), hdfs_dir="/data", fs="hdfs1:HDFS", legacy=False))

    assert len(calls) == 1
    method, path, kwargs = calls[0]
    assert (method, path) == ("POST", "/fileBrowser/upload")
    assert kwargs["params"] == {
        "path": "/data",
        "filesystemId": "hdfs1",
        "filesystemType": "HDFS",
    }
    assert "binary" in kwargs["files"]


def test_upload_falls_back_to_the_legacy_flow(monkeypatch, tmp_path):
    """An older Rocket has no /fileBrowser/upload — the two-request flow still works."""
    src = tmp_path / "f.txt"
    src.write_text("hi")
    seq = [
        FakeResp(ok=False, status_code=404, text="not found"),
        FakeResp(json_data="/tmp/uploads/u/f.txt"),
        FakeResp(ok=True, status_code=200),
    ]
    calls = []

    def fr(method, path, **kwargs):
        calls.append((method, path, kwargs))
        return seq.pop(0)

    monkeypatch.setattr(rfb, "request", fr)
    rfb.cmd_upload(ns(local_src=str(src), hdfs_dir="/data", fs="hdfs1:HDFS", legacy=False))

    assert [c[1] for c in calls] == [
        "/fileBrowser/upload",
        "/fileBrowser/uploadLocalFile",
        "/fileBrowser/putLocalFileToHadoopFs",
    ]


def test_upload_legacy_flag_skips_the_one_shot_route(monkeypatch, tmp_path):
    src = tmp_path / "f.txt"
    src.write_text("hi")
    seq = [FakeResp(json_data="/tmp/uploads/u/f.txt"), FakeResp(ok=True, status_code=200)]
    calls = []

    def fr(method, path, **kwargs):
        calls.append((method, path, kwargs))
        return seq.pop(0)

    monkeypatch.setattr(rfb, "request", fr)
    rfb.cmd_upload(ns(local_src=str(src), hdfs_dir="/data", fs="hdfs1:HDFS", legacy=True))

    assert [c[1] for c in calls] == [
        "/fileBrowser/uploadLocalFile",
        "/fileBrowser/putLocalFileToHadoopFs",
    ]


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

    rfb.cmd_upload(ns(local_src=str(src), hdfs_dir="/data", fs="hdfs1:HDFS", legacy=True))

    assert len(calls) == 3
    assert calls[0][1] == "/fileBrowser/uploadLocalFile"
    assert calls[1][1] == "/fileBrowser/putLocalFileToHadoopFs"
    assert calls[2][1] == "/fileBrowser/putLocalFileToHadoopFs"
    assert calls[2][2]["json"]["dockerPath"] == "/tmp/uploads/u/f.txt"
