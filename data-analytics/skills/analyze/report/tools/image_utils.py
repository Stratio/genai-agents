"""Utilities for embedding images as base64 in HTML content."""

import base64
import mimetypes
import re
from pathlib import Path


def image_to_base64(image_path: str | Path, base_dir: Path | None = None) -> str | None:
    """Convert a local image file to a base64 data URI.

    Args:
        image_path: Path to the image file (absolute or relative).
        base_dir: Base directory to resolve relative paths against.

    Returns:
        A data URI string (e.g. "data:image/png;base64,...") or None if file not found.
    """
    path = Path(image_path)
    if not path.is_absolute() and base_dir:
        path = base_dir / path

    if not path.is_file():
        return None

    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type is None:
        mime_type = "application/octet-stream"

    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime_type};base64,{b64}"


def embed_images_in_html(html: str, base_dir: Path | None = None) -> str:
    """Replace local image src references in HTML with base64 data URIs.

    Handles both <img src="..."> and url(...) in inline styles.
    Skips URLs that are already data URIs or remote (http/https).

    Args:
        html: HTML string with image references.
        base_dir: Base directory to resolve relative image paths against.

    Returns:
        HTML string with local images embedded as base64.
    """

    def _replace_img_src(match: re.Match) -> str:
        prefix = match.group(1)
        src = match.group(2)
        suffix = match.group(3)

        if src.startswith(("data:", "http://", "https://")):
            return match.group(0)

        data_uri = image_to_base64(src, base_dir)
        if data_uri:
            return f'{prefix}{data_uri}{suffix}'
        return match.group(0)

    # Replace <img src="..."> and <img src='...'>
    html = re.sub(
        r'(<img\s[^>]*?src=["\'])([^"\']+)(["\'])',
        _replace_img_src,
        html,
        flags=re.IGNORECASE,
    )

    def _replace_css_url(match: re.Match) -> str:
        prefix = match.group(1)
        url = match.group(2)
        suffix = match.group(3)

        if url.startswith(("data:", "http://", "https://")):
            return match.group(0)

        data_uri = image_to_base64(url, base_dir)
        if data_uri:
            return f'{prefix}{data_uri}{suffix}'
        return match.group(0)

    # Replace url(...) in inline styles
    html = re.sub(
        r'(url\(["\']?)([^"\')\s]+)(["\']?\))',
        _replace_css_url,
        html,
    )

    return html
