# Referencia de Herramientas

El módulo `arena/tools.py` incluye 5 herramientas listas para usar en tu agente. Cada una recibe el estado del tablero como diccionarios y devuelve una columna (`int`) o `None` si no encuentra una jugada relevante.

---

## Cómo funcionan internamente

Cada herramienta sigue el mismo contrato:

```python
def herramienta(obs: dict, cfg: dict) -> int | None:
    ...
```

Donde:

```python
obs = {
    "board": list(observation.board),  # lista de 42 enteros
    "mark": observation.mark,          # 1 o 2
}

cfg = {
    "rows": configuration.rows,        # 6
    "cols": configuration.columns,     # 7
    "inarow": configuration.inarow,    # 4
}
```

---

## Las 5 herramientas

### `win_now`
**Si hay una jugada que gana la partida en este turno, la ejecuta.**

Itera por todas las columnas válidas, simula la jugada con `drop_piece`, y verifica `check_win`. Devuelve la primera columna ganadora que encuentre, o `None` si no existe.

```
Antes:        Después de win_now → columna 4:
. . . . . . .   . . . . . . .
. . . . . . .   . . . . . . .
. . . . . . .   . . . . . . .
. . . . . . .   . . . . . . .
. . . A . . .   . . . A . . .
. A A A . . .   . A A A A . .   ← victoria!
```

---

### `block_now`
**Si el rival puede ganar en su próximo turno, bloquea esa columna.**

Misma lógica que `win_now` pero simulando la jugada del oponente. Devuelve la columna a bloquear, o `None` si el rival no tiene victoria inmediata.

```
Antes:        Después de block_now → columna 3:
. . . . . . .   . . . . . . .
. . . . . . .   . . . . . . .
. . . . . . .   . . . . . . .
. . . . . . .   . . . . . . .
. . . B . . .   . . . B . . .
. B B . . . .   . B B A . . .   ← bloqueo
```

---

### `prefer_center`
**Elige la columna válida más cercana al centro (columna 3).**

El centro del tablero es estratégicamente más valioso porque conecta más direcciones posibles. Esta herramienta siempre devuelve una columna (nunca `None`), por lo que actúa como fallback seguro.

---

### `avoid_dead`
**Evita columnas casi llenas sin potencial estratégico.**

⚠️ Esta herramienta está actualmente sin implementación (devuelve siempre `None`). Es un punto de extensión que puedes completar tú mismo.

---

### `random_valid`
**Elige una columna válida al azar.**

Siempre devuelve algo. Útil como fallback final o para agentes exploratorios. `apply_tools` lo usa internamente si ninguna otra herramienta decide.

---

## Cómo combinarlas con `apply_tools`

```python
from arena.tools import apply_tools

result = apply_tools(obs_dict, cfg_dict, ["win_now", "block_now", "prefer_center"])
```

El flujo de `apply_tools`:

```
win_now → ¿devolvió columna?  → SÍ → retorna esa columna
                               → NO ↓
block_now → ¿devolvió columna? → SÍ → retorna esa columna
                                → NO ↓
prefer_center → retorna la columna más al centro
```

Si todas devuelven `None` (lo cual no pasa con `prefer_center` o `random_valid`), usa `random_valid` como fallback de seguridad.

---

## Estrategias de combinación

| Combinación | Estilo |
|---|---|
| `["win_now", "block_now", "prefer_center"]` | Equilibrado — gana, defiende, luego posiciona |
| `["win_now", "prefer_center", "random_valid"]` | Agresivo — prioriza atacar sobre defender |
| `["block_now", "win_now", "prefer_center"]` | Defensivo — prioriza no perder |

> **Regla:** solo puedes declarar 3 herramientas por partida.

---

## Extender o crear tus propias herramientas

Puedes escribir funciones con el mismo contrato (`obs: dict, cfg: dict → int | None`) y pasarlas directamente a `apply_tools`, o llamarlas manualmente en tu agente:

```python
def my_tool(obs, cfg):
    from arena.board import Board
    board = Board(cfg["rows"], cfg["cols"], cfg["inarow"], obs["board"])
    # tu lógica aquí
    return None  # o un int

def my_agent(observation, configuration):
    obs_dict = {"board": list(observation.board), "mark": observation.mark}
    cfg_dict = {"rows": observation.rows, "cols": configuration.columns, "inarow": configuration.inarow}

    result = my_tool(obs_dict, cfg_dict)
    if result is not None:
        return result

    from random import choice
    return choice([c for c in range(configuration.columns) if observation.board[c] == 0])
```
