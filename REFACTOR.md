# Refactor Guide — Alien Invasion Final Polish

This file now reflects the project as it actually stands, not as it once imagined itself in a more innocent age.

The plan has been trimmed to the work that is still relevant:
- Sound effects are off the list.
- High score persistence is already working.
- The main remaining feature is finishing the intro / landing screen properly.
- After that, there is one small cleanup pass to bring tests and notes into line with the new state-based flow.

---

## Current Snapshot

### Already done

The refactor has already started. These pieces are in place:

```python
# In AlienInvasion.__init__()
self.game_state = "intro"
self.play_button = Button(self, "Play")
```

```python
# In run_game()
if self.game_state == "playing":
    self.ship.update()
    self._update_bullets()
    self._update_aliens()
```

```python
# In _ship_hit()
else:
    self.game_state = "intro"
    pygame.mouse.set_visible(True)
```

```python
# In GameStats.__init__()
self.reset_stats()
self.get_high_score()
```

```python
# In Scoreboard.check_high_score()
if self.stats.score > self.stats.high_score:
    self.stats.high_score = self.stats.score
    self.prep_high_score()
    self.stats.save_high_score()
```

So the project already has:
- a `game_state` string instead of the old `game_active` boolean
- a Play button
- a path back to the intro state after game over
- high score load/save behaviour

### Still not finished

The intro page is not working yet because the wiring is incomplete:
- `_draw_intro_screen()` exists, but `_update_screen()` never calls it
- gameplay objects are still drawn during the intro state
- the scoreboard is still drawn during the intro state
- mouse and keyboard input are not fully routed by `game_state`
- the title text in `_draw_intro_screen()` is not centred yet
- one test and one planning note still refer to `game_active`

Think of it like fitting a new front door but forgetting to tell the house where the hallway is.

---

## 1. Finish The Intro / Landing Screen

### What you're building

A proper title screen before gameplay starts.

Right now the project has the parts for that screen, but the main draw loop still behaves like the old version, so the game world shows up underneath the Play button. The goal here is to make the intro state feel like its own screen, not just the normal game wearing a paper hat.

### Learning goal: a simple state machine

This is a very useful pattern to learn early.

A boolean can only answer one question: on or off.

A state string can answer a better question: where is the game right now?

For this project, that means:
- `"intro"`: show the landing screen and wait for input
- `"playing"`: update and draw the real game

That separation is the whole point of this refactor.

### What the code already has

You already added the state variable:

```python
# In __init__()
self.game_state = "intro"
self.play_button = Button(self, "Play")
```

You already limit gameplay updates to the playing state:

```python
def run_game(self) -> None:
    while True:
        self._check_events()
        if self.game_state == "playing":
            self.ship.update()
            self._update_bullets()
            self._update_aliens()

        self._update_screen()
        self.clock.tick(60)
```

You already wrote an intro drawing helper:

```python
def _draw_intro_screen(self) -> None:
    self.screen.fill(self.settings.bg_color)
    self.font = pygame.font.SysFont(None, 72)
    self.text_color: tuple[int, int, int] = (255, 255, 255)
    game_title = "Alien Invasion!"
    self.title_image = self.font.render(game_title, True, self.text_color, self.settings.bg_color)
    self.title_rect = self.title_image.get_rect()
    self.title_rect.top = self.screen.get_rect().top
    self.screen.blit(self.title_image, self.title_rect)
    self.play_button.draw_button()
```

You already have a start-game path on button click:

```python
def _check_play_button(self, mouse_position) -> None:
    button_clicked = self.play_button.rect.collidepoint(mouse_position)
    if button_clicked and not self.game_state == "playing":
        self.settings.initialize_dynamic_settings()
        self.stats.reset_stats()
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()
        self.game_state = "playing"
        pygame.mouse.set_visible(False)

        self.bullets.empty()
        self.aliens.empty()
        self._create_fleet()
        self.ship.center_ship()
```

### Why it still does not work

The current draw loop does not actually use the intro state:

```python
def _update_screen(self) -> None:
    self.screen.fill(self.settings.bg_color)
    for bullet in self.bullets.sprites():
        bullet.draw_bullet()
    self.ship.blit_ship()
    self.aliens.draw(self.screen)
    self.sb.show_score()
    if not self.game_state == "playing":
        self.play_button.draw_button()
    pygame.display.flip()
```

That means:
- bullets still draw
- the ship still draws
- aliens still draw
- the scoreboard still draws
- the intro helper never runs

So the state exists, but the rendering logic has not properly moved over to it yet.

### TODOs

**Step 1 — route `_update_screen()` through `game_state`**

This is the main fix.

The intro state should call `_draw_intro_screen()`.
The playing state should draw bullets, ship, aliens, and scoreboard.

Target shape:

```python
def _update_screen(self) -> None:
    self.screen.fill(self.settings.bg_color)

    if self.game_state == "intro":
        self._draw_intro_screen()
    elif self.game_state == "playing":
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blit_ship()
        self.aliens.draw(self.screen)
        self.sb.show_score()

    pygame.display.flip()
```

