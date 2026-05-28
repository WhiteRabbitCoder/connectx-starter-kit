# Guía de Clase — ConnectX: Agentes Inteligentes

> Este documento explica el proyecto completo de principio a fin: qué es el juego, cómo funciona el código, cómo crear tu agente y cómo esto se conecta con Machine Learning.  
> Léelo en orden la primera vez. Después úsalo como referencia.

---

## Parte 1 — El juego

### ¿Qué es ConnectX?

ConnectX es una versión programable de **Connect Four** (Cuatro en línea). Las reglas son las mismas que el juego de mesa:

- El tablero tiene **6 filas y 7 columnas**
- Dos jugadores se alternan tirando fichas hacia abajo en una columna
- Las fichas caen por gravedad y se apilan desde el fondo
- Gana el primero en conectar **4 fichas consecutivas** en horizontal, vertical o diagonal
- Si el tablero se llena sin ganador, es empate

La diferencia con el juego de mesa es que aquí no juegas tú: **escribes un programa que juega por ti**.

### El tablero

El tablero se muestra así en la terminal:

```
. . . . . . .
. . . . . . .
. . . . . . .
. . . . B . .
. . A . B . .
. A A . B . .
0 1 2 3 4 5 6
```

- `.` = celda vacía
- `A` = fichas del jugador 1
- `B` = fichas del jugador 2
- Los números de abajo son los índices de columna (0 a 6)

En este tablero, B gana si juega en la columna 4: habrá 4 fichas B en vertical (filas 2, 3, 4, 5 de la columna 4). A debería haber bloqueado antes.

### Cómo se representa el tablero en código

El tablero es una **lista plana de 42 enteros**. El valor de cada celda es:

- `0` — celda vacía
- `1` — ficha del jugador 1
- `2` — ficha del jugador 2

Para convertir entre posición (fila, columna) e índice de lista:

```
índice = fila * 7 + columna
```

El tablero tiene fila 0 arriba y fila 5 abajo (el fondo). Ejemplo:

```
Fila 0:  índices  0  1  2  3  4  5  6
Fila 1:  índices  7  8  9 10 11 12 13
...
Fila 5:  índices 35 36 37 38 39 40 41
```

Cuando sueltas una ficha en la columna 3, cae a la celda más baja disponible de esa columna. Si está vacía, cae hasta la fila 5 (índice 38). Si ya hay una ficha en la fila 5, cae en la fila 4 (índice 31), y así sucesivamente.

---

## Parte 2 — El código

### Cómo está organizado el proyecto

```
connectx-starter-kit/
├── agents/         ← los programas que juegan (tus agentes)
├── arena/          ← el motor del juego (tablero + herramientas)
├── scripts/        ← los comandos para jugar, ver partidas y torneos
└── docs/           ← esta documentación
```

### El motor: `arena/board.py`

`Board` es el objeto que representa el tablero. Lo puedes usar en tu agente para simular jugadas sin modificar el tablero real.

```python
from arena.board import Board

# Crear un tablero vacío
tablero = Board()

# Soltar una ficha del jugador 1 en la columna 3
tablero.drop_piece(3, 1)

# Ver qué columnas tienen espacio
tablero.valid_moves()   # → [0, 1, 2, 3, 4, 5, 6]

# ¿Ganó el jugador 1?
tablero.check_win(1)    # → False (aún no)

# Hacer una copia para simular sin afectar el original
copia = tablero.copy()
copia.drop_piece(3, 1)  # solo afecta a 'copia'
```

**Métodos disponibles:**

| Método | Qué hace |
|---|---|
| `drop_piece(col, mark)` | Suelta una ficha; retorna `False` si la columna está llena |
| `valid_moves()` | Lista de columnas donde aún se puede jugar |
| `check_win(mark)` | `True` si ese jugador ha ganado |
| `is_full()` | `True` si no quedan celdas vacías |
| `copy()` | Crea una copia independiente del tablero |

