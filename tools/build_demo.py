"""Assemble already captured browser frames into a short offline walkthrough."""

from pathlib import Path

from PIL import Image

root = Path(__file__).resolve().parents[1] / "reports/demo"
names = ["answer", "source", "refusal", "error"]
frames = [Image.open(root / f"{name}.png").convert("RGB") for name in names]
frames[0].save(
    root / "walkthrough.gif",
    save_all=True,
    append_images=frames[1:],
    duration=[4000, 6000, 4000, 4000],
    loop=0,
)
for frame in frames:
    frame.close()
print("Saved 18-second captured-frame walkthrough; not a continuous screen recording.")
