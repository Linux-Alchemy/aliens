# Phase 1 Test Outline: Alien Invasion

## Testing Philosophy

We're writing tests for a game built on pygame. The goal here isn't 100% coverage
or bulletproof edge-case handling — it's to build the **habit and understanding**
of why we test, what's worth testing, and how to structure tests that actually
tell you something useful when they pass or fail.

Each test in this outline targets a **specific behaviour** of the code. We're not
testing pygame itself (that's someone else's problem). We're testing that *our*
code does what we told it to do.

**Framework:** pytest
**Total tests:** 13

---

## Test Infrastructure

Before writing any individual tests, we need shared setup that multiple test
files will reuse. This lives in `conftest.py` — pytest's built-in mechanism for
shared fixtures.

### File: `tests/conftest.py`

Pygame requires `pygame.init()` before you can create surfaces, rects, or do
basically anything useful. Several of our classes also expect an `ai_game` object
passed into their `__init__`. Rather than repeating that setup in every test file,
we build **fixtures** — reusable setup functions that pytest injects into tests
automatically.

```
Fixture: pygame_init (scope: session)
    """
    Initialize and teardown pygame for the entire test session.

    Scope is 'session' because pygame.init() is expensive and only
    needs to happen once — not before every single test.

    Yields:
        None — this fixture exists purely for its side effect.
    """
    TODO:
    - call pygame.init() to start the pygame subsystem
    - yield (this is where all the tests run)
    - call pygame.quit() to clean up after all tests finish

    WHY session scope?
    pygame.init() boots up audio, video, and input subsystems. Doing that
    once and sharing it across all tests is faster and avoids weird state
    issues from repeated init/quit cycles.
```

```
Fixture: game (scope: function, depends on: pygame_init)
    """
    Create a fresh AlienInvasion instance for each test.

    Returns:
        AlienInvasion: A fully initialized game instance with screen,
                       settings, ship, and empty bullet group.
    """
    TODO:
    - import AlienInvasion from src.aliens.alien_invasion
    - create a new AlienInvasion() instance
    - return it

    WHY function scope?
    Each test gets its own clean game instance. Tests that fire bullets
    or move the ship won't leak state into other tests. This is the
    default scope, but we're being explicit about it because understanding
    fixture scope matters.
```

---

## Test File 1: `tests/test_settings.py`

**Module under test:** `src/aliens/settings.py`
**Why start here:** Settings is a pure data class with no dependencies — no
pygame, no other modules, no side effects. It's the simplest thing to test
and the gentlest introduction to writing assertions.

### What Settings Does

`Settings.__init__()` assigns a set of configuration values as instance
attributes. These values control screen dimensions, colours, ship speed,
and bullet behaviour. Every other class in the game reads from a Settings
instance. If these values are wrong, everything downstream breaks.

---

### Test 1: `test_default_screen_settings`

```python
def test_default_screen_settings(settings: Settings) -> None:
    """
    Verify that screen-related settings initialize to their expected defaults.

    Tests that screen_width, screen_height, and bg_color are set to the
    values the game relies on for display setup.

    Args:
        settings: A Settings instance provided by the settings fixture.
    """
```

**Why this test exists:**

Settings is the single source of truth for the game's configuration. The
`AlienInvasion.__init__` method passes `self.settings.screen_width` and
`self.settings.screen_height` directly to `pygame.display.set_mode()`. If
someone accidentally changes a default — say, swaps width and height, or
changes the background colour tuple from 3 values to 2 — the game breaks
in ways that might not be immediately obvious.

This test acts as a **contract**: "these are the values we agreed on, and
they haven't drifted." It's the simplest kind of test — direct value
comparison — but it catches accidental edits to a file that everything
else depends on.

```
TODO (detailed pseudocode):

1. ARRANGE
   - create a new Settings() instance
     (no arguments needed — Settings takes no params)

2. ASSERT screen dimensions
   - assert settings.screen_width equals 1200
   - assert settings.screen_height equals 800
   WHY: these are the exact values passed to pygame.display.set_mode()
        in AlienInvasion.__init__. If they change, the game window changes.

3. ASSERT background colour
   - assert settings.bg_color equals the tuple (0, 0, 0)
   WHY: bg_color is an RGB tuple. pygame.Surface.fill() expects exactly
        3 integers. If this becomes (0, 0) or "black", fill() will blow up.
```

**What a failure here tells you:**
Someone changed a default in Settings. Go look at what changed and whether
the rest of the code was updated to match.

---

### Test 2: `test_default_bullet_settings`