### Las herramientas: `arena/tools.py`

El kit incluye 5 funciones heurísticas listas para usar. Cada una analiza el tablero y sugiere una columna, o devuelve `None` si no tiene nada que aportar.

| Herramienta | Qué hace |
|---|---|
| `win_now` | Si puedo ganar en este turno, lo hago |
| `block_now` | Si el rival puede ganar en su próximo turno, lo bloqueo |
| `prefer_center` | Elige la columna válida más cercana al centro |
| `avoid_dead` | *(Sin implementar — punto de extensión)* |
| `random_valid` | Elige una columna válida al azar |

La función `apply_tools` las ejecuta en el orden que le des, y devuelve el resultado de la primera que no sea `None`:

```python
from arena.tools import apply_tools

# Primero intenta ganar, luego bloquear, luego ir al centro
apply_tools(obs_dict, cfg_dict, ["win_now", "block_now", "prefer_center"])
```

**Regla de la actividad: tu agente puede usar máximo 3 herramientas.**

### Tu agente: `agents/team_template.py`

Tu agente es una función llamada `my_agent`. El motor la llama una vez por turno y espera que retorne un número de columna (0–6).

```python
def my_agent(observation, configuration):
    # observation.board  → lista de 42 enteros (el tablero)
    # observation.mark   → tu número: 1 o 2
    # configuration.rows     → 6
    # configuration.columns  → 7
    # configuration.inarow   → 4

    return 3  # siempre juega en la columna 3 (ejemplo tonto)
```

Eso es todo lo que el motor necesita de ti.

---

## Parte 3 — Cómo crear tu agente

Hay tres niveles de complejidad. Empieza por el primero y avanza según quieras.

### Nivel 1: Agente aleatorio (punto de partida)

Elige cualquier columna válida al azar. Es el agente más simple posible.

```python
from random import choice

def my_agent(observation, configuration):
    validas = [c for c in range(configuration.columns) if observation.board[c] == 0]
    return choice(validas)
```

Las columnas válidas son aquellas cuya celda superior (`board[col]`) está vacía — ahí es donde caerá la próxima ficha.

### Nivel 2: Usar las herramientas del kit

Combina hasta 3 herramientas. El orden importa: las herramientas se ejecutan en secuencia y la primera que devuelva algo decide la jugada.

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

Este agente:
1. Gana si puede (`win_now`)
2. Bloquea si el rival está a punto de ganar (`block_now`)
3. Juega cerca del centro si ninguna de las anteriores aplica (`prefer_center`)

Es un agente sólido con solo 3 líneas de lógica real.

### Nivel 3: Lógica propia con Board

Puedes usar `Board` directamente para simular jugadas y tomar decisiones más sofisticadas. El patrón clave es **copiar el tablero antes de simular**:

```python
from arena.board import Board

def my_agent(observation, configuration):
    tablero = Board(
        configuration.rows,
        configuration.columns,
        configuration.inarow,
        list(observation.board)
    )
    mark = observation.mark
    rival = 3 - mark  # si soy 1, el rival es 2, y viceversa

    # ¿Puedo ganar ahora?
    for col in tablero.valid_moves():
        simulacion = tablero.copy()
        simulacion.drop_piece(col, mark)
        if simulacion.check_win(mark):
            return col

    # ¿El rival gana en su próximo turno?
    for col in tablero.valid_moves():
        simulacion = tablero.copy()
        simulacion.drop_piece(col, rival)
        if simulacion.check_win(rival):
            return col

    # Si no, ir al centro
    movimientos = tablero.valid_moves()
    return min(movimientos, key=lambda c: abs(c - 3))
```

Este es esencialmente el mismo comportamiento que las herramientas, pero escrito manualmente. A partir de aquí puedes añadir cualquier lógica adicional.

### El error más común

**Jugar en una columna llena** es derrota automática. Siempre asegúrate de que la columna que retornas está en `valid_moves()`.

