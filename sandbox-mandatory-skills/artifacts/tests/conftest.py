# Packs the skill once per session, the way genai-agents-sandbox receives it: its guide
# and the theme catalog only exist inside the skill once packed.

import subprocess
import zipfile
from pathlib import Path

import pytest

_SKILL = Path(__file__).resolve().parents[1]
_MONOREPO = _SKILL.parents[1]


@pytest.fixture(scope="session")
def packed_zip(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("pack")
    subprocess.run(
        ["bash", str(_MONOREPO / "pack_sandbox_mandatory_skills.sh"), "--skill", _SKILL.name,
         "--output-dir", str(out)],
        check=True,
        capture_output=True,
        text=True,
    )
    return out / "sandbox-mandatory-skills.zip"


@pytest.fixture(scope="session")
def packed_skill(packed_zip) -> Path:
    with zipfile.ZipFile(packed_zip) as zf:
        zf.extractall(packed_zip.parent / "unpacked")
    return packed_zip.parent / "unpacked" / _SKILL.name