```python
def test_default_bullet_settings(settings: Settings) -> None:
    """
    Verify that bullet-related settings initialize to their expected defaults.

    Tests speed, dimensions, colour, and max count — the full set of values
    that Bullet and AlienInvasion depend on for bullet behaviour.

    Args:
        settings: A Settings instance provided by the settings fixture.
    """
```

**Why this test exists:**

Bullet behaviour is governed entirely by these five settings. The Bullet
class reads `bullet_speed`, `bullet_width`, `bullet_height`, and
`bullet_color` during `__init__`. The AlienInvasion class reads
`bullet_max_count` in `_fire_bullet()` to cap how many bullets can exist
at once.

We test these separately from screen settings because they're a **different
responsibility**. If a bullet test fails, you know immediately it's a
bullet config problem, not a screen config problem. Grouping related
assertions together keeps your error messages meaningful.

```
TODO (detailed pseudocode):

1. ARRANGE
   - create a new Settings() instance

2. ASSERT bullet physics values
   - assert settings.bullet_speed equals 3
   - assert settings.bullet_width equals 3
   - assert settings.bullet_height equals 15
   WHY: Bullet.__init__ uses width and height to create the bullet's Rect
        via pygame.Rect(0, 0, width, height). Wrong dimensions mean the
        bullet is visually wrong or its collision rect is off.

3. ASSERT bullet appearance
   - assert settings.bullet_color equals the tuple (60, 60, 60)
   WHY: same reasoning as bg_color — it's an RGB tuple, and pygame.draw.rect()
        will fail if the format is wrong.

4. ASSERT bullet limit
   - assert settings.bullet_max_count equals 10
   WHY: _fire_bullet() uses this to decide whether to create a new bullet.
        If this value is accidentally set to 0, the player can never fire.
        If set to 9999, performance could suffer with thousands of sprites.
```

**Fixture for both Settings tests:**

```
Fixture: settings (local to test_settings.py)
    """
    Create a fresh Settings instance.

    Returns:
        Settings: A new Settings instance with all defaults.
    """
    TODO:
    - import Settings from src.aliens.settings
    - return Settings()

    WHY a fixture and not just Settings() in each test?
    Right now it's one line, so a fixture feels like overkill. But the
    habit matters. When Settings later takes arguments (difficulty level,
    custom configs), the fixture is where you change it once, not in
    every test function.
```

---

## Test File 2: `tests/test_ship.py`

**Module under test:** `src/aliens/ship.py`
**Why this is tested second:** Ship introduces the first real dependency —
it needs a pygame display surface and an `ai_game`-like object. This is
where you learn about **test fixtures** doing real work.

### What Ship Does

`Ship` loads a bitmap image, positions itself at the bottom-centre of the
screen, and moves left/right based on boolean flags. Its `update()` method
checks screen boundaries before applying movement.

---

### Test 1: `test_ship_starts_at_midbottom`

```python
def test_ship_starts_at_midbottom(game: AlienInvasion) -> None:
    """
    Verify the ship's starting position is centred at the bottom of the screen.

    The ship should spawn at screen_rect.midbottom so the player starts in a
    predictable, centred position every time.

    Args:
        game: A fully initialized AlienInvasion instance from the game fixture.
    """
```

**Why this test exists:**

The ship's starting position is set in `Ship.__init__` with
`self.rect.midbottom = self.screen_rect.midbottom`. If this line changes —
or if the screen dimensions change without updating the ship setup — the
player could spawn off-screen, in a corner, or clipping the edge.

This tests the **relationship** between two objects: the ship and the
screen. It's not enough to check that midbottom is "some value" — we need
to confirm it matches the screen's midbottom. That's the contract.

```
TODO (detailed pseudocode):

1. ARRANGE
   - use the game fixture (provides game.ship and game.screen)
   - get the screen's rect via game.screen.get_rect()
     this gives us the screen's dimensions as a Rect object

2. ASSERT starting position
   - assert game.ship.rect.midbottom equals screen_rect.midbottom
   WHY: midbottom is a tuple of (x, y). Comparing the full tuple checks
        both horizontal centering AND vertical positioning in one assertion.
        If the ship is centred but floating in the middle of the screen,
        this catches it.

3. ASSERT the float tracker matches the rect
   - assert game.ship.x equals float(game.ship.rect.x)
   WHY: Ship stores self.x as a float for smooth sub-pixel movement, then
        casts back to int for self.rect.x. At init, these must agree.
        If they don't, the ship will visually jump on the first frame.
```

**What a failure here tells you:**
Either the ship's init changed its starting position, or the screen
dimensions changed and the ship didn't adapt. Check both.

---

### Test 2: `test_ship_respects_screen_boundaries`

