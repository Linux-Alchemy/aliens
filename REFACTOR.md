# Refactor Guide — Alien Invasion Polish

Three improvements that go beyond the book. Each one introduces a concept you haven't
used yet. The goal is to *understand what you're doing* while you do it — not to spend
three days on it. Follow the TODOs in order; the pseudo-code tells you the shape, the
real snippets tell you the syntax.

---

## 1. Intro / Landing Screen

### What you're building
A proper title screen before gameplay starts. Right now the Play button floats on top
of the game world — fine for a tutorial, a bit rough for a portfolio. A dedicated intro
screen makes the game feel finished.

### New concept: game state
This is your first mini state machine. Instead of a single `game_active` boolean,
you'll track *where in the game you are* with a string:

```python
# In AlienInvasion.__init__():
self.game_state = "intro"   # other values: "playing", "game_over"
```

Then `_update_screen()` and `_check_events()` route based on that value instead of
checking `game_active` everywhere.

> **Why bother?** One boolean can only mean "on or off". A state string can mean
> intro, playing, paused, game_over — and your drawing/event logic stays clean because
> each state only does its own job. This is how almost every game engine works at scale.

---

### TODOs

**Step 1 — add the state variable**
- [ ] In `__init__`, replace `self.game_active = False` with `self.game_state = "intro"`
- [ ] Anywhere in the code that reads `self.game_active`, update it to check
      `self.game_state == "playing"` instead

**Step 2 — write `_draw_intro_screen()`**

This method draws the title and the Play button onto a blank screen. You already know
how to render text (`Scoreboard` does it) and draw the button. You're just combining
those ideas here:

```python
def _draw_intro_screen(self) -> None:
    # fill the screen with the background colour
    # create a font — pygame.font.SysFont(None, size) works fine
    # render a title string as an image surface
    # position that surface near the top-centre of the screen
    # blit it to self.screen
    # draw the play button (you already have self.play_button.draw_button())
```

The only new thing here is positioning. `pygame.font.SysFont(None, 72)` gives you a
big font. To centre text horizontally, get the rect from the rendered surface and set
`rect.centerx = self.screen_rect.centerx`. Vertical position: set `rect.top` to
something like `self.screen_rect.height // 4`.

**Step 3 — update `_update_screen()`**

Route drawing through the state:

```python
def _update_screen(self) -> None:
    self.screen.fill(self.settings.bg_color)

    if self.game_state == "intro":
        self._draw_intro_screen()
    elif self.game_state == "playing":
        # everything that was already here: bullets, ship, aliens, scoreboard
        ...

    pygame.display.flip()
```

**Step 4 — update `_check_events()`**

The Play button click currently calls `_check_play_button()`. That method sets
`game_active = True` and resets everything. Rename/refactor it to `_start_game()` and
have it set `self.game_state = "playing"` instead:

```python
def _start_game(self) -> None:
    self.game_state = "playing"
    self.settings.initialize_dynamic_settings()
    # reset stats, clear bullets, clear aliens, create fleet, center ship
    # hide the mouse cursor
    ...
```

Then in `_check_events()`:

```python
# inside the MOUSEBUTTONDOWN branch:
if self.game_state == "intro":
    mouse_pos = pygame.mouse.get_pos()
    if self.play_button.rect.collidepoint(mouse_pos):
        self._start_game()
```

### Watch-outs
- Don't leave any stray `self.game_active` references — do a quick search after
  you're done (`grep -n "game_active" src/aliens/main.py`)
- The scoreboard's `show_score()` should only be called during `"playing"` state,
  otherwise it'll try to draw a score on the intro screen

---

## 2. Sound Effects — `pygame.mixer`

### What you're building
Three sound effects: bullet fired, alien destroyed, ship hit. That's enough to make
the game feel alive without going overboard.

### New concept: `pygame.mixer`
Pygame has a dedicated audio module. You load a sound file once (at init), then call
`.play()` on it whenever you need it. The module handles the rest.

```python
# Load once — cheap after the first time
shoot_sound = pygame.mixer.Sound("assets/shoot.wav")

# Play on demand — very cheap
shoot_sound.play()
```

### Getting sound files
You need `.wav` or `.ogg` files (avoid MP3 — patchy support). Free options:
- **freesound.org** — search "laser", "explosion", "boom"; filter by licence CC0
- **kenney.nl/assets** — has entire free game audio packs, no attribution needed

Download 3 files and drop them in your `assets/` folder.

---

### TODOs

**Step 1 — init the mixer**

`pygame.init()` usually covers this, but it's good practice to be explicit. Add this
*before* `pygame.init()` in `AlienInvasion.__init__()`:

