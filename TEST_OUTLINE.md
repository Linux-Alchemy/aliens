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
**Max tests per file:** 2
**Total tests:** 8

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

## Test File 4: `tests/test_alien_invasion.py`

**Module under test:** `src/aliens/alien_invasion.py`
**Why this is tested last:** AlienInvasion is the **integration layer** —
it wires together Settings, Ship, Bullet, and pygame. Testing it means
testing that the pieces fit together correctly.

### What AlienInvasion Does

`AlienInvasion` is the game's main class. It initialises pygame, creates
the display, instantiates Ship and a bullet Group, runs the main loop, and
handles all input events. It's the orchestrator.

---

### Test 1: `test_game_initializes_with_required_components`

```python
def test_game_initializes_with_required_components(game: AlienInvasion) -> None:
    """
    Verify that AlienInvasion.__init__ creates all required game components.

    The game needs a screen surface, a Settings instance, a Ship instance,
    and an empty sprite Group for bullets. If any of these are missing,
    the game loop will crash.

    Args:
        game: A fully initialized AlienInvasion instance from the game fixture.
    """
```

**Why this test exists:**

This is an **integration smoke test**. It doesn't test complex behaviour —
it tests that the constructor successfully creates all the objects the game
loop expects to find. Think of it as a preflight checklist before takeoff.

`run_game()` calls `self.ship.update()`, `self._update_bullets()`, and
`self._update_screen()`. All of these touch `self.settings`, `self.ship`,
`self.screen`, and `self.bullets`. If any of those attributes don't exist
or are the wrong type, the game crashes on the first frame.

```
TODO (detailed pseudocode):

1. ARRANGE
   - use the game fixture (AlienInvasion is already constructed)

2. ASSERT settings exists and is correct type
   - assert game.settings is an instance of Settings
   WHY: every other component reads from settings. If it's missing or
        the wrong type, nothing else works.

3. ASSERT screen exists and is a pygame Surface
   - assert game.screen is an instance of pygame.Surface
   WHY: the screen is what everything draws to. pygame.display.set_mode()
        returns a Surface. If this failed silently, we'd have no display.

4. ASSERT ship exists and is correct type
   - assert game.ship is an instance of Ship
   WHY: the game loop calls game.ship.update() and game.ship.blit_ship()
        every frame. A missing ship means a crash on frame 1.

5. ASSERT bullets group exists and is empty
   - assert game.bullets is an instance of pygame.sprite.Group
   - assert len(game.bullets) equals 0
   WHY: bullets starts as an empty Group. Bullets get added when the
        player fires. If it's not a Group (or not empty), the sprite
        management system won't work correctly.
```

**What a failure here tells you:**
Something in AlienInvasion.__init__ was removed, renamed, or reordered in
a way that broke the construction chain. Check the constructor.

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

## Test File Structure

When all tests are written, the project should look like this:

```
tests/
    __init__.py          <-- already exists
    conftest.py          <-- shared fixtures (pygame_init, game)
    test_settings.py     <-- 2 tests, no pygame dependency
    test_ship.py         <-- 2 tests, uses game fixture
    test_bullet.py       <-- 2 tests, uses game fixture
    test_alien_invasion.py  <-- 2 tests, uses game fixture
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
5. **test_alien_invasion.py** — integration tests. Verifies the pieces
   fit together and business rules hold.

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