```python
def test_ship_respects_screen_boundaries(game: AlienInvasion) -> None:
    """
    Verify the ship cannot move beyond the left or right screen edges.

    Tests that update() enforces boundary checks so the ship stays visible
    regardless of how long a movement key is held.

    Args:
        game: A fully initialized AlienInvasion instance from the game fixture.
    """
```

**Why this test exists:**

Ship.update() has two boundary checks:
- `self.rect.right < self.screen_rect.right` (right edge)
- `self.rect.left > 0` (left edge)

Without these, holding a movement key would send the ship sailing off into
the void. This test verifies the **conditional logic** — the part of update()
that makes a decision. If you're going to test behaviour, test the behaviour
that has a branch in it.

```
TODO (detailed pseudocode):

1. ARRANGE — test right boundary
   - use the game fixture
   - manually set game.ship.x to a value at the right edge of the screen
     (screen_width minus ship_rect.width — so rect.right == screen edge)
   - update game.ship.rect.x to match (int of the new x)
   - set game.ship.moving_right to True

2. ACT — try to move past the right edge
   - call game.ship.update()

3. ASSERT — ship stayed put
   - assert game.ship.rect.right is less than or equal to screen_rect.right
   WHY: update() should refuse to increment self.x because the boundary
        condition (rect.right < screen_rect.right) is now False. The ship
        stays at the edge.

4. ARRANGE — test left boundary
   - set game.ship.moving_right to False (stop rightward movement)
   - set game.ship.x to 0.0 (ship is flush with left edge)
   - update game.ship.rect.x to 0
   - set game.ship.moving_left to True

5. ACT — try to move past the left edge
   - call game.ship.update()

6. ASSERT — ship stayed put
   - assert game.ship.rect.left is greater than or equal to 0
   WHY: same logic, opposite direction. The condition (rect.left > 0) is
        False when left == 0, so the ship shouldn't move further left.
```

**What a failure here tells you:**
A boundary check in update() is broken or was removed. The ship will
disappear off-screen if this isn't fixed.

---

## Test File 3: `tests/test_bullet.py`

**Module under test:** `src/aliens/bullet.py`
**Why this is tested third:** Bullet depends on both Settings and Ship
(it reads the ship's position for its spawn point). This builds on the
fixture chain you've already set up.

### What Bullet Does

`Bullet` is a pygame Sprite. It creates a small rectangle at the ship's
`midtop` position and moves upward each frame by `bullet_speed`. It also
has a `draw_bullet()` method for rendering.

---

### Test 1: `test_bullet_spawns_at_ship_position`

```python
def test_bullet_spawns_at_ship_position(game: AlienInvasion) -> None:
    """
    Verify a new bullet is created at the ship's midtop position.

    The bullet should appear right at the tip of the ship, not at the
    origin or some arbitrary location.

    Args:
        game: A fully initialized AlienInvasion instance from the game fixture.
    """
```

**Why this test exists:**

In `Bullet.__init__`, the rect is first created at (0, 0) with the
configured width and height, then repositioned:
`self.rect.midtop = ai_game.ship.rect.midtop`

This is a two-step process, and the second step is what makes bullets
actually appear at the ship. If someone removes or reorders that line —
or refactors the constructor — bullets would spawn at (0, 0), which is
the top-left corner of the screen. Visually confusing, logically wrong.

This test verifies the **relationship** between bullet and ship position
at the moment of creation.

```
TODO (detailed pseudocode):

1. ARRANGE
   - use the game fixture
   - note the ship's current midtop position:
       store game.ship.rect.midtop as expected_position

2. ACT
   - import Bullet from src.aliens.bullet
   - create a new Bullet instance, passing game as the ai_game argument
     (exactly how _fire_bullet() does it)

3. ASSERT spawn position
   - assert bullet.rect.midtop equals expected_position
   WHY: midtop is a tuple (x, y). Checking the full tuple confirms the
        bullet is both horizontally centred on the ship AND vertically
        at the ship's top edge. If only x or only y is correct, this
        catches the partial failure.

4. ASSERT float tracker matches
   - assert bullet.y equals float(bullet.rect.y)
   WHY: same pattern as Ship — Bullet stores self.y as a float for
        smooth movement. At creation, the float and the rect must agree.
        A mismatch means the bullet would jump on its first update().
```

**What a failure here tells you:**
Bullet isn't reading the ship's position correctly, or the rect
repositioning was lost. Check `Bullet.__init__`.

---

### Test 2: `test_bullet_moves_upward_on_update`

```python
def test_bullet_moves_upward_on_update(game: AlienInvasion) -> None:
    """
    Verify that calling update() moves the bullet upward by bullet_speed.

    Each frame, the bullet's y-coordinate should decrease (move toward
    the top of the screen) by exactly settings.bullet_speed pixels.

    Args:
        game: A fully initialized AlienInvasion instance from the game fixture.
    """
```

**Why this test exists:**

`Bullet.update()` does two things:
1. Decrements `self.y` by `self.settings.bullet_speed`
2. Sets `self.rect.y` to the new `self.y` value

This is the bullet's entire reason for existing — it moves upward. If the
speed is applied in the wrong direction (incrementing instead of
decrementing), or if `rect.y` isn't updated to match the float, bullets
either fall downward or appear to freeze while their internal state drifts.

Testing movement is testing **state change over time**. You record the
"before", perform the action, then check the "after" matches what you
predicted.

```
TODO (detailed pseudocode):

1. ARRANGE
   - use the game fixture
   - create a new Bullet instance, passing game as ai_game
   - record the bullet's starting y position:
       store bullet.rect.y as start_y
   - look up the expected speed:
       store game.settings.bullet_speed as speed

2. ACT
   - call bullet.update() once (simulating one frame)

3. ASSERT the bullet moved upward
   - assert bullet.rect.y equals (start_y - speed)
   WHY: in pygame, y=0 is the TOP of the screen. Moving "up" visually
        means DECREASING y. So after one update, the bullet should be
        exactly bullet_speed pixels higher (lower y value). This is a
        common source of confusion — make sure the subtraction is right.

4. ASSERT the float tracker is consistent
   - assert bullet.y equals float(bullet.rect.y)
   WHY: the float self.y drives the movement, and rect.y is the rendered
        position. After update(), they must still agree. If they diverge,
        the bullet's visual position won't match its logical position,
        which would cause collision detection bugs later.
```

**What a failure here tells you:**
Either the speed is being added instead of subtracted (bullet goes down),
the rect isn't being updated from the float, or the speed value changed.

---

## Test File 4: `tests/test_alien.py`

**Module under test:** `src/aliens/alien.py`
**Why this is tested here:** Alien depends on the game fixture (it needs a screen and
settings), so it slots in naturally after Bullet. It introduces testing **methods that
return values** (`edge_check()`) and **state changes driven by settings** (`update()`).

### What Alien Does

`Alien` is a pygame Sprite. It loads an image, positions itself offset from the
top-left corner by one alien's own dimensions (so the fleet doesn't spawn flush
against the edge), and exposes `edge_check()` to detect screen boundaries and
`update()` to move horizontally each frame using `alien_speed` and `fleet_direction`.

