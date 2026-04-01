# Fruit Ninja Using OpenCV

Play Fruit Ninja with hand tracking using Python, OpenCV, MediaPipe, and Pygame.

## What This Project Includes

- Real-time hand tracking with smoothing for stable blade movement.
- Pinch-hold "knife stop" gesture to temporarily freeze slicing.
- Two game modes:
  - Classic: 3 lives.
  - Survival: 1 life.
- Mouse input and hand input support.
- Fruit slicing effects, bombs, score/life HUD, and sound effects.

## Requirements

- Windows/macOS/Linux
- Python 3.11 recommended
- Webcam (for hand mode)

## Setup (Recommended: Conda)

An environment file is included so others can recreate the same setup.

1. Create the environment:

   ```bash
   conda env create -f environment.yml
   ```

2. Activate it:

   ```bash
   conda activate fruit-ninja-opencv
   ```

3. Run the game:

   ```bash
   python main.py
   ```

## Setup (Pip Alternative)

If you do not want Conda:

```bash
pip install -r requirements.txt
python main.py
```

## Controls

- Menu navigation: Mouse click.
- In-game pause menu: Press ESC.
- Mouse mode: Hold left mouse button and swipe.
- Hand mode:
  - Slice by moving your index finger quickly.
  - Pinch and hold (thumb + index close) to activate knife stop.

## Git: Push This Clone To Your Own Repo

If this code started from someone else's repository, point this local clone to your own GitHub repo.

1. Create a new empty repo on GitHub (do not add README/license there).
2. In this project folder, run:

   ```bash
   git remote rename origin upstream
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```

3. Verify remotes:

   ```bash
   git remote -v
   ```

If you get a 403 permission denied error on push, your origin still points to a repo you cannot write to.

## Troubleshooting

- MediaPipe error about missing mp.solutions:
  - Use mediapipe==0.10.14 (already pinned in environment.yml).
- Webcam not opening:
  - Close other apps using the camera.
  - Check OS camera permissions.
- Low tracking quality:
  - Improve room lighting.
  - Keep your hand inside the camera frame.

## Tech Stack

- [MediaPipe](https://developers.google.com/mediapipe)
- [OpenCV](https://opencv.org/)
- [Pygame](https://www.pygame.org/)