Why this matters:
- it finally makes the intro screen real
- it stops gameplay visuals leaking into the menu state
- it follows the exact state-machine idea you started already

**Step 2 — fix the intro title layout**

At the moment the title is rendered, but it is not centred. You create the rect and only set `top`, so it stays at the left edge by default.

Current line of thinking:

```python
self.title_rect = self.title_image.get_rect()
self.title_rect.top = self.screen.get_rect().top
```

What you want instead is something like:

```python
self.title_rect = self.title_image.get_rect()
self.title_rect.centerx = self.screen.get_rect().centerx
self.title_rect.top = self.screen.get_rect().height // 4
```

Learning note:
- `get_rect()` gives you a movable box around the rendered text
- setting `centerx` centres it horizontally
- setting `top` places it vertically

This is standard `pygame` positioning, and worth getting comfortable with because you will use it everywhere.

**Step 3 — route mouse clicks by state**

Right now every mouse click gets sent to `_check_play_button()`:

```python
elif event.type == pygame.MOUSEBUTTONDOWN:
    mouse_position = pygame.mouse.get_pos()
    self._check_play_button(mouse_position)
```

That works, but it is still old-style logic.

What you want is to only treat the click as a Play-button click while in the intro state:

```python
elif event.type == pygame.MOUSEBUTTONDOWN:
    if self.game_state == "intro":
        mouse_position = pygame.mouse.get_pos()
        self._check_play_button(mouse_position)
```

This keeps your event handling clean and matches the refactor goal: each state handles its own business.

**Step 4 — stop gameplay input from firing during the intro**

At the moment, key presses still go through `_check_key_down()` regardless of state:

```python
elif event.type == pygame.KEYDOWN:
    self._check_key_down(event)
```

That means movement flags and bullet firing can still be triggered while sitting on the intro screen.

You have a couple of acceptable ways to fix this.

Simplest route:
- keep `q` as a global quit key
- only allow movement and shooting when `self.game_state == "playing"`

One possible shape:

```python
elif event.type == pygame.KEYDOWN:
    if event.key == pygame.K_q:
        sys.exit()
    elif self.game_state == "playing":
        self._check_key_down(event)
```

You could also guard inside `_check_key_down()`, but the important thing is the same: intro mode should not behave like gameplay mode.

**Step 5 — test the state flow end to end**

Once the draw and event routing are fixed, check the full loop manually:

1. Start the game.
2. Confirm you only see the intro screen.
3. Click Play.
4. Confirm gameplay appears and the mouse cursor hides.
5. Lose all ships.
6. Confirm the game returns to the intro screen and the mouse cursor becomes visible again.

Why this check matters:
- `_ship_hit()` already sends the game back to `"intro"`
- once `_update_screen()` is state-based, that path should finally display the correct screen

### Watch-outs

- Do not leave `self.sb.show_score()` outside the `"playing"` branch
- Do not leave ship, alien, or bullet drawing outside the `"playing"` branch
- If the title still looks wrong after centring, print or inspect the rect values rather than guessing
- You do not have to rename `_check_play_button()` to `_start_game()` unless you want the extra cleanup; the important part is the state-based flow

---

## 2. Clean Up The State Refactor

### What this is

This is the short tidy-up pass after the intro screen works.

The code has moved to `game_state`, but one test and one project note still talk about `game_active`. That is why the test suite currently reports one failure even though the game has mostly moved on.

### TODOs

**Step 1 — update the stale test**

Current test:

```python
def test_game_starts_inactive(pygame_game) -> None:
    assert not pygame_game.game_active
```

Replace the idea with the new truth:

```python
def test_game_starts_in_intro_state(pygame_game) -> None:
    assert pygame_game.game_state == "intro"
```

This is not just pedantry. Tests are supposed to describe reality. If the test still checks the old API, it is like labelling a cat as “small horse” and then being shocked by the veterinary bill.

**Step 2 — update `TEST_OUTLINE.md`**

That note still references `game_active`, so it should either:
- be updated to `game_state == "intro"`
- or be removed if the tests it describes are already written

Keep the project notes aligned with the code, otherwise future-you has to do detective work for no reason.

**Step 3 — optional small improvement**

Once the intro screen works, consider adding one extra test around state transitions.

Useful examples:
- clicking Play changes `game_state` from `"intro"` to `"playing"`
- the game starts in `"intro"`

This is optional, but it would be a good learning exercise because state transitions are exactly the sort of thing tests are good at catching.

---

## Order Of Attack

Do the remaining work in this order:

1. Finish `_update_screen()` so it branches on `game_state`
2. Fix `_draw_intro_screen()` so the title is centred
3. Route mouse and keyboard input by state in `_check_events()`
4. Manually test the full intro -> playing -> intro loop
5. Update the stale test and `TEST_OUTLINE.md`

That order keeps the work sensible:
- first make the screen render correctly
- then make input behave correctly
- then clean up the test/documentation drift

Small, testable steps. No heroics required.