```python
# MAL: puede intentar jugar en columna llena
return 3

# BIEN: siempre filtra las columnas disponibles
movimientos = tablero.valid_moves()
return min(movimientos, key=lambda c: abs(c - 3))
```

---

## Parte 4 — Estrategia

Antes de saltar a Machine Learning, hay mucho que puedes lograr pensando estratégicamente.

### ¿Por qué el centro es valioso?

La columna 3 (el centro) participa en más combinaciones ganadoras posibles que cualquier otra columna. Una ficha en el centro puede ser parte de una línea horizontal, vertical, y ambas diagonales. Una ficha en la esquina solo puede ser parte de menos combinaciones.

```
Número de líneas ganadoras que pasan por cada columna:
col:  0   1   2   3   4   5   6
     [3]  [6] [9] [12] [9] [6] [3]
```

### ¿Qué es una "amenaza doble"?

Una amenaza doble ocurre cuando tienes dos formas diferentes de ganar en el próximo turno. El rival solo puede bloquear una, y tú ganas con la otra.

```
. . . . . . .
. . . . . . .
. . . . . . .
. . . . . . .
. . A . A . .
. . A . A . .
```

Si A juega en la columna 2 y conecta 3 en la columna 2, Y también tiene 2 fichas en las columnas 2 y 4 formando dos secuencias, el rival no puede bloquear ambas.

Crear amenazas dobles es una habilidad avanzada: requiere pensar varios turnos adelante.

### ¿Qué significa pensar varios turnos adelante?

Cada vez que juegas, el tablero cambia y el rival tiene nuevas opciones. Una buena jugada no es solo la que parece mejor ahora, sino la que lleva a posiciones más favorables en el futuro.

Esto es exactamente lo que hace **Minimax**: explorar sistemáticamente el árbol de jugadas posibles.

---

## Parte 5 — Machine Learning

Hasta aquí todo era lógica determinista: si X, entonces Y. Machine Learning es diferente: **la estrategia se aprende de la experiencia**, no se programa a mano.

### ¿Por qué ConnectX es un buen entorno para aprender ML?

- Las reglas son simples y claras
- El resultado de cada partida es una señal inequívoca (ganaste / perdiste / empataste)
- Puedes generar miles de partidas automáticamente
- El tablero tiene dimensiones manejables (42 celdas)
- Puedes probar tus ideas en segundos con el torneo local

### La conexión con ML: del tablero a la decisión

En ML, el problema se formula así:

```
Estado → Modelo → Acción
```

En nuestro caso:
- **Estado**: el tablero (42 valores + tu ficha)
- **Acción**: columna donde jugar (0–6)
- **Modelo**: lo que quieres aprender

El modelo puede ser una tabla, una red neuronal, o cualquier función que mapee estados a acciones.

### Enfoque 1 — Minimax (búsqueda, no ML puro)

Minimax no aprende nada — es búsqueda exhaustiva. Pero es la base conceptual de muchos algoritmos modernos y produce agentes muy fuertes.

**La idea:** si asumo que yo siempre elijo la jugada que me favorece más, y el rival siempre elige la que me favorece menos, ¿cuál es mi mejor jugada ahora?

```
Mi turno (MAX):    elige la columna con mayor puntuación
Turno del rival (MIN): elige la columna con menor puntuación para mí
```

Esto se repite hasta cierta profundidad. En las hojas del árbol, una función **heurística** evalúa qué tan bueno es ese estado para mí.

```python
def minimax(tablero, profundidad, es_mi_turno, mark):
    rival = 3 - mark

    if tablero.check_win(mark):     return +1000   # gané
    if tablero.check_win(rival):    return -1000   # perdí
    if tablero.is_full():           return 0       # empate
    if profundidad == 0:            return heuristica(tablero, mark)

    if es_mi_turno:
        mejor = -float("inf")
        for col in tablero.valid_moves():
            copia = tablero.copy()
            copia.drop_piece(col, mark)
            mejor = max(mejor, minimax(copia, profundidad - 1, False, mark))
        return mejor
    else:
        peor = float("inf")
        for col in tablero.valid_moves():
            copia = tablero.copy()
            copia.drop_piece(col, rival)
            peor = min(peor, minimax(copia, profundidad - 1, True, mark))
        return peor
```

