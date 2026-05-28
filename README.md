# ConnectX — Starter Kit para Agentes Inteligentes

> Diseña, entrena y enfrenta tu propio agente de IA en un torneo de **Connect Four** aumentado.

---

## ¿Qué es ConnectX?

ConnectX es una generalización de Connect Four: dos jugadores se turnan para soltar fichas en un tablero de **6 filas × 7 columnas**. Gana el primero en alinear **4 fichas consecutivas** en horizontal, vertical o diagonal. Si el tablero se llena sin ganador, el resultado es empate.

```
. . . . . . .
. . . . . . .
. . . . . . .
. . . . B . .
. . A . B . .
. A A . B . .
0 1 2 3 4 5 6   ← columnas
```

---

## Instalación

Requiere **Python 3.10+**.

```bash
pip install -r requirements.txt
```

---

## Comandos principales

```bash
# Jugar tu agente contra el baseline
python3 -m scripts.play_vs_baseline agents/team_template.py

# Ver una partida en vivo entre dos agentes
python3 -m scripts.watch_match agents/team_template.py agents/baseline_agent.py

# Torneo round-robin entre todos los agentes en agents/
python3 -m scripts.tournament
```

---

## Estructura del proyecto

```
connectx-starter-kit/
├── agents/
│   ├── team_template.py      # ← TU agente va aquí
│   ├── default_agent.py      # Ejemplo usando herramientas
│   ├── baseline_agent.py     # Oponente heurístico por defecto
│   └── random_agent.py       # Agente aleatorio (mínimo posible)
├── arena/
│   ├── board.py              # Lógica del tablero y detección de victoria
│   └── tools.py              # 5 herramientas reutilizables
├── scripts/
│   ├── play_vs_baseline.py   # Jugar una partida contra el baseline
│   ├── tournament.py         # Torneo round-robin
│   └── watch_match.py        # Ver una partida en tiempo real
├── docs/
│   ├── crear-agente.md       # Guía paso a paso para crear tu agente
│   ├── herramientas.md       # Referencia completa de las 5 herramientas
│   └── machine-learning.md   # Cómo aplicar ML a este problema
└── requirements.txt
```

---

## Reglas de la actividad

1. Tu agente debe definir la función `my_agent(observation, configuration)`
2. Debe retornar un entero válido entre `0` y `6`
3. Puede usar **máximo 3 herramientas** del kit por partida
4. Jugar en una columna llena es derrota automática
5. El torneo es **round-robin**: cada agente se enfrenta a todos los demás una vez
6. Puntuación: **3 pts** por victoria, **1 pt** por empate, **0 pts** por derrota

---

## Documentación

| Documento | Contenido |
|---|---|
| [Crear tu agente](docs/crear-agente.md) | Paso a paso para escribir y probar tu agente |
| [Herramientas](docs/herramientas.md) | Referencia de las 5 herramientas y cómo combinarlas |
| [Machine Learning](docs/machine-learning.md) | Cómo aplicar RL, minimax y redes neuronales |

---

## Recursos externos

- [Kaggle — ConnectX environment](https://www.kaggle.com/c/connectx) — competencia original con leaderboard global
- [Sutton & Barto — Reinforcement Learning: An Introduction](http://incompleteideas.net/book/the-book.html)
- [AlphaZero paper (DeepMind)](https://arxiv.org/abs/1712.01815)
- [Minimax con alpha-beta](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning)
