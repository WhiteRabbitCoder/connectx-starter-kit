# Machine Learning aplicado a ConnectX

ConnectX es un entorno ideal para aprender y experimentar con técnicas de inteligencia artificial porque:

- El espacio de estados es manejable (tablero 6×7)
- Las reglas son simples y deterministas
- El resultado (ganar/perder/empatar) es una señal de recompensa clara
- Puedes generar miles de partidas rápidamente con el torneo local

---

## El problema desde la perspectiva de ML

En cada turno, tu agente recibe un **estado** (el tablero) y debe elegir una **acción** (columna 0–6). El objetivo es aprender una **política** — una función que mapea estados a acciones — que maximice la probabilidad de ganar.

```
Estado (tablero 6×7) → Política → Acción (columna 0-6) → Nuevo estado + recompensa
```

---

## Nivel 1 — Minimax (búsqueda clásica)

Minimax es el punto de partida para cualquier juego de dos jugadores de suma cero. No es ML en sentido estricto, pero es la base conceptual de muchos algoritmos modernos.

### Idea

Construye un árbol de jugadas posibles. El agente asume que él siempre elige la jugada que **maximiza** su puntuación, y el rival siempre elige la que la **minimiza**. Evalúa las hojas del árbol con una función heurística.

```
                [estado actual]
               /       |        \
          [col 0]   [col 3]   [col 6]     ← mis jugadas (MAX)
         /    \
    [col 1] [col 4]                        ← jugadas del rival (MIN)
```

### Implementación básica

```python
from arena.board import Board

def minimax(board, depth, is_maximizing, mark):
    opponent = 1 if mark == 2 else 2

    if board.check_win(mark):     return +1000
    if board.check_win(opponent): return -1000
    if board.is_full():           return 0
    if depth == 0:                return heuristica(board, mark)

    moves = board.valid_moves()
    if is_maximizing:
        best = -float("inf")
        for col in moves:
            child = board.copy()
            child.drop_piece(col, mark)
            best = max(best, minimax(child, depth - 1, False, mark))
        return best
    else:
        best = float("inf")
        for col in moves:
            child = board.copy()
            child.drop_piece(col, opponent)
            best = min(best, minimax(child, depth - 1, True, mark))
        return best

def my_agent(observation, configuration):
    board = Board(configuration.rows, configuration.columns,
                  configuration.inarow, list(observation.board))
    mark = observation.mark
    best_col, best_score = board.valid_moves()[0], -float("inf")

    for col in board.valid_moves():
        child = board.copy()
        child.drop_piece(col, mark)
        score = minimax(child, depth=4, is_maximizing=False, mark=mark)
        if score > best_score:
            best_score, best_col = score, col

    return best_col
```

### Poda alpha-beta

Permite ignorar ramas que no pueden cambiar el resultado, reduciendo el tiempo de cómputo significativamente. Con profundidad 4 ya puedes tener un agente muy competitivo.

```python
def minimax_ab(board, depth, alpha, beta, is_maximizing, mark):
    # ... misma estructura, pero:
    if is_maximizing:
        for col in board.valid_moves():
            score = minimax_ab(child, depth-1, alpha, beta, False, mark)
            alpha = max(alpha, score)
            if alpha >= beta:
                break  # poda beta
    else:
        for col in board.valid_moves():
            score = minimax_ab(child, depth-1, alpha, beta, True, mark)
            beta = min(beta, score)
            if alpha >= beta:
                break  # poda alpha
```

---

## Nivel 2 — Aprendizaje por refuerzo (RL)

### Conceptos clave

| Concepto | En ConnectX |
|---|---|
| **Estado (s)** | El tablero actual: 42 valores + tu ficha |
| **Acción (a)** | Columna donde jugar: 0–6 |
| **Recompensa (r)** | `+1` si ganas, `-1` si pierdes, `0` en otro caso |
| **Política (π)** | La función `my_agent` que queremos aprender |
| **Valor (V)** | Cuán bueno es estar en un estado dado |
| **Q-valor (Q)** | Cuán buena es una acción desde un estado dado |

### Q-Learning

Aprende una tabla `Q[estado][acción]` con la ecuación de Bellman:

```
Q(s, a) ← Q(s, a) + α * [r + γ * max_a'(Q(s', a')) - Q(s, a)]
```

El problema: hay aproximadamente **4×10¹²** estados posibles. La tabla es imposible de almacenar directamente.

**Solución: usar una red neuronal para aproximar Q** → eso es DQN.

---

## Nivel 3 — Deep Q-Network (DQN)

