"""Records a real run of the console as the backup video: drives the live screen, records it, then lays the
cached Tamil audio on the video at the moments each line played. The browser is muted while recording.
Usage (server must be running on :8000): python scripts/record_backup.py"""
import io
import shutil
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "http://localhost:8000"
OUT_DIR = ROOT / "backup"
TMP = OUT_DIR / "_raw"
VIEW = {"width": 1280, "height": 800}


def beat(page, seconds):
    page.wait_for_timeout(int(seconds * 1000))


def pick(page, persona_label):
    page.select_option("#persona", label=persona_label)


def place_call(page):
    page.click("#run")
    page.wait_for_selector(".toast", timeout=90000)


def play_whole_call(page, log, t0, limit=120):
    page.locator("#h-call").scroll_into_view_if_needed()
    page.evaluate("window.scrollBy(0, -90)")
    page.click("#play-call")
    start = time.time()
    while time.time() - start < limit:
        if "Play the call" in page.inner_text("#play-call"):
            break
        beat(page, 0.5)
    log.extend({"at": e["t"] / 1000 - t0, "id": e["id"]} for e in page.evaluate("window.__audioLog"))


def main():
    shutil.rmtree(TMP, ignore_errors=True)
    OUT_DIR.mkdir(exist_ok=True)
    import httpx
    httpx.post(f"{BASE}/api/demo/reset", timeout=30)
    log = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True, args=["--mute-audio", "--autoplay-policy=no-user-gesture-required"])
        t0 = time.time()
        ctx = browser.new_context(viewport=VIEW, record_video_dir=str(TMP), record_video_size=VIEW)
        page = ctx.new_page()
        page.goto(f"{BASE}/#live")
        page.wait_for_selector("#hero-headline")
        beat(page, 3.5)                                   # before: sales are low, nothing has happened yet

        # 1. golden path: Tamil call ends with a new schedule
        pick(page, "Merchant agrees (Tamil)")
        beat(page, 1.5)
        place_call(page)
        page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
        beat(page, 3.0)                                   # hero now says relief is in force, all four steps green
        play_whole_call(page, log, t0)
        beat(page, 1.0)
        page.locator("#h-repay").scroll_into_view_if_needed()
        beat(page, 3.5)                                   # before and after schedule, new end date

        # 2. a deliberate escalation: the merchant says the shop is closing
        page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
        page.click("#reset")
        beat(page, 1.5)
        pick(page, "Says the shop is closing")
        place_call(page)
        beat(page, 2.0)
        page.locator("#h-queue").scroll_into_view_if_needed()
        beat(page, 3.5)                                   # handover queue with the summary

        # 3. the audit log: verify, tamper, verify again
        page.click("#tab-audit")
        beat(page, 2.5)
        page.click("#verify")
        beat(page, 3.0)
        page.click("#tamper")
        beat(page, 1.5)
        page.click("#verify")
        beat(page, 3.5)

        # 4. test results
        page.click("#tab-results")
        beat(page, 5.0)
        page.mouse.wheel(0, 650)
        beat(page, 3.5)

        ctx.close()                                       # writes the video
        browser.close()

    raw = next(TMP.glob("*.webm"))
    out = OUT_DIR / "Keel_demo_backup.mp4"
    audio_dir = ROOT / "data" / "audio"
    inputs, filters, labels = ["-i", str(raw)], [], []
    for i, e in enumerate(log, start=1):
        inputs += ["-i", str(audio_dir / f"{e['id']}.wav")]
        ms = max(0, int(e["at"] * 1000))
        filters.append(f"[{i}:a]adelay={ms}|{ms}[a{i}]")
        labels.append(f"[a{i}]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs]
    if labels:
        cmd += ["-filter_complex", ";".join(filters) + f";{''.join(labels)}amix=inputs={len(labels)}:normalize=0[aout]",
                "-map", "0:v", "-map", "[aout]", "-c:a", "aac", "-b:a", "128k"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "24", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    shutil.rmtree(TMP, ignore_errors=True)
    print(f"audio lines laid on the video: {len(log)}")
    for e in log:
        print(f"  {e['at']:6.1f}s  {e['id']}")
    print("wrote", out, f"{out.stat().st_size / 1e6:.1f} MB")


main()
