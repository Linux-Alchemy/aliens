# Test Outline: Next Tests to Write

Five simple tests covering bits of the game not yet touched by the existing suite.
Each one is a few lines and a single assertion or two.

---

## 1. `game_active` starts as `False` — `test_main.py`

The game shouldn't start until the Play button is clicked.

```python
def test_game_starts_inactive(pygame_game):
    assert pygame_game.game_active == False
```

---

## 2. Alien fleet is populated on init — `test_main.py`

After `__init__`, there should be aliens on the board — not an empty group.

```python
def test_alien_fleet_not_empty(pygame_game):
    assert len(pygame_game.aliens) > 0
```

---

## 3. `GameStats` initialises with correct defaults — new file `test_game_stats.py`

Score, level, and ships_left should all be at their starting values.

```python
def test_game_stats_defaults(pygame_game):
    assert pygame_game.stats.score == 0
    assert pygame_game.stats.level == 1
    assert pygame_game.stats.ships_left == pygame_game.settings.ship_limit
```

---

## 4. `reset_stats()` resets score and level — `test_game_stats.py`

Simulates what happens when the player hits Play again after a game over.

```python
def test_reset_stats(pygame_game):
    pygame_game.stats.score = 500
    pygame_game.stats.level = 4
    pygame_game.stats.reset_stats()
    assert pygame_game.stats.score == 0
    assert pygame_game.stats.level == 1
```

---

## 5. `increase_speed()` actually increases speeds — `test_settings.py`

Makes sure levelling up has a real effect on the dynamic settings.

```python
def test_increase_speed(defaults):
    initial_bullet_speed = defaults.bullet_speed
    defaults.increase_speed()
    assert defaults.bullet_speed > initial_bullet_speed
```

---