---

### Fixture for alien.py tests

```
Fixture: alien (local to test_alien.py, depends on: game)
    """
    Create a fresh Alien instance using the live game object.

    Args:
        game: A fully initialized AlienInvasion instance from the game fixture.

    Returns:
        Alien: A new Alien instance positioned at its default starting location.
    """
    TODO:
    - import Alien from src.aliens.alien
    - create a new Alien(game) instance
    - return it

    WHY a local fixture and not just Alien(game) in each test?
    Same reason as the settings fixture — the habit. If Alien's constructor
    ever gains required arguments or changes its signature, you fix it in
    one place, not in every test function.
```

---

### Test 1: `test_alien_starts_at_expected_position`

```python
def test_alien_starts_at_expected_position(alien: Alien) -> None:
    """
    Verify the alien's starting position is offset from the screen edge
    by exactly one alien's own dimensions.

    The fleet needs breathing room from the screen edges. __init__ sets
    rect.x = rect.width and rect.y = rect.height to achieve this.

    Args:
        alien: A fresh Alien instance from the alien fixture.
    """
```

**Why this test exists:**

`Alien.__init__` places each alien at:
```python
self.rect.x = self.rect.width
self.rect.y = self.rect.height
```

This "one alien unit of padding" is a deliberate design choice — it gives the fleet
a clean starting margin. It also means `_create_fleet()` starts its loop at
`(alien_width, alien_height)`, which matches this initial position.

If someone changes the starting offset — say, to `0` or to half the width — the
entire fleet spawns in a different place. This could clip the first alien against
the edge or leave an unexpectedly large gap. The test **documents the contract**
between the alien's position and the fleet-building logic.

The float tracker `self.x` must also match `self.rect.x` at creation — same
reasoning as Ship and Bullet.

```
TODO (detailed pseudocode):

1. ARRANGE
   - use the alien fixture (Alien already constructed)

2. ASSERT starting x position
   - assert alien.rect.x equals alien.rect.width
   WHY: the alien spawns one alien-width from the left edge. rect.width
        is the alien image's pixel width, not a magic number. If the image
        changes size, the offset adapts automatically — the test confirms
        this relationship holds.

3. ASSERT starting y position
   - assert alien.rect.y equals alien.rect.height
   WHY: same logic for the vertical axis. One alien-height from the top.

4. ASSERT float tracker matches rect
   - assert alien.x equals float(alien.rect.x)
   WHY: self.x is the float used for sub-pixel movement in update().
        At creation it must agree with rect.x. If they disagree, the
        alien will visually jump on its very first update().
```

