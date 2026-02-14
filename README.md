
# Magic Forest — Valentine Edition

![Gameplay demo](docs/demo.gif)

Magic Forest is a cozy pixel-platformer starring X as she explores an enchanted forest full of curious creatures and little secrets. Smooth camera scrolling, tintable sprites, particle effects, and a playful Valentine start screen make it delightful to play. Cross-platform builds available.

## Quick Description (300 chars)
Magic Forest is a cozy pixel-platformer starring Céline exploring an enchanted forest. Enjoy smooth camera scrolling, tintable sprites, particle effects, and a Valentine-themed start screen. Fast native builds for Windows/macOS/Linux; download on itch.io to play instantly.

## Features
- Charming pixel art with runtime tinting
- Smooth camera and level collisions
- Valentine-themed start screen with playful UI
- Enemies: bees, snails, boars
- Packaged builds via GitHub Actions for Windows/macOS/Linux

## How to Play
- Keyboard controls: Arrow keys to move, Up to jump, Space to attack.
- At the start screen choose `YES` to begin — `NO` will playfully dodge your cursor.

## Run locally (developer)
```bash
cd /path/to/repo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python MagicForest/04_LevelLoading/_04_LevelLoading.py
```

## Build & Distribute (quick)
- I provide a GitHub Actions workflow that builds native packages for Windows, macOS and Linux. Push to `main` and download artifacts from the Actions run.
- For itch.io uploads use the `MagicForest-<platform>.zip` artifacts and upload under your project page.

## Adding a demo GIF
Place an animated GIF at `docs/demo.gif` (recommended 640×360) and it will display here on GitHub. You can also embed hosted GIFs by replacing the image URL above.

## License
This project is provided as-is. Add your preferred license file if you want to publish.
# game
