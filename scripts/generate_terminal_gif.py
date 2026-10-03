#!/usr/bin/env python3
"""Generate an original macOS-style terminal GIF for the gogolumo profile README."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1000
HEIGHT = 320
FPS = 20
BG = (13, 17, 23)  # #0d1117
PANEL = (22, 27, 34)
BORDER = (48, 54, 61)
TITLEBAR = (28, 33, 40)
TEXT = (201, 209, 217)
DIM = (110, 118, 129)
ACCENT = (139, 148, 255)  # soft indigo
ACCENT_2 = (121, 192, 255)  # soft blue
PROMPT = (163, 113, 247)  # violet
GREEN = (63, 185, 80)
YELLOW = (210, 153, 34)
RED = (248, 81, 73)
CURSOR = (139, 148, 255)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "gogolumo.gif"
FONT_PATH = "/System/Library/Fonts/SFNSMono.ttf"

Segment = tuple[str, tuple[int, int, int]]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


def rounded_rect(draw: ImageDraw.ImageDraw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_window(base: Image.Image) -> ImageDraw.ImageDraw:
    draw = ImageDraw.Draw(base)
    margin = 18
    rounded_rect(
        draw,
        (margin, margin, WIDTH - margin, HEIGHT - margin),
        14,
        PANEL,
        outline=BORDER,
        width=1,
    )
    draw.rounded_rectangle(
        (margin, margin, WIDTH - margin, margin + 36),
        radius=14,
        fill=TITLEBAR,
    )
    draw.rectangle((margin, margin + 18, WIDTH - margin, margin + 36), fill=TITLEBAR)

    cy = margin + 18
    for i, color in enumerate((RED, YELLOW, GREEN)):
        cx = margin + 22 + i * 18
        draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=color)

    title = "gogolumo — zsh"
    tf = font(13)
    tw = draw.textlength(title, font=tf)
    draw.text(((WIDTH - tw) / 2, margin + 11), title, fill=DIM, font=tf)
    return draw


def measure(text: str, size: int = 16) -> float:
    return ImageFont.truetype(FONT_PATH, size).getlength(text)


class TerminalScene:
    def __init__(self):
        self.lines: list[list[Segment]] = []
        self.partial: list[Segment] = []
        self.show_cursor = True
        self.cursor_on = True

    def _draw_segments(self, draw, x0, y, segments, f):
        x = x0
        for text, color in segments:
            draw.text((x, y), text, fill=color, font=f)
            x += measure(text)
        return x

    def snapshot(self) -> Image.Image:
        img = Image.new("RGB", (WIDTH, HEIGHT), BG)
        draw = draw_window(img)
        f = font(16)
        x0 = 42
        y = 68
        line_h = 26

        visible = self.lines[-8:]
        for segments in visible:
            self._draw_segments(draw, x0, y, segments, f)
            y += line_h

        if self.partial is not None:
            end_x = self._draw_segments(draw, x0, y, self.partial, f)
            if self.show_cursor and self.cursor_on:
                draw.rectangle((end_x + 1, y + 2, end_x + 9, y + 18), fill=CURSOR)
        return img


def type_text(scene: TerminalScene, frames: list, text: str, color=TEXT, cps=22):
    delay = max(1, round(FPS / cps))
    for ch in text:
        if scene.partial and scene.partial[-1][1] == color:
            prev, _ = scene.partial[-1]
            scene.partial[-1] = (prev + ch, color)
        else:
            scene.partial.append((ch, color))
        for _ in range(delay if ch != " " else max(1, delay - 1)):
            frames.append(scene.snapshot())
    for _ in range(2):
        frames.append(scene.snapshot())


def pause(scene: TerminalScene, frames: list, seconds: float):
    n = max(1, int(seconds * FPS))
    for i in range(n):
        if scene.show_cursor:
            scene.cursor_on = (i // max(1, int(FPS * 0.55))) % 2 == 0
        frames.append(scene.snapshot())


def commit_line(scene: TerminalScene):
    scene.lines.append(list(scene.partial))
    scene.partial = []


def blank_line(scene: TerminalScene):
    scene.lines.append([])


def soft_clear_content(scene: TerminalScene, frames: list):
    """Quick dim-out of text between beats, keeping the window chrome."""
    last = scene.snapshot()
    empty = TerminalScene()
    empty_frame = empty.snapshot()
    for i in range(8):
        t = (i + 1) / 8
        frames.append(Image.blend(last, empty_frame, t))
    scene.lines.clear()
    scene.partial = []
    scene.cursor_on = True
    for _ in range(4):
        frames.append(scene.snapshot())


def clear_screen_soft(scene: TerminalScene, frames: list):
    """Fade toward empty for a loopable reset without a hard cut."""
    last = scene.snapshot()
    for i in range(12):
        fade = Image.new("RGB", (WIDTH, HEIGHT), BG)
        alpha = 1 - (i + 1) / 12
        frames.append(Image.blend(fade, last, alpha))
    scene.lines.clear()
    scene.partial = []
    scene.show_cursor = True
    scene.cursor_on = True
    for _ in range(8):
        frames.append(scene.snapshot())


def build_frames() -> list[Image.Image]:
    scene = TerminalScene()
    frames: list[Image.Image] = []

    pause(scene, frames, 0.4)

    # $ whoami
    type_text(scene, frames, "$ ", PROMPT, cps=18)
    type_text(scene, frames, "whoami", TEXT, cps=18)
    pause(scene, frames, 0.22)
    commit_line(scene)

    type_text(scene, frames, "bohdan dron", ACCENT, cps=20)
    pause(scene, frames, 0.12)
    commit_line(scene)
    type_text(scene, frames, "gogolumo", ACCENT_2, cps=20)
    pause(scene, frames, 0.35)
    commit_line(scene)

    blank_line(scene)

    # $ ls projects/
    type_text(scene, frames, "$ ", PROMPT, cps=18)
    type_text(scene, frames, "ls projects/", TEXT, cps=18)
    pause(scene, frames, 0.18)
    commit_line(scene)

    for name in ("Wheel/", "PlaySparse/", "Punktiq/", "RBSmithy/"):
        type_text(scene, frames, name, ACCENT, cps=28)
        pause(scene, frames, 0.06)
        commit_line(scene)

    pause(scene, frames, 0.55)
    soft_clear_content(scene, frames)

    # $ ./current-focus
    type_text(scene, frames, "$ ", PROMPT, cps=18)
    type_text(scene, frames, "./current-focus", TEXT, cps=18)
    pause(scene, frames, 0.22)
    commit_line(scene)

    focus_lines = [
        ("Wheel", "native macOS navigation"),
        ("PlaySparse", "adaptive storage research"),
    ]
    col = 12  # monospace column width
    for left, right in focus_lines:
        padded = left.ljust(col)
        type_text(scene, frames, padded, ACCENT, cps=26)
        type_text(scene, frames, right, TEXT, cps=24)
        pause(scene, frames, 0.1)
        commit_line(scene)

    blank_line(scene)

    type_text(scene, frames, "> ", PROMPT, cps=16)
    type_text(
        scene,
        frames,
        "mostly building tools that should already exist",
        DIM,
        cps=18,
    )
    pause(scene, frames, 2.0)
    pause(scene, frames, 0.8)
    clear_screen_soft(scene, frames)
    return frames


def save_gif(frames: list[Image.Image], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for i, frame in enumerate(frames):
            frame.save(tmp_path / f"frame_{i:04d}.png")

        palette = tmp_path / "palette.png"
        raw_gif = tmp_path / "raw.gif"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-framerate",
                str(FPS),
                "-i",
                str(tmp_path / "frame_%04d.png"),
                "-vf",
                "palettegen=max_colors=128:stats_mode=diff",
                str(palette),
            ],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-framerate",
                str(FPS),
                "-i",
                str(tmp_path / "frame_%04d.png"),
                "-i",
                str(palette),
                "-lavfi",
                "paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle",
                "-loop",
                "0",
                str(raw_gif),
            ],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(raw_gif),
                "-filter_complex",
                "[0:v] fps=16,scale=1000:-1:flags=lanczos,split [a][b];"
                "[a] palettegen=max_colors=96:stats_mode=diff [p];"
                "[b][p] paletteuse=dither=bayer:bayer_scale=4",
                str(path),
            ],
            check=True,
            capture_output=True,
        )

    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"Wrote {path} ({size_mb:.2f} MB, {len(frames)} source frames)")


def main():
    frames = build_frames()
    save_gif(frames, OUT)


if __name__ == "__main__":
    main()