**What a failure here tells you:**
The starting position in `Alien.__init__` changed. Check whether `_create_fleet()`
also changed to match — they're coupled.

---

### Test 2: `test_alien_edge_check_detects_boundaries`

```python
def test_alien_edge_check_detects_boundaries(alien: Alien, game: AlienInvasion) -> None:
    """
    Verify edge_check() returns True when the alien is at either screen edge,
    and False when it is safely in the middle of the screen.

    This return value is what _check_fleet_edges() uses to decide whether to
    reverse the fleet's direction.

    Args:
        alien: A fresh Alien instance from the alien fixture.
        game: The AlienInvasion instance, needed to get screen dimensions.
    """
```

**Why this test exists:**

`edge_check()` is a **predicate** — a method that asks a yes/no question. It
returns `True` when the alien has reached (or passed) either boundary:

```python
return self.rect.right >= screen_rect.right or self.rect.left <= 0
```

`_check_fleet_edges()` loops through every alien and calls `edge_check()`. If
any alien returns `True`, the entire fleet reverses direction. This is the core
of the fleet bouncing mechanic.

Testing a predicate means checking all three meaningful cases: left edge, right
edge, and the safe middle. If `edge_check()` always returns `True` (broken
condition) or never returns `True` (wrong comparison operator), the fleet either
never moves or never stops. Both break the game.

```
TODO (detailed pseudocode):

1. ARRANGE — get screen dimensions
   - get the screen rect: screen_rect = game.screen.get_rect()

2. ARRANGE + ACT — test right edge
   - set alien.rect.right to screen_rect.right
     (this places the alien exactly at the right boundary)

3. ASSERT — right edge detected
   - assert alien.edge_check() returns True
   WHY: the condition is rect.right >= screen_rect.right. At exactly
        screen_rect.right the comparison is True (equal, not just greater).
        The >= is intentional — if an alien somehow overshoots, it still
        triggers the reversal.

4. ARRANGE + ACT — test left edge
   - set alien.rect.left to 0
     (flush against the left side of the screen)

5. ASSERT — left edge detected
   - assert alien.edge_check() returns True
   WHY: the condition is rect.left <= 0. At exactly 0 (not negative) this
        should still return True. Tests the boundary value, not just the
        obviously-out-of-bounds case.

6. ARRANGE + ACT — test safe middle
   - set alien.rect.x to screen_rect.centerx
     (well within both boundaries)

7. ASSERT — no edge detected
   - assert alien.edge_check() returns False
   WHY: confirms the method doesn't trigger spuriously. If it returned
        True here, the fleet would reverse every frame and never move
        horizontally — which would look like the game is frozen.
```

**What a failure here tells you:**
The comparison operators in `edge_check()` changed or the screen rect isn't
being fetched correctly. Check the method's conditional expression.

---

## Test File 5: `tests/test_button.py`

**Module under test:** `src/aliens/button.py`
**Why test it:** Button is a new module with its own visual contract — it must
centre itself on screen and centre its text on itself. These are **layout
relationships** between three objects (screen, button rect, message rect), and
layout bugs are silent: nothing crashes, the button just looks wrong.

### What Button Does

`Button.__init__` creates a fixed-size rect and positions it at the screen's
centre. `_prep_msg()` renders the text as a Surface and centres that Surface
on the button rect. Together they guarantee the button appears in the right
place with the text in the right place.

---

### Fixture for button.py tests

```
Fixture: button (local to test_button.py, depends on: game)
    """
    Create a fresh Button instance using the live game object.

    Args:
        game: A fully initialized AlienInvasion instance from the game fixture.

    Returns:
        Button: A Button instance with the label "Play".
    """
    TODO:
    - import Button from src.aliens.button
    - create a new Button(game, "Play") instance
    - return it

    WHY "Play" as the message?
    It's the real label the game will use. Using the actual value keeps the
    test grounded in real usage rather than testing with arbitrary data.
```

---

### Test 1: `test_button_centered_on_screen`

```python
def test_button_centered_on_screen(button: Button, game: AlienInvasion) -> None:
    """
    Verify the button rect is centred on the screen, and the message image
    is centred on the button.

    Two layout relationships must hold: button-to-screen, and message-to-button.
    If either is wrong, the visual result is off-centre.

    Args:
        button: A Button instance from the button fixture.
        game: The AlienInvasion instance, used to get screen dimensions.
    """
```

**Why this test exists:**

`Button.__init__` sets:
```python
self.rect.center = self.screen_rect.center
```

