# Guía: Cómo crear tu propio agente

Tu agente vive en `agents/team_template.py`. La única regla estructural: debes definir una función llamada `my_agent` con esta firma exacta:

```python
def my_agent(observation, configuration):
    ...
    return columna  # entero entre 0 y 6
```

Esta función se llama una vez por turno. Recibe el estado del tablero y debe retornar la columna donde quiere jugar.

---

## Parámetros de entrada

### `observation`

| Atributo | Tipo | Descripción |
|---|---|---|
| `observation.board` | `list[int]` | Estado del tablero: lista de 42 enteros. `0` = vacío, `1` = jugador 1, `2` = jugador 2 |
| `observation.mark` | `int` | Tu ficha: `1` si juegas primero, `2` si juegas segundo |

El tablero es plano, pero representa una grilla de 6 filas × 7 columnas:

```
índice = fila * 7 + columna
```

Ejemplo: la celda en fila 5 (fila inferior), columna 3 es `board[5*7+3]` = `board[38]`.

### `configuration`

| Atributo | Valor | Descripción |
|---|---|---|
| `configuration.rows` | `6` | Número de filas |
| `configuration.columns` | `7` | Número de columnas |
| `configuration.inarow` | `4` | Fichas consecutivas para ganar |

---

## Paso 1 — Agente mínimo

El agente más simple posible: elige una columna válida al azar.

```python
from random import choice

def my_agent(observation, configuration):
    valid = [c for c in range(configuration.columns) if observation.board[c] == 0]
    return choice(valid)
```

> Las columnas válidas son aquellas cuya celda superior (`board[col]`) está vacía.

---

## Paso 2 — Usar las herramientas del kit

El kit incluye 5 herramientas listas para usar. Puedes combinar hasta **3** de ellas.

```python
from arena.tools import apply_tools

def my_agent(observation, configuration):
    obs_dict = {
        "board": list(observation.board),
        "mark": observation.mark,
    }
    cfg_dict = {
        "rows": configuration.rows,
        "cols": configuration.columns,
        "inarow": configuration.inarow,
    }
    return apply_tools(obs_dict, cfg_dict, ["win_now", "block_now", "prefer_center"])
```

`apply_tools` ejecuta las herramientas en orden y devuelve el resultado de la primera que no sea `None`. Si ninguna decide, usa `random_valid` como fallback automático.

Ver referencia completa en [herramientas.md](herramientas.md).

---

## Paso 3 — Lógica propia

Puedes escribir lógica completamente custom usando `arena.board.Board`:

```python
from arena.board import Board

def my_agent(observation, configuration):
    board = Board(
        configuration.rows,
        configuration.columns,
        configuration.inarow,
        list(observation.board)
    )
    mark = observation.mark

    # Ganar si puedo
    for col in board.valid_moves():
        test = board.copy()
        test.drop_piece(col, mark)
        if test.check_win(mark):
            return col

    # Bloquear si el rival puede ganar
    opponent = 1 if mark == 2 else 2
    for col in board.valid_moves():
        test = board.copy()
        test.drop_piece(col, opponent)
        if test.check_win(opponent):
            return col

    # Preferir el centro
    moves = board.valid_moves()
    return min(moves, key=lambda c: abs(c - configuration.columns // 2))
```

---

## Probar tu agente

```bash
# Contra el baseline
python3 -m scripts.play_vs_baseline agents/team_template.py

# Ver la partida animada en terminal
python3 -m scripts.watch_match agents/team_template.py agents/baseline_agent.py

# Torneo completo
python3 -m scripts.tournament
```

---

## API de `Board`

| Método | Retorno | Descripción |
|---|---|---|
| `board.valid_moves()` | `list[int]` | Columnas donde se puede jugar |
| `board.drop_piece(col, mark)` | `bool` | Suelta una ficha; retorna `False` si la columna está llena |
| `board.check_win(mark)` | `bool` | Verifica si `mark` ha ganado |
| `board.is_full()` | `bool` | Verifica si el tablero está lleno |
| `board.copy()` | `Board` | Copia profunda del tablero (útil para simulaciones) |
| `board.to_observation(mark)` | objeto | Convierte al formato `observation` del motor |

---

## Errores comunes

**Retornar una columna llena** → derrota automática. Siempre filtra con `valid_moves()`.

**Retornar `None`** → el motor lanzará un error. Asegúrate de tener siempre un fallback.

**Modificar el tablero original** → usa siempre `board.copy()` antes de simular jugadas.
