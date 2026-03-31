# Refactor TODO List

A running list of code improvements to make before showcasing this project.

---

## UI Flow — Intro / Landing Screen

### [ ] Add a dedicated intro screen before gameplay starts

**What to investigate:**
Right now the game starts from the main gameplay screen with a Play button drawn on top when
`game_active` is `False`. For a portfolio version, it may be cleaner to separate this into a
proper intro/landing screen that shows the game title, some ASCII-style title art, and the
Play button before switching to the actual gameplay screen.

**Proposed change:**
Introduce a simple screen-state variable such as `current_screen` or `game_state`, then route
both drawing and event handling through that state. Rough shape:

```python
self.current_screen = "intro"
```

Then have `_update_screen()` delegate based on state:

```python
if self.current_screen == "intro":
    self._draw_intro_screen()
elif self.current_screen == "playing":
    self._draw_gameplay_screen()
```

Likewise in `_check_events()`, only check the Play button when on the intro screen. Clicking
Play would switch the state to `"playing"` and call the extracted game-start logic.

**Notes / watch-outs:**
- This is a good argument for extracting `_start_game()` out of `_check_play_button()` first,
  so the intro screen only needs to trigger one clean method instead of duplicating reset logic.
- `game_active` and `current_screen` are not quite the same job. Decide whether to keep both
  (`current_screen` for UI flow, `game_active` for simulation running) or collapse them into
  a single state system so the code doesn't end up with two clocks telling different lies.
- ASCII title art in pygame won't be true terminal ASCII art unless rendered line by line with
  a monospace font. That is fine, just worth knowing so expectations stay tethered to Earth.
- If you later add pause or game-over screens, a state-based layout scales much better than
  scattering `if not self.game_active` checks through the render path.

---

## Sound — `pygame.mixer`

### [ ] Look into adding sound effects via `pygame.mixer`

**What to investigate:**
`pygame.mixer` is the standard pygame module for audio. Worth a look to add basic sound effects
(firing bullets, alien explosions, ship hit, game over).

**Things to look up:**
- `pygame.mixer.init()` — needs to be called before loading sounds; check whether `pygame.init()`
  covers it automatically or if it needs explicit init
- `pygame.mixer.Sound` — loads and plays a sound file (WAV/OGG recommended; MP3 support is patchy)
- `sound.play()` — plays the sound; returns a `Channel` object if you need to track it
- `pygame.mixer.music` — separate API for background music (streaming, better for longer tracks)
- Channel management — `pygame.mixer.set_num_channels()` if you find sounds cutting each other off

**Gotchas to consider:**
- `pygame.mixer` can fail silently if no audio device is available (headless/CI environments) —
  worth wrapping init in a try/except so the game doesn't crash just because there's no sound card
- Sound files aren't included in the repo by default — decide early whether to bundle assets or
  keep them out of version control (add to `.gitignore` if not bundling)
- Latency: `pygame.mixer` has a buffer that can introduce a small delay; tune with
  `pygame.mixer.pre_init(frequency, size, channels, buffer)` before `pygame.init()` if shots feel laggy
- OGG is generally preferred over WAV for size; MP3 can have licensing/patent issues depending on platform

---

## High Score — Persisting to File

### [ ] Look into saving the high score between sessions

**What to investigate:**
Currently scores reset when the game closes. Worth adding basic persistence so the high score
survives between sessions — simplest approach is a plain text or JSON file.

**Things to look up:**
- `pathlib.Path` — cleaner than `os.path` for building the save file location
- `json.dump` / `json.load` — easy if you want to store more than just the score later
  (level reached, date, etc.); overkill for a single int but scales well
- Where to save: `~/.local/share/aliens/` is the conventional XDG location on Linux;
  alternatively just drop a `highscore.txt` next to the game for simplicity
- `GameStats` is the natural home for load/save logic since it already owns `score` and `high_score`

**Gotchas to consider:**
- File may not exist on first run — handle `FileNotFoundError` gracefully and default to `0`
- File could be corrupted or contain garbage — validate the loaded value before trusting it
  (at minimum check it's a non-negative integer)
- Don't save on every score update — only write when a new high score is actually set, to avoid
  hammering the disk every frame
- If the save path is outside the repo, make sure it's created if it doesn't exist
  (`Path.mkdir(parents=True, exist_ok=True)`)
- Consider whether the high score should reset if the player uninstalls — probably yes,
  so keeping it in `~/.local/share/` rather than bundled with the game is the right call

---

## `main.py` — Game Start

### [ ] Add `p` key as an alternative way to start the game

**Current behaviour:**
The game starts only via mouse click on the Play button, handled in `_check_play_button(mouse_position)`.
That method is tightly coupled to the mouse: it checks `collidepoint` on the button rect and bails
out if `game_active` is already `True`.

**Proposed change:**
Extract the actual start-game logic out of `_check_play_button` into a dedicated `_start_game` method,
then call it from both the mouse handler and the new keypress handler:

```python
def _start_game(self) -> None:
    """Reset state and activate the game"""
    self.stats.reset_stats()
    self.game_active = True
    pygame.mouse.set_visible(False)
    self.bullets.empty()
    self.aliens.empty()
    self._create_fleet()
    self.ship.center_ship()

def _check_play_button(self, mouse_position) -> None:
    """Start the game when the Play button is clicked"""
    button_clicked = self.play_button.rect.collidepoint(mouse_position)
    if button_clicked and not self.game_active:
        self._start_game()
```

Then in `_check_key_down`, add:

```python
elif event.key == pygame.K_p and not self.game_active:
    self._start_game()
```

**Notes / watch-outs:**
- The `and not self.game_active` guard on the keypress is critical — without it, hitting `p`
  mid-game will reset everything (bullets, aliens, ship position) while the game is already running.
  The mouse path already has this guard via `collidepoint`; the keyboard path needs it explicitly.
- `pygame.mouse.set_visible(False)` lives inside `_start_game` now — make sure it isn't also
  left behind in `_check_play_button` after the refactor, or you'll call it twice (harmless but messy).
- If you later add a pause feature, `p` is an obvious candidate for that too. Decide now whether
  `p` = "play/unpause" or keep them as separate keys to avoid a confusing double-duty binding.
- Update any tests that call `_check_play_button` directly to either call `_start_game` or go
  through the full mouse event path — they'll still work but the test intent may be clearer if
  pointed at `_start_game`.
