from __future__ import annotations

import io
import tarfile
from pathlib import Path

import pytest

from nemotron.recipes.omni3.stage0_sft.data_prep import _extract_valor32k_tar

CANONICAL_MP4 = "raid/datasets/audioset/valor_videos/video_0.000_1.000.mp4"


def _write_file_member(
    tar: tarfile.TarFile,
    name: str,
    data: bytes = b"mp4",
) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(data)
    tar.addfile(info, io.BytesIO(data))


def _write_typed_member(
    tar: tarfile.TarFile,
    name: str,
    typeflag: bytes,
    *,
    linkname: str = "",
) -> None:
    info = tarfile.TarInfo(name)
    info.type = typeflag
    info.linkname = linkname
    tar.addfile(info)


def _make_tar(tmp_path: Path, build) -> Path:
    tar_path = tmp_path / "valor.tar"
    with tarfile.open(tar_path, "w") as tar:
        build(tar)
    return tar_path


def test_valor32k_guarded_tar_extracts_canonical_mp4_to_top_level(
    tmp_path: Path,
) -> None:
    tar_path = _make_tar(
        tmp_path,
        lambda tar: _write_file_member(tar, CANONICAL_MP4, b"video-bytes"),
    )
    videos_dir = tmp_path / "videos"

    _extract_valor32k_tar(tar_path, videos_dir, strip_components=4)

    extracted = list(videos_dir.glob("*.mp4"))
    assert extracted == [videos_dir / "video_0.000_1.000.mp4"]
    assert extracted[0].read_bytes() == b"video-bytes"
    assert list(videos_dir.rglob("*.mp4")) == extracted


@pytest.mark.parametrize(
    ("member_name", "message"),
    [
        ("/raid/datasets/audioset/valor_videos/absolute.mp4", "absolute paths"),
        (
            "raid/datasets/audioset/valor_videos/../escape.mp4",
            "path components",
        ),
        ("raid/datasets/audioset/valor_videos", "removes the full path"),
    ],
)
def test_valor32k_guarded_tar_rejects_unsafe_member_paths(
    tmp_path: Path,
    member_name: str,
    message: str,
) -> None:
    tar_path = _make_tar(
        tmp_path,
        lambda tar: _write_file_member(tar, member_name),
    )

    with pytest.raises(ValueError, match=message):
        _extract_valor32k_tar(tar_path, tmp_path / "videos", strip_components=4)

    assert not list((tmp_path / "videos").rglob("*.mp4"))


@pytest.mark.parametrize(
    ("typeflag", "message"),
    [
        (tarfile.SYMTYPE, "symlinks and hardlinks"),
        (tarfile.LNKTYPE, "symlinks and hardlinks"),
        (tarfile.FIFOTYPE, "only regular files and directories"),
    ],
)
def test_valor32k_guarded_tar_rejects_link_and_special_entries(
    tmp_path: Path,
    typeflag: bytes,
    message: str,
) -> None:
    tar_path = _make_tar(
        tmp_path,
        lambda tar: _write_typed_member(
            tar,
            CANONICAL_MP4,
            typeflag,
            linkname="/tmp/escape.mp4",
        ),
    )

    with pytest.raises(ValueError, match=message):
        _extract_valor32k_tar(tar_path, tmp_path / "videos", strip_components=4)


def test_valor32k_guarded_tar_rejects_targets_escaping_videos_dir(
    tmp_path: Path,
) -> None:
    tar_path = _make_tar(
        tmp_path,
        lambda tar: _write_file_member(
            tar,
            "raid/datasets/audioset/valor_videos/link_out/escape.mp4",
        ),
    )
    videos_dir = tmp_path / "videos"
    videos_dir.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (videos_dir / "link_out").symlink_to(outside, target_is_directory=True)

    with pytest.raises(ValueError, match="escapes"):
        _extract_valor32k_tar(tar_path, videos_dir, strip_components=4)

    assert not (outside / "escape.mp4").exists()


def test_valor32k_product_code_no_longer_shells_out_to_tar_xf() -> None:
    source = (
        Path("src/nemotron/recipes/omni3/stage0_sft/data_prep.py")
        .read_text(encoding="utf-8")
    )

    assert "subprocess.check_call" not in source
    assert '"tar", "xf"' not in source
