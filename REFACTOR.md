# Refactor TODO List

A running list of code improvements to make before showcasing this project.

---

## `main.py` — Input Handling

### [ ] Consolidate `_check_key_down` / `_check_key_up` into a single movement handler

**Current problem:**
`_check_key_down` and `_check_key_up` both contain identical condition blocks
(`if event.key == pygame.K_RIGHT / K_LEFT`) with only `True`/`False` differing.
This is ambiguous at a glance and looks like a copy-paste bug.

**Proposed change:**
Replace the two movement-related checks with a single method:

```python
def _handle_movement_key(self, event, is_pressed: bool) -> None:
    """Set ship movement state on key press or release"""
    if event.key == pygame.K_RIGHT:
        self.ship.moving_right = is_pressed
    elif event.key == pygame.K_LEFT:
        self.ship.moving_left = is_pressed
```

Call it from `_check_events` with explicit intent:

```python
elif event.type == pygame.KEYDOWN:
    self._check_key_down(event)           # handles space, q, etc.
    self._handle_movement_key(event, True)
elif event.type == pygame.KEYUP:
    self._handle_movement_key(event, False)
```

Delete `_check_key_up` entirely.

**Notes / watch-outs:**
- `_check_key_down` still needs to exist for non-movement keys (`K_SPACE`, `K_q`) — don't fold those into `_handle_movement_key`.
- Check tests for any direct calls to `_check_key_up` — if tests are simulating key release events by calling it directly, they'll need updating to simulate a `KEYUP` event through `_check_events` instead, or call `_handle_movement_key(event, False)` directly.
- Verify `ship.moving_right` and `ship.moving_left` still behave correctly in `ship.py`'s `update()` method after the rename — the flags themselves don't change, only how they're set.

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