```python
pygame.mixer.pre_init(44100, -16, 2, 512)
```

The last argument (512) is the buffer size — smaller = less latency on sound effects.

**Step 2 — load sounds in `__init__`**

After `pygame.init()`, load your files. Wrap it so the game doesn't crash if audio
isn't available (e.g. running tests headlessly):

```python
try:
    self.shoot_sound = pygame.mixer.Sound("assets/shoot.wav")
    self.explosion_sound = pygame.mixer.Sound("assets/explosion.wav")
    self.ship_hit_sound = pygame.mixer.Sound("assets/ship_hit.wav")
    self.sounds_enabled = True
except pygame.error:
    self.sounds_enabled = False
```

**Step 3 — play sounds at the right moments**

Find each relevant method and add a play call:

```python
# In _fire_bullet():
if self.sounds_enabled:
    self.shoot_sound.play()

# In _check_bullet_alien_collisions(), inside the `if collisions:` block:
# play explosion sound

# In _ship_hit():
# play ship hit sound
```

**Step 4 — add assets to `.gitignore` (optional)**

If you don't want to bundle the audio files in the repo, add this to `.gitignore`:

```
assets/*.wav
assets/*.ogg
```

If you *do* want them in the repo (simpler for a portfolio), skip this step and just
commit them. Either is fine.

### Watch-outs
- `pygame.mixer.Sound()` takes a path string or `Path` object — either works
- Volume is 0.0–1.0; `sound.set_volume(0.5)` if anything is too loud
- If you hear sounds cutting each other off when many aliens die at once,
  look up `pygame.mixer.set_num_channels()` — default is 8, usually enough

---

## 3. Persist the High Score

### What you're building
Save the high score to a file when it's beaten, load it back when the game starts.
Currently every session starts from zero — this fixes that.

### New concepts: `pathlib` and `json`

`pathlib.Path` is the modern way to work with file paths in Python. It's cleaner than
string concatenation and works the same on every OS:

```python
from pathlib import Path

save_path = Path("~/.local/share/aliens/highscore.json").expanduser()
```

`json` turns Python values into text and back — simple:

```python
import json

# Writing
with open(save_path, 'w') as f:
    json.dump({"high_score": 1500}, f)

# Reading
with open(save_path, 'r') as f:
    data = json.load(f)
    score = data["high_score"]
```

---

### TODOs

**Step 1 — add load/save to `GameStats`**

`GameStats` already owns `high_score`, so this is the natural home. Add two methods:

```python
def load_high_score(self) -> None:
    # build the path using Path("~/.local/share/aliens/highscore.json").expanduser()
    # if the file exists, open it and read the high_score value
    # if the file doesn't exist (FileNotFoundError), set self.high_score = 0
    # if the value loaded isn't a valid non-negative int, default to 0

def save_high_score(self) -> None:
    # build the same path
    # make sure the parent directory exists: path.parent.mkdir(parents=True, exist_ok=True)
    # write {"high_score": self.high_score} as JSON
```

The only genuinely new syntax here is `Path` and `json`. The logic is just an
if/else wrapped in a try/except — nothing you haven't seen.

**Step 2 — call `load_high_score()` at startup**

In `GameStats.__init__()`, after `self.high_score = 0`, replace that line with a call
to `self.load_high_score()`. This means the first thing the game does is check whether
there's a saved score:

```python
def __init__(self, ai_game) -> None:
    self.settings = ai_game.settings
    self.reset_stats()
    self.load_high_score()   # replaces self.high_score = 0
```

**Step 3 — call `save_high_score()` when a new high score is set**

This already happens in one place: `Scoreboard.check_high_score()`. Add the save call
there:

```python
def check_high_score(self) -> None:
    if self.stats.score > self.stats.high_score:
        self.stats.high_score = self.stats.score
        self.prep_high_score()
        self.stats.save_high_score()    # add this line
```

That's it. Don't save anywhere else — you don't need to.

### Watch-outs
- `Path.expanduser()` is what turns `~` into `/home/yourname/` — don't forget it
- `mkdir(parents=True, exist_ok=True)` won't crash if the directory already exists;
  that's the whole point of `exist_ok=True`
- After loading, validate the value: `if isinstance(score, int) and score >= 0` before
  assigning it. Someone (future you) might edit the file manually and break it

---

## Order of attack

Do them in this order — each one is independent, but this sequence keeps the changes
small and testable:

1. **High score persistence** — pure Python, no pygame, easiest win
2. **Sound effects** — isolated additions, nothing existing changes
3. **Intro screen** — most invasive (touches `_update_screen` and `_check_events`),
   do it last so you're not debugging state changes on top of new audio code
