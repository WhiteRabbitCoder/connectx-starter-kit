# ConnectX — Starter Kit para Agentes Inteligentes

> Diseña y enfrenta tu propio agente de IA en un torneo de **Connect Four**.  
> Este kit es el punto de partida de la actividad: aquí encontrarás el tablero, las herramientas, los agentes de ejemplo y todo lo necesario para competir.

---

## ¿Qué es esto?

ConnectX es una versión programable de Connect Four. En lugar de jugar tú, **escribes un programa** que juega por ti. El programa recibe el estado del tablero en cada turno y decide en qué columna soltar su ficha.

El objetivo de la actividad es que diseñes ese programa — tu **agente** — y lo enfrentes al de tus compañeros en un torneo.

---

## El juego

Dos jugadores se turnan para soltar fichas en un tablero de **6 filas × 7 columnas**.  
Gana el primero en alinear **4 fichas consecutivas** en horizontal, vertical o diagonal.

```
. . . . . . .
. . . . . . .
. . . . . . .
. . . . B . .
. . A . B . .
. A A . B . .
0 1 2 3 4 5 6   ← número de columna
```

En este ejemplo, B gana si juega la columna 4 (conecta 4 verticales).  
Las fichas caen por gravedad: siempre van al fondo de la columna disponible.

---

## Instalación

Requiere **Python 3.10 o superior**.

```bash
# 1. Crear y activar entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt
```

---

## ¿Por dónde empiezo?

**1. Abre `agents/team_template.py`** — ese es tu agente. Edita la función `my_agent`.

**2. Pruébalo contra el baseline:**
```bash
python3 -m scripts.play_vs_baseline agents/team_template.py
```

**3. Míralo jugar en vivo:**
```bash
python3 -m scripts.watch_match agents/team_template.py agents/baseline_agent.py
```

**4. Corre el torneo completo:**
```bash
python3 -m scripts.tournament
```

---

## Estructura del proyecto

```
connectx-starter-kit/
├── agents/
│   ├── team_template.py      # ← TU agente va aquí
│   ├── default_agent.py      # Ejemplo usando las herramientas del kit
│   ├── baseline_agent.py     # Oponente heurístico (referencia)
│   └── random_agent.py       # Agente que juega al azar
├── arena/
│   ├── board.py              # Lógica del tablero
│   └── tools.py              # 5 herramientas listas para usar
├── scripts/
│   ├── play_vs_baseline.py   # Jugar contra el baseline
│   ├── tournament.py         # Torneo round-robin
│   └── watch_match.py        # Ver una partida animada en terminal
├── docs/
│   ├── guia-de-clase.md      # Documento completo de la actividad (empieza aquí)
│   ├── crear-agente.md       # Referencia técnica: cómo escribir tu agente
│   ├── herramientas.md       # Las 5 herramientas y cómo combinarlas
│   └── machine-learning.md   # Cómo aplicar RL y redes neuronales
└── requirements.txt
```

---

## Reglas de la actividad

| Regla | Detalle |
|---|---|
| Firma de la función | `def my_agent(observation, configuration)` — nombre exacto |
| Retorno | Entero entre `0` y `6` (columna donde jugar) |
| Límite de herramientas | Máximo **3 herramientas del kit** por agente |
| Jugada inválida | Jugar en columna llena = derrota automática |
| Formato del torneo | Round-robin: todos contra todos, una vez |
| Puntuación | Victoria = 3 pts · Empate = 1 pt · Derrota = 0 pts |

---

## Documentación

| Documento | Para qué sirve |
|---|---|
| [Guía de clase](docs/guia-de-clase.md) | Explicación completa del proyecto, el juego y las ideas de ML — **empieza aquí si es tu primera vez** |
| [Crear tu agente](docs/crear-agente.md) | Referencia técnica: parámetros, API del tablero, ejemplos de código |
| [Herramientas](docs/herramientas.md) | Las 5 herramientas disponibles, cómo usarlas y combinarlas |
| [Machine Learning](docs/machine-learning.md) | Minimax, Q-Learning, DQN y self-play aplicados a ConnectX |

---

## Recursos externos

- [Kaggle — ConnectX environment](https://www.kaggle.com/c/connectx) — competencia original con leaderboard global
- [Sutton & Barto — Reinforcement Learning: An Introduction](http://incompleteideas.net/book/the-book.html)
- [AlphaZero paper (DeepMind)](https://arxiv.org/abs/1712.01815)
- [Minimax con alpha-beta (Wikipedia)](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning)