And `_prep_msg()` sets:
```python
self.msg_image_rect.center = self.rect.center
```

These are two chained centring operations. If either line is wrong — or if
one is applied before the rect has been sized — the button or its label drifts
off-centre.

This is an example of testing **layout relationships** rather than raw values.
We don't care what the exact pixel coordinates are (they depend on screen size).
We care that `button.rect.center == screen.get_rect().center`. That relationship
must hold regardless of the screen dimensions.

```
TODO (detailed pseudocode):

1. ARRANGE
   - use the button and game fixtures
   - get the screen's rect: screen_rect = game.screen.get_rect()

2. ASSERT button is centred on screen
   - assert button.rect.center equals screen_rect.center
   WHY: center is a tuple (x, y). Comparing the whole tuple confirms both
        horizontal and vertical centering in one assertion. If the button
        is centred vertically but not horizontally (or vice versa), this
        catches it. We're asserting a relationship, not a magic number.

3. ASSERT message is centred on button
   - assert button.msg_image_rect.center equals button.rect.center
   WHY: the text surface must be centred on the button rect, not on the
        screen. If _prep_msg() accidentally centres on the screen instead,
        the text could appear at the right position when the button is
        centred, but drift if the button is ever repositioned. Testing
        the message-to-button relationship keeps these concerns separate.
```

**What a failure here tells you:**
Either the button rect isn't being centred correctly in `__init__`, or
`_prep_msg()` isn't centring the text surface on the button rect. Check
both assignment lines.

---

## Test File 6: `tests/test_alien_invasion.py`

**Module under test:** `src/aliens/main.py`
**Why this is tested last:** AlienInvasion is the **integration layer** —
it wires together Settings, Ship, Bullet, Alien, GameStats, and pygame.
Testing it means testing that the pieces fit together *and* that the
game's rules (lives, game over, fleet repopulation) behave correctly.

### What AlienInvasion Does

`AlienInvasion` is the game's orchestrator. It initialises every subsystem,
creates the alien fleet, tracks game state through `GameStats`, and enforces
rules like lives-based game-over and the bullet limit. The game loop reads
`self.game_active` each frame to decide whether to run updates.

---

### Test 1: `test_game_initializes_with_fleet_and_stats`

```python
def test_game_initializes_with_fleet_and_stats(game: AlienInvasion) -> None:
    """
    Verify that AlienInvasion.__init__ creates all required game components,
    including the alien fleet, GameStats, and the game_active flag.

    This is the full preflight checklist — if any component is missing,
    the game loop will crash on the first frame.

    Args:
        game: A fully initialized AlienInvasion instance from the game fixture.
    """
```

**Why this test exists:**

This is an **integration smoke test** — not testing complex behaviour, but
confirming that the constructor successfully created every object the game
loop depends on. Think of it as a preflight checklist before takeoff.

`run_game()` checks `self.game_active`, calls `self.ship.update()`,
`self._update_bullets()`, `self._update_aliens()`, and `self._update_screen()`.
All of these touch `self.settings`, `self.ship`, `self.screen`, `self.bullets`,
`self.aliens`, and `self.stats`. If any attribute is missing or the wrong type,
the game crashes silently or explodes on frame one.

`game_active` is also critical — it's the gate that controls whether ship,
bullet, and alien logic run each frame. If it starts as `False`, the game
loads but appears completely unresponsive.

```
TODO (detailed pseudocode):

1. ARRANGE
   - use the game fixture (AlienInvasion is already constructed)
   - import Settings, Ship, GameStats from their modules

2. ASSERT core display components
   - assert game.settings is an instance of Settings
   - assert game.screen is an instance of pygame.Surface
   WHY: settings feeds every other component. screen is what everything
        draws to. These are the lowest-level dependencies.

3. ASSERT ship and bullets exist
   - assert game.ship is an instance of Ship
   - assert game.bullets is an instance of pygame.sprite.Group
   - assert len(game.bullets) equals 0
   WHY: bullets must start empty — they're added when the player fires.
        Ship must exist so the game loop can call update() and blit_ship().

4. ASSERT stats exists and has correct type
   - assert game.stats is an instance of GameStats
   WHY: _ship_hit() reads and writes game.stats.ships_left. If stats is
        missing, the first alien collision crashes the game rather than
        decrementing the life count.

5. ASSERT aliens group exists and fleet is populated
   - assert game.aliens is an instance of pygame.sprite.Group
   - assert len(game.aliens) is greater than 0
   WHY: unlike bullets, aliens should NOT start empty. _create_fleet() is
        called in __init__, so there should be a full fleet waiting. If
        len is 0, _create_fleet() failed silently or wasn't called.

6. ASSERT game_active is True
   - assert game.game_active is True
   WHY: game_active gates the entire update loop. False at start means the
        player can't move, shoot, or interact — the game loads but does
        nothing. It should only become False when ships_left hits 0.
```

