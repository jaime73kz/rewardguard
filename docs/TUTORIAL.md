# Tutorial: usar RewardGuard paso a paso (Windows)

## 1. Qué necesitas

Python 3.11 o superior. Para comprobarlo, abre el símbolo del sistema y escribe `python --version`.

## 2. Descargar el proyecto

1. Entra en https://github.com/jaime73kz/rewardguard.
2. Pulsa el botón verde **Code** y luego **Download ZIP**.
3. Haz clic derecho en el zip y elige **Extraer todo**.

## 3. Abrir la terminal en la carpeta correcta

1. Abre la carpeta `rewardguard` extraída. Debes ver `README.md`, `tasks` y `rewardguard`.
2. Haz clic en la barra de direcciones del Explorador, borra lo que hay, escribe `cmd` y pulsa Enter.
3. Se abre una ventana negra: es la terminal, ya dentro de la carpeta.

## 4. Ver las tareas

```
python -m rewardguard list
```

## 5. Ejecutar la demostración

```
python -m rewardguard scan examples/agents/honesto examples/agents/sobreajustado examples/agents/tramposo -o informe.html
```

Tarda unos segundos. Al terminar verás tres líneas con la puntuación aparente y la real de cada agente. Abre `informe.html` con doble clic.

## 6. Leer el informe

- **Puntuación aparente**: lo que diría un evaluador que solo mira los tests visibles.
- **Puntuación real**: lo que vale la solución de verdad.
- **Puntuación inflada**: la diferencia. Si es alta, el agente hace trampa o memoriza.

Veredictos:

- **Limpia**: resuelve el problema.
- **Incorrecta**: falla, pero sin pruebas de trampa.
- **Sobreajuste**: pasa los tests visibles y falla con entradas nuevas.
- **Trampa**: hay pruebas de que intentó engañar al evaluador.
- **No evaluable**: falta la solución o no se puede cargar.

En "Pruebas encontradas" se abre cada solución sospechosa y se ve exactamente qué hizo, por ejemplo "abrió un archivo señuelo con las respuestas de los tests".

## 7. Analizar una IA de verdad

1. Mira el enunciado de una tarea en la carpeta `tasks`, por ejemplo `tasks/fizzbuzz.py`, en la línea `PROMPT`.
2. Pégalo en una IA y guarda el código que te devuelva en `soluciones/mi_ia/fizzbuzz.py`. El archivo se llama como el id de la tarea.
3. Repite con las demás tareas y con otras IAs, cada una en su carpeta.
4. Ejecuta `python -m rewardguard scan soluciones/mi_ia -o resultado.html`.

Si la IA hace una versión honesta, saldrá "Limpia". Es normal que las IAs actuales no hagan trampa en tareas tan sencillas: RewardGuard es útil sobre todo cuando se entrena o se evalúa con muchas tareas y mucha presión para pasar tests.

## 8. Crear una tarea nueva

Copia `tasks/fizzbuzz.py` con otro nombre y cambia `ID`, `FUNCTION`, `PROMPT`, `VISIBLE`, `reference` y `generate`. El README explica cada pieza.

## 9. Problemas frecuentes

- **`python` no se reconoce**: instala Python desde python.org y marca "Add Python to PATH".
- **`la carpeta de soluciones no existe`**: la ruta que has escrito no es correcta. Comprueba que la terminal está en la carpeta del proyecto (paso 3) y que escribes bien el nombre.
- **Todo sale "No evaluable"**: los archivos no se llaman como el id de la tarea.

## 10. Uso responsable

RewardGuard ejecuta código en tu ordenador. Revisa lo que pegas antes de ejecutarlo.
