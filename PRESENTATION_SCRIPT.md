# Fruit Ninja Mini Game Presentation Script 

## Quick Use Guide

- Audience level: non-IT visitors and students.
- Speaking style: simple, warm, and clear.
- Pace: around 45 to 75 seconds per slide.
- Total time: about 8 to 10 minutes.

---

## Opening (Before Slide 1)

Hello everyone.
Today I will show you our Fruit Ninja mini game project.
The special part is this: we can play using hand movement from a webcam, not just a mouse.
I will explain the technical side in very simple words.

---

## Slide 1 - Your Finger Becomes the Blade

On this slide, the big idea is simple.
Your finger becomes the blade.

Think of the game like a smart mirror.
The camera watches your hand.
The program finds your index finger.
Then it draws the blade where your finger moves.

So what looks like magic is actually a clear process.
Input comes from the camera, then the game updates very fast, about 60 times every second.

Transition line:
Now let us see the journey from camera image to blade movement.

---

## Slide 2 - How the Camera Controls the Game

This slide is like a relay race.
Each step passes data to the next step.

Step 1: camera gives live frames.
Step 2: hand finder detects the fingertip.
Step 3: smoothing removes tiny shakes.
Step 4: screen mapping converts camera position to game position.
Step 5: blade follows that mapped point.

In simple words, this is why the blade feels stable instead of shaky.
We changed noisy camera motion into smooth game motion.

Transition line:
Now a key gameplay rule: speed.

---

## Slide 3 - Comic Story: How One Swipe Is Judged

This slide explains the decision logic like a comic story.

Frame 1: the game records your swipe path.
Frame 2: it checks two things.
First check: did your swipe pass near the fruit?
Second check: was your swipe fast enough?
Frame 3: final decision, cut or no cut.

So a swipe must be both near enough and fast enough.
That is why random hand motion does not always cut fruit.

Technical truth said simply:
The game uses a minimum speed rule for slicing.

Transition line:
Now let us look at how the game checks hit versus miss with geometry.

---

## Slide 4 - How the Game Decides Hit or Miss

Here we use a shape analogy.
Imagine drawing a thick marker line.
That is the blade path.
The fruit is treated like a circle.

If the thick line touches the circle, that is a hit.
If not, it is a miss.

So the game is not guessing.
It is doing a geometry distance check every frame.

Transition line:
Now let us zoom out and see the full game loop.

---

## Slide 5 - Repeating Game Loop

This is the core engine recipe.
The game repeats this cycle again and again.

1. Listen for input events.
2. Read hand or mouse position.
3. Move fruits and objects.
4. Check collisions.
5. Draw scene.
6. Play sounds and show frame.

This loop runs about 60 times per second.
That is why controls feel responsive.
If this loop slows down, the game feels laggy.

Transition line:
Now let us compare the two game modes.

---

## Slide 6 - Classic vs Survival Modes

We have two challenge styles.

Classic mode is practice friendly.
You start with 3 lives.
Bomb hit or missed fruit costs 1 life.

Survival mode is high pressure.
You start with 1 life.
One big mistake ends the run.

Same game engine, same slicing skill, different difficulty feel.

Transition line:
Next, I will show the project structure as a team.

---

## Slide 7 - Each Python File Has One Job

We designed the code like a school event team.
Each file has one clear role.

main.py is the captain and controls the loop.
input_manager.py translates hand or mouse into game input.
sensors.py handles webcam and tracking.
physics.py checks hit logic.
game_engine.py handles score and lives.
game_objects.py handles fruit, blade, bomb, and effects.
ui_manager.py handles menus.
audio_manager.py handles music and sound effects.

This structure makes the project easier to build, explain, and debug.

Transition line:
Finally, let us close with a quick myth check.

---

## Slide 8 - Recap and Myth Check

Myth one: the game uses one photo.
Truth: it uses live video frames.

Myth two: any movement can slice.
Truth: movement must pass speed and position checks.

Myth three: hit detection is random.
Truth: it uses geometry rules.

Myth four: everything is in one file.
Truth: the project is modular, like a team.

Final closing line:
Our project combines computer vision, game design, and clean Python structure in a way that beginners can understand and enjoy.
Thank you.

---

## Optional Q and A Prompts

If someone asks, How does the hand become stable?
You can answer: We smooth noisy camera motion before using it in the game.

If someone asks, Why do some swipes fail?
You can answer: The swipe was either too slow or did not pass close enough to fruit.

If someone asks, Why two modes?
You can answer: Classic helps beginners practice, Survival gives a harder challenge.