**What a failure here tells you:**
Something in `AlienInvasion.__init__` was removed, renamed, or reordered.
The assertion that fails tells you exactly which component is broken —
check the constructor and each relevant class's `__init__`.

---

### Test 2: `test_fire_bullet_respects_max_count`

```python
def test_fire_bullet_respects_max_count(game: AlienInvasion) -> None:
    """
    Verify that _fire_bullet() stops creating bullets once the max is reached.

    The bullet limit prevents the player from flooding the screen with
    projectiles. Once bullet_max_count bullets exist, firing should be
    silently ignored.

    Args:
        game: A fully initialized AlienInvasion instance from the game fixture.
    """
```

**Why this test exists:**

`_fire_bullet()` has a guard clause:
```python
if len(self.bullets) < self.settings.bullet_max_count:
```

This is a **business rule** — a deliberate design decision about game
balance. Without the limit, a player could hold spacebar and flood the
screen with bullets, tanking performance and making the game trivially easy.

Testing business rules is high-value because they're the decisions that
are most likely to be accidentally changed during refactoring. Someone
might change `<` to `<=` (off-by-one), remove the check for "simplicity",
or change the max without realising the impact.

```
TODO (detailed pseudocode):

1. ARRANGE
   - use the game fixture
   - look up the max count: store game.settings.bullet_max_count as max_count

2. ACT — fill up to the limit
   - loop max_count times:
       call game._fire_bullet() on each iteration
   - this should create exactly max_count bullets

3. ASSERT — we're at the limit
   - assert len(game.bullets) equals max_count
   WHY: confirms that _fire_bullet() successfully creates bullets up to
        the limit. If this fails, the creation logic itself is broken.

4. ACT — try to exceed the limit
   - call game._fire_bullet() one more time (attempt number max_count + 1)

5. ASSERT — count didn't increase
   - assert len(game.bullets) still equals max_count
   WHY: the guard clause should have blocked the extra bullet. If the
        count is now max_count + 1, the limit isn't being enforced.
        This is the actual test of the business rule.
```

**What a failure here tells you:**
If step 3 fails: bullets aren't being created or added to the group
properly. Check `_fire_bullet()` and `Bullet.__init__`.
If step 5 fails: the max count check is broken. Look at the comparison
operator and the value of `bullet_max_count`.

---

### Test 3: `test_ship_hit_decrements_ship_count`

```python
def test_ship_hit_decrements_ship_count(game: AlienInvasion) -> None:
    """
    Verify that _ship_hit() decrements ships_left by one and resets the
    game board with a fresh fleet.

    Each time the ship is destroyed (alien collision or reaching the bottom),
    the player should lose one life and the game should reset to a fresh state.

    Args:
        game: A fully initialized AlienInvasion instance from the game fixture.
    """
```

**Why this test exists:**

`_ship_hit()` is the consequence of two separate events: the ship colliding
with an alien, and aliens reaching the bottom of the screen. Both call
`_ship_hit()` via `_update_aliens()`. It has two jobs:

1. Decrement `stats.ships_left` (player loses a life)
2. Reset the board: clear bullets, clear aliens, recreate the fleet,
   recentre the ship

This test covers job 1 and the "board reset" half of job 2. Testing these
together makes sense because the decrement only happens *when there are
ships left* — it's inside an `if self.stats.ships_left > 0:` guard. Testing
that the count went down also implicitly confirms the guard was entered.

This is also your first test of a **method with side effects** — `_ship_hit()`
changes multiple pieces of state in one call. The pattern is the same: record
the "before" state, call the method, assert the expected "after" state.

```
TODO (detailed pseudocode):

1. ARRANGE
   - use the game fixture
   - record the starting life count:
       store game.stats.ships_left as initial_ships
     (this will be settings.ship_limit, currently 3)

2. ACT
   - call game._ship_hit()
     (simulates the ship being hit once)

3. ASSERT ship count decreased by one
   - assert game.stats.ships_left equals (initial_ships - 1)
   WHY: each hit costs exactly one life. The test uses initial_ships - 1
        rather than hardcoding 2, so the test still works if ship_limit
        ever changes in Settings.

4. ASSERT fleet was recreated
   - assert len(game.aliens) is greater than 0
   WHY: _ship_hit() calls self.aliens.empty() then self._create_fleet().
        If both happen correctly, the aliens group should be non-empty
        after the call. If it's 0, either empty() was called but
        _create_fleet() wasn't, or _create_fleet() produced no aliens.

5. ASSERT game is still active
   - assert game.game_active is True
   WHY: game_active should only become False when ships_left hits 0.
        With initial_ships > 0, this hit should NOT end the game. If
        game_active is False here, the game ends one hit too early.
```