Con profundidad 4–6 y **poda alpha-beta** (que elimina ramas que no pueden cambiar el resultado), minimax produce agentes muy competitivos.

### Enfoque 2 — Aprendizaje por Refuerzo (RL)

En RL, el agente aprende jugando. Recibe una recompensa al final de cada partida y ajusta su comportamiento para maximizarla.

Los conceptos clave:

| Concepto | En ConnectX |
|---|---|
| **Estado (s)** | El tablero en un momento dado |
| **Acción (a)** | Columna elegida |
| **Recompensa (r)** | +1 si ganas, −1 si pierdes, 0 en otro caso |
| **Política (π)** | La función que decide qué columna jugar dado un estado |
| **Q(s, a)** | Estimación de cuánto vale tomar la acción `a` en el estado `s` |

El algoritmo **Q-Learning** aprende la tabla Q actualizando sus estimaciones con cada experiencia:

```
Q(s, a) ← Q(s, a) + α × [r + γ × max Q(s', a') − Q(s, a)]
```

- `α` (alpha) = tasa de aprendizaje: cuánto peso das a la nueva información
- `γ` (gamma) = factor de descuento: cuánto valoras las recompensas futuras vs las inmediatas
- `s'` = estado siguiente después de tomar la acción `a`

El problema: hay del orden de 4×10¹² estados posibles en ConnectX. Imposible guardar una tabla tan grande.

**Solución: una red neuronal que aproxime Q** — eso es lo que hace **DQN (Deep Q-Network)**.

### Enfoque 3 — Redes neuronales (DQN)

En lugar de una tabla, una red neuronal aprende a estimar `Q(estado, acción)` para las 7 columnas a la vez.

Primero necesitas convertir el tablero en un formato que la red pueda procesar. El truco es tratarlo como una imagen con 3 canales:

```python
import numpy as np

def tablero_a_tensor(board, mark):
    grid = np.array(board).reshape(6, 7)
    mis_fichas    = (grid == mark).astype(float)      # dónde estoy yo
    fichas_rival  = (grid == 3 - mark).astype(float)  # dónde está el rival
    celdas_vacias = (grid == 0).astype(float)          # dónde no hay nadie
    return np.stack([mis_fichas, fichas_rival, celdas_vacias])  # forma: (3, 6, 7)
```

Esto es análogo a una imagen RGB (rojo, verde, azul → canal 1, canal 2, canal 3). Eso permite usar **redes convolucionales (CNN)**, que son especialmente buenas detectando patrones espaciales — exactamente lo que necesitamos para detectar líneas y amenazas en el tablero.

La red recibe el tensor (3, 6, 7) y produce 7 números: la estimación de valor para cada columna. El agente elige la columna con mayor valor entre las válidas.

### Enfoque 4 — Self-play (como AlphaZero)

El método más potente. El agente aprende jugando contra versiones anteriores de sí mismo.

```
1. Versión 0: agente aleatorio
2. Juega miles de partidas contra sí mismo → genera datos
3. Entrena la red con esos datos → Versión 1
4. Versión 1 juega contra Versión 0 → si gana más del 55%, reemplaza
5. Repite con Versión 1 como base → Versión 2
6. ...indefinidamente
```

En cada generación, el agente se enfrenta a un oponente de exactamente su nivel: ni tan fácil que no aprenda nada, ni tan difícil que no pueda ganar. Esto produce un aprendizaje estable y sostenido.

AlphaZero (DeepMind, 2017) usó este enfoque para dominar ajedrez, shogi y Go — superando a los mejores programas especializados del mundo partiendo desde cero, sin conocimiento humano más allá de las reglas.

### Resumen: del más simple al más potente