En lugar de una tabla, una red neuronal aprende a predecir `Q(s, a)` para todos los valores de `a` a la vez.

### Representación del tablero como tensor

```python
import numpy as np

def board_to_tensor(board, mark):
    grid = np.array(board).reshape(6, 7)
    canal_propio   = (grid == mark).astype(float)      # mis fichas
    canal_rival    = (grid == 3 - mark).astype(float)  # fichas del rival
    canal_vacio    = (grid == 0).astype(float)          # celdas vacías
    return np.stack([canal_propio, canal_rival, canal_vacio])  # shape: (3, 6, 7)
```

Este formato de 3 canales es análogo a una imagen RGB, lo que permite usar **redes convolucionales (CNN)** que capturan patrones espaciales: líneas, amenazas, bloqueos.

### Arquitectura de red sugerida (PyTorch)

```python
import torch.nn as nn

class ConnectXNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1),  # (3, 6, 7) → (64, 6, 7)
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU(),
        )
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 6 * 7, 128),
            nn.ReLU(),
            nn.Linear(128, 7),  # Q-value para cada columna
        )

    def forward(self, x):
        return self.head(self.conv(x))
```

### Flujo de entrenamiento con DQN

```
1. El agente juega una partida contra un oponente
2. Cada (estado, acción, recompensa, estado_siguiente) se guarda en un replay buffer
3. En cada paso, se samplea un mini-batch del buffer
4. Se calculan los Q-valores objetivo:  r + γ * max(Q_target(s', a'))
5. Se actualiza la red con gradiente descendente
6. Cada N pasos, la red objetivo se actualiza con los pesos actuales
```

---

## Nivel 4 — Self-play y AlphaZero

El enfoque más potente para juegos de dos jugadores: el agente aprende jugando **contra versiones anteriores de sí mismo**.

### Idea central

1. Inicia con un agente aleatorio
2. Genera partidas de self-play
3. Entrena la red con los resultados
4. La nueva versión reemplaza a la anterior si gana más del 55% de partidas de evaluación
5. Repite indefinidamente

### Por qué funciona

Cada versión del agente es exactamente el oponente correcto para la versión actual: ni demasiado fácil ni imposible de vencer. El agente aprende a explotar sus propias debilidades y a defenderse de ellas.

### Componentes de AlphaZero

- **Red de política** (policy head): estima la probabilidad de cada acción
- **Red de valor** (value head): estima la probabilidad de ganar desde el estado actual
- **Monte Carlo Tree Search (MCTS)**: usa las estimaciones de la red para guiar la búsqueda del árbol

```
Red neuronal
├── Entrada: tablero como tensor (3, 6, 7)
├── Cuerpo: capas convolucionales compartidas
├── Policy head → distribución sobre las 7 columnas
└── Value head  → escalar en [-1, 1] (probabilidad de victoria)
```

---

## Cómo empezar experimentando

### Paso 1 — Genera datos

Usa el torneo local para generar partidas entre agentes existentes. Guarda cada par `(tablero, columna_jugada)` de las partidas ganadas.

```python
# En scripts/tournament.py puedes instrumentar play_single
# para registrar el historial de cada partida
```

### Paso 2 — Entrena un clasificador

Entrena una red que prediga la columna correcta dado el estado del tablero (aprendizaje supervisado con los datos de partidas):

```python
# Input:  tensor (3, 6, 7)
# Output: distribución sobre 7 columnas (CrossEntropyLoss)
```

### Paso 3 — Integra como agente

```python
import torch
import numpy as np

model = ConnectXNet()
model.load_state_dict(torch.load("mi_modelo.pt"))
model.eval()

def my_agent(observation, configuration):
    tensor = board_to_tensor(observation.board, observation.mark)
    x = torch.tensor(tensor, dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        q_values = model(x).squeeze()
    valid = [c for c in range(configuration.columns) if observation.board[c] == 0]
    q_valid = {c: q_values[c].item() for c in valid}
    return max(q_valid, key=q_valid.get)
```

### Paso 4 — Mejora con self-play o RL

Una vez que tienes la infraestructura base, puedes pasar a entrenamiento con RL usando frameworks como **Stable-Baselines3** o **RLlib**, o implementar self-play desde cero.

---

## Resumen de dificultad

| Enfoque | Dificultad | Potencial |
|---|---|---|
| Heurísticas manuales | Baja | Medio |
| Minimax depth 4 | Media | Alto |
| Minimax + alpha-beta | Media | Muy alto |
| DQN básico | Alta | Alto |
| Self-play + MCTS | Muy alta | Máximo |