**What a failure here tells you:**
Step 3: the decrement in `_ship_hit()` is missing or has an off-by-one.
Step 4: `_create_fleet()` wasn't called or produced no aliens.
Step 5: the `if self.stats.ships_left > 0:` guard is wrong or missing.

---

### Test 4: `test_ship_hit_ends_game_when_no_ships_left`

```python
def test_ship_hit_ends_game_when_no_ships_left(game: AlienInvasion) -> None:
    """
    Verify that _ship_hit() sets game_active to False when ships_left is
    already zero — triggering the game over condition.

    The game should end, not crash, when all lives are exhausted.

    Args:
        game: A fully initialized AlienInvasion instance from the game fixture.
    """
```

**Why this test exists:**

`_ship_hit()` branches on `ships_left`:

```python
if self.stats.ships_left > 0:
    self.stats.ships_left -= 1
    # ... reset board ...
else:
    self.game_active = False
```

The `else` branch is the **game over condition** — the only way `game_active`
should ever become `False` through normal gameplay. If this branch is broken,
one of two bad things happens:

- The `if` is always taken → the game never ends (infinite lives)
- The `else` fires too early → the game ends before the player runs out of lives

Both are gameplay-breaking bugs that wouldn't cause a crash, just wrong
behaviour. Tests that catch **silent logic errors** are among the most valuable
you can write — these are the bugs that pass manual testing unless you
specifically play through a game over.

This is also a good example of **arranging state to test a specific branch**.
We don't simulate three deaths to get to zero lives — we directly set
`ships_left = 0` to isolate the else branch. This keeps the test fast and
focused on exactly one thing.

```
TODO (detailed pseudocode):

1. ARRANGE
   - use the game fixture
   - manually set game.stats.ships_left to 0
     (we're forcing the "no lives left" condition directly)
   WHY: we're not testing the decrement logic here (that's Test 3).
        We're testing what happens when the count is already zero.
        Direct state manipulation is the right tool for isolating a branch.

2. ACT
   - call game._ship_hit()

3. ASSERT game is now over
   - assert game.game_active is False
   WHY: the else branch should have set game_active = False. If it's
        still True, the game never ends — the player has effectively
        infinite lives. This is the core assertion.

4. ASSERT ships_left did not go negative
   - assert game.stats.ships_left equals 0
   WHY: the else branch should NOT decrement ships_left again — it's
        already at the floor. If ships_left is now -1, the decrement
        ran when it shouldn't have. Negative lives would cause confusing
        state if the game were ever restarted.
```

**What a failure here tells you:**
Step 3: the `else` branch is missing or unreachable. The `if` condition
may be wrong (e.g. `>= 0` instead of `> 0`), or the branch sets the
wrong attribute.
Step 4: the decrement ran inside the else. Check the if/else structure
in `_ship_hit()`.

---

## Test File Structure

When all tests are written, the project should look like this:

```
tests/
    __init__.py             <-- already exists
    conftest.py             <-- shared fixtures (pygame_init, game)
    test_settings.py        <-- 2 tests, no pygame dependency
    test_ship.py            <-- 2 tests, uses game fixture
    test_bullet.py          <-- 2 tests, uses game fixture
    test_alien.py           <-- 2 tests, uses game fixture + local alien fixture
    test_button.py          <-- 1 test,  uses game fixture + local button fixture
    test_alien_invasion.py  <-- 4 tests, uses game fixture
```

## Build Order

Write the tests in this order — each file builds on what you learned in
the previous one:

1. **conftest.py** — set up the shared fixtures first. Everything else
   depends on these.
2. **test_settings.py** — pure assertions, no fixtures needed beyond a
   Settings instance. Gets you comfortable with the assert pattern.
3. **test_ship.py** — introduces the game fixture. Tests initial state
   and conditional logic.
4. **test_bullet.py** — tests object relationships (bullet-to-ship) and
   state changes over time.
5. **test_alien.py** — tests a predicate method and starting position.
   Introduces local fixtures and boundary value testing.
6. **test_button.py** — tests layout relationships rather than raw values.
   Introduces the idea that some bugs are silent (no crash, just wrong).
7. **test_alien_invasion.py** — integration tests. Verifies all pieces fit
   together, business rules hold, and branching game-over logic works.

## Running the Tests

```bash
# run all tests from project root
pytest

# run a specific file
pytest tests/test_settings.py

# run with verbose output (shows each test name and result)
pytest -v

# stop on first failure (useful while writing tests)
pytest -x
```