| Enfoque | Aprende? | Dificultad | Potencial |
|---|---|---|---|
| Heurísticas manuales | No | Baja | Medio |
| Minimax (depth 4) | No | Media | Alto |
| Minimax + alpha-beta | No | Media | Muy alto |
| Q-Learning tabular | Sí | Alta | Limitado (tabla muy grande) |
| DQN (red neuronal) | Sí | Alta | Alto |
| Self-play + MCTS | Sí | Muy alta | Máximo |

Para esta actividad, llegar a un minimax funcional con heurística propia ya es un logro sólido. DQN y self-play son el horizonte para quienes quieran explorar más.

---

## Parte 6 — El torneo

### Cómo funciona

El torneo es **round-robin**: cada agente se enfrenta a todos los demás una vez. No hay eliminatorias.

```bash
python3 -m scripts.tournament
```

El script busca automáticamente todos los archivos `.py` en la carpeta `agents/` (excepto `__init__.py` y `team_template.py`) y los enfrenta entre sí.

### Sistema de puntuación

- Victoria: **3 puntos**
- Empate: **1 punto** para cada jugador
- Derrota: **0 puntos**

### Quién va primero

En cada enfrentamiento, el agente que aparece primero en orden alfabético juega como **jugador 1** (va primero). Esto es una ventaja real en Connect Four: quien va primero tiene más control del centro.

### Cómo prepararte para el torneo

1. **Prueba tu agente contra el baseline** — es el oponente de referencia
2. **Observa dónde pierde** — `watch_match` te muestra cada jugada
3. **Ajusta la estrategia** — añade lógica para los patrones donde falla
4. **Vuelve a probar** — el ciclo es rápido, cada partida dura segundos

---

## Parte 7 — Ideas para mejorar tu agente

Estas son rutas concretas, ordenadas de menos a más ambicioso:

### Mejorar el orden de las herramientas

El orden en `apply_tools` importa. Prueba `["block_now", "win_now", "prefer_center"]` vs `["win_now", "block_now", "prefer_center"]` y compara resultados en el torneo.

### Implementar `avoid_dead`

La herramienta `avoid_dead` existe en el código pero no está implementada (siempre devuelve `None`). Puedes completarla: evita columnas que, aunque válidas, no contribuyen a ninguna línea ganadora posible.

### Contar amenazas

En lugar de solo reaccionar (ganar o bloquear), proactivamente busca columnas que creen el mayor número de "ventanas" abiertas — grupos de 4 celdas que aún pueden llenarse con tus fichas.

### Minimax con profundidad 3–4

Implementa la función minimax del ejemplo en `docs/machine-learning.md`. Con profundidad 3 ya superas claramente a los agentes heurísticos. Con profundidad 4–5 y poda alpha-beta, es muy difícil de vencer.

### Red neuronal simple

Entrena un clasificador que prediga la columna correcta a partir del estado del tablero, usando partidas generadas por el torneo como datos de entrenamiento. Es un proyecto de ML completo en miniatura.

---

## Glosario rápido

| Término | Significado en este contexto |
|---|---|
| **Agente** | El programa que juega (tu función `my_agent`) |
| **Estado** | El tablero en un momento dado |
| **Acción** | La columna que elige el agente |
| **Política** | La estrategia: qué acción tomar en cada estado |
| **Heurística** | Una función que evalúa qué tan bueno es un estado sin explorar el árbol completo |
| **Herramienta** | Una función del kit que sugiere una jugada para un tipo de situación |
| **Round-robin** | Formato de torneo donde todos se enfrentan a todos |
| **Minimax** | Algoritmo de búsqueda que asume que ambos jugadores juegan de forma óptima |
| **RL** | Reinforcement Learning — aprendizaje por ensayo y error con recompensas |
| **DQN** | Deep Q-Network — Q-Learning aproximado con una red neuronal |
| **Self-play** | Entrenamiento donde el agente juega contra versiones anteriores de sí mismo |
