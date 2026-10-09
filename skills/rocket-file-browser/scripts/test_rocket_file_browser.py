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


# The filesystems a Rocket typically lists: the internal metadata one first, then the
# configured S3 buckets.
FILESYSTEMS = [
    {"id": "hdfs1", "type": "HDFS", "defaultPath": "/"},
    {"id": "bucket-a", "type": "S3", "defaultPath": "/landing"},
]


@pytest.fixture(autouse=True)
def listed_filesystems(monkeypatch):
    """Every command resolves --fs against the listing; serve a fixed one."""
    monkeypatch.setattr(rfb, "list_filesystems", lambda: list(FILESYSTEMS))


# --- parse_fs / resolve_target_fs ------------------------------------------


def test_parse_fs():
    assert rfb.parse_fs("hdfs1:HDFS") == {"id": "hdfs1", "type": "HDFS"}
    assert rfb.parse_fs(None) is None


def test_parse_fs_splits_on_the_last_colon():
    assert rfb.parse_fs("host:8020:HDFS") == {"id": "host:8020", "type": "HDFS"}


@pytest.mark.parametrize("bad", ["no-colon", "bucket:", ":S3"])
def test_parse_fs_invalid_exits(bad):
    with pytest.raises(SystemExit):
        rfb.parse_fs(bad)


def test_resolve_fs_auto_single(monkeypatch):
    monkeypatch.setattr(rfb, "list_filesystems", lambda: [{"id": "x", "type": "HDFS"}])
    assert rfb.resolve_target_fs(None) == {"id": "x", "type": "HDFS"}


def test_resolve_fs_multiple_requires_explicit(capsys):
    with pytest.raises(SystemExit):
        rfb.resolve_target_fs(None)
    err = capsys.readouterr().err
    assert "hdfs1:HDFS" in err and "bucket-a:S3" in err


def test_resolve_fs_none_listed_exits(monkeypatch):
    monkeypatch.setattr(rfb, "list_filesystems", lambda: [])
    with pytest.raises(SystemExit):
        rfb.resolve_target_fs(None)


def test_resolve_fs_explicit_picks_a_listed_one():
    assert rfb.resolve_target_fs("bucket-a:S3") == {"id": "bucket-a", "type": "S3"}


def test_resolve_fs_explicit_type_is_normalized_to_rockets_spelling():
    assert rfb.resolve_target_fs("bucket-a:s3") == {"id": "bucket-a", "type": "S3"}


@pytest.mark.parametrize("unknown", ["bucket-b:S3", "bucket-a:HDFS", "Bucket-A:S3"])
def test_resolve_fs_explicit_unknown_exits_with_the_options(unknown, capsys):
    with pytest.raises(SystemExit):
        rfb.resolve_target_fs(unknown)
    assert "bucket-a:S3" in capsys.readouterr().err


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


def test_ls_payload_on_an_s3_bucket(monkeypatch):
    calls = _recorder(monkeypatch, FakeResp(json_data=[]))
    rfb.cmd_ls(ns(hdfs_path="/landing", fs="bucket-a:S3"))
    _, _, kwargs = calls[0]
    assert kwargs["json"]["targetFilesystem"] == {"id": "bucket-a", "type": "S3"}


def test_single_filesystem_is_still_sent_explicitly(monkeypatch):
    """Never leave targetFilesystem out: Rocket would fall back to the internal FS."""
    monkeypatch.setattr(rfb, "list_filesystems", lambda: [FILESYSTEMS[1]])
    calls = _recorder(monkeypatch, FakeResp(json_data=[]))
    rfb.cmd_ls(ns(hdfs_path="/landing", fs=None))
    _, _, kwargs = calls[0]
    assert kwargs["json"]["targetFilesystem"] == {"id": "bucket-a", "type": "S3"}


def test_success_message_names_the_filesystem(monkeypatch, capsys):
    _recorder(monkeypatch)
    rfb.cmd_cp(ns(src="/a", dst="/b", fs="bucket-a:S3"))
    assert "[bucket-a:S3]" in capsys.readouterr().out


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


def test_upload_to_an_s3_bucket(monkeypatch, tmp_path):
    src = tmp_path / "f.txt"
    src.write_text("hi")
    calls = _recorder(monkeypatch, FakeResp(json_data="/landing/f.txt"))

    rfb.cmd_upload(ns(local_src=str(src), hdfs_dir="/landing", fs="bucket-a:S3", legacy=False))

    _, _, kwargs = calls[0]
    assert kwargs["params"] == {
        "path": "/landing",
        "filesystemId": "bucket-a",
        "filesystemType": "S3",
    }


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
