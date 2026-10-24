#!/usr/bin/env python3
"""Build the Subaru theme for both the local preview and the DSH client plugin."""
import base64
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src"
ASSETS = ROOT / "assets"
PREVIEW = ROOT / "preview"
PLUGIN = ROOT / "dsh-theme-subaru"


def data_url(path: pathlib.Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def main() -> int:
    css = (SRC / "theme.css").read_text(encoding="utf-8")
    js = (SRC / "theme.js").read_text(encoding="utf-8")

    wall = ASSETS / "wall.jpg"
    if not wall.exists():
        wall = ASSETS / "wall.placeholder.jpg"
        print("note: assets/wall.jpg not found, using the original placeholder wallpaper")
    avatar = ASSETS / "avatar.jpg"
    if not avatar.exists():
        avatar = ASSETS / "avatar.placeholder.jpg"
        print("note: assets/avatar.jpg not found, using the original placeholder avatar")
    font = ASSETS / "yuji-sub.woff"
    if not font.exists():
        raise SystemExit("missing assets/yuji-sub.woff (Yuji Syuku subset)")

    # ---- local preview -------------------------------------------------
    PREVIEW.mkdir(exist_ok=True)
    shutil.copy2(wall, PREVIEW / "wall.jpg")
    shutil.copy2(avatar, PREVIEW / "avatar.jpg")
    shutil.copy2(font, PREVIEW / "yuji-sub.woff")

    preview_css = (
        css.replace("__WALL__", "wall.jpg")
        .replace("__AVATAR__", "avatar.jpg")
        .replace("__FONT__", "yuji-sub.woff")
    )
    (PREVIEW / "theme.css").write_text(preview_css, encoding="utf-8")
    (PREVIEW / "boot.js").write_text(
        "var __SW_CSS__ = " + json.dumps(preview_css, ensure_ascii=False) + ";\n"
        + js
        + "\nswBoot(__SW_CSS__);\n",
        encoding="utf-8",
    )

    # ---- client plugin -------------------------------------------------
    (PLUGIN / "lib").mkdir(parents=True, exist_ok=True)
    plugin_css = (
        css.replace("__WALL__", data_url(wall, "image/jpeg"))
        .replace("__AVATAR__", data_url(avatar, "image/jpeg"))
        .replace("__FONT__", data_url(font, "font/woff"))
    )

    client = f"""window.__ModuleLoader__.load({{
\tid: "dsh-theme-subaru",
\tfactory: (require) => {{
\t\tvar module = {{ exports: {{}} }};
\t\tvar exports = module.exports;
\t\tObject.defineProperty(exports, Symbol.toStringTag, {{ value: "Module" }});
\t\tvar SW_CSS = {json.dumps(plugin_css, ensure_ascii=False)};
{indent(js, 2)}
\t\t/**
\t\t * Mount the Subaru Awa night-live-house skin on the Web client.
\t\t * @param ctx - Client root context.
\t\t */
\t\tfunction apply(ctx) {{
\t\t\tif (ctx && typeof ctx.effect === "function") ctx.effect(function () {{ return swBoot(SW_CSS); }});
\t\t\telse swBoot(SW_CSS);
\t\t}}
\t\texports.apply = apply;
\t\texports.inject = [];
\t\treturn module.exports;
\t}}
}});
"""
    (PLUGIN / "lib" / "client.js").write_text(client, encoding="utf-8")

    (PLUGIN / "lib" / "index.js").write_text(
        "// Host half: the browser bundle carries the whole skin.\n"
        "export function apply() {}\n",
        encoding="utf-8",
    )

    (PLUGIN / "package.json").write_text(
        json.dumps(
            {
                "name": "dsh-theme-subaru",
                "version": "1.0.0",
                "private": True,
                "description": "安和昴 / Girls Band Cry night-live-house skin for the DSH Web client",
                "type": "module",
                "main": "lib/index.js",
                "exports": {
                    ".": "./lib/index.js",
                    "./client": "./lib/client.js",
                    "./package.json": "./package.json",
                },
                "dsh": {"client": {"platform": "web"}},
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    shutil.copy2(font, PLUGIN / "lib" / "yuji-sub.woff")
    license_src = ASSETS / "OFL.txt"
    if license_src.exists():
        shutil.copy2(license_src, PLUGIN / "lib" / "OFL.txt")

    print("preview:", PREVIEW / "index.html")
    print("plugin :", PLUGIN / "lib" / "client.js", f"{(PLUGIN / 'lib' / 'client.js').stat().st_size:,} bytes")
    return 0


def indent(text: str, spaces: int) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line.strip() else line for line in text.splitlines())


if __name__ == "__main__":
    raise SystemExit(main())
