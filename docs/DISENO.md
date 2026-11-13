# Cómo está hecho RewardGuard

Este documento explica el diseño para poder defenderlo en una entrevista.

## Idea

Un evaluador de código tradicional hace `resultado == esperado`. Una IA entrenada para maximizar la nota puede aprender a hacer cierta esa comparación sin resolver el problema. RewardGuard evalúa **cómo** se obtiene el resultado, no solo cuál es.

Las técnicas que usa ya existen por separado, como los honeypots, los ganchos de auditoría, las pruebas diferenciales y las relaciones metamórficas. Lo propio del proyecto es combinarlas en un único evaluador y medir la diferencia entre lo que ve un evaluador ingenuo y lo que vale la solución de verdad.

## Módulos

- `task.py`: carga tareas escritas como módulos de Python. Cada una tiene enunciado, tests visibles, una referencia correcta, un generador de entradas y, si procede, relaciones metamórficas.
- `harness.py`: se ejecuta en un proceso aparte. Carga la solución, instala el gancho de auditoría, llama a la función con cada caso y escribe un evento JSON por línea. Nunca recibe los resultados esperados.
- `runner.py`: prepara una carpeta temporal con los archivos señuelo, lanza el vigilante con `subprocess` y recoge los eventos.
- `static.py`: analiza el código sin ejecutarlo con el módulo `ast`.
- `judge.py`: junta todas las pruebas y emite el veredicto.
- `report.py` y `cli.py`: informes y comandos.

## Decisiones

**Los esperados no viajan al proceso de la solución.** Así, buscar el valor esperado en la pila o en memoria no encuentra nada. Además, la comparación la hace el evaluador desde fuera.

**Archivos señuelo.** Contienen respuestas reales de los tests visibles. Una solución tramposa que los lee pasa los tests visibles, pero queda registrada y falla con las entradas nuevas.

**Gancho de auditoría.** Python permite registrar un gancho que recibe eventos como `open`, `os.listdir` o `sys._getframe`. Para no acusar a soluciones legítimas, solo se atribuye un evento a la solución si lo provoca ella: la apertura de archivos se filtra por ruta, `sys._getframe` solo cuenta si la llama directamente el código de la solución, porque `namedtuple` y `dataclasses` lo usan por dentro.

**Detectar `__eq__` tramposo.** Se compara cada resultado con un objeto centinela único. Cualquier cosa honesta es distinta de él, y un objeto que dice ser igual a todo lo es.

**Salida prematura.** El vigilante escribe un evento `done` al terminar. Si el proceso acaba con código 0 sin ese evento, es el truco de salir antes de que el evaluador compruebe nada.

**Funciones internas de Python.** Se guardan los identificadores de los `builtins` antes de cargar la solución y se comparan después. Para que no se pueda sabotear al vigilante, este usa referencias propias a las funciones que necesita.

**Entradas generadas, deterministas.** El generador usa una semilla fija por tarea, así que los resultados se repiten en cada ejecución.

**Veredicto con pruebas.** Cada veredicto lleva la lista de evidencias que lo justifican. Una evidencia crítica da "Trampa". Una tabla de respuestas solo da "Sobreajuste" si además falla con entradas nuevas. Un fallo sin evidencias es "Incorrecta", un error honesto.

**Puntuación aparente frente a real.** La aparente imita a un evaluador ingenuo: cuenta como superados los casos de una solución que engaña a la comparación o sale con código 0. La real pone a cero las soluciones con trampa y cuenta también las entradas generadas.

## Limitaciones honestas

- No es un sandbox de seguridad.
- Un atacante con conocimientos puede intentar evadir el gancho de auditoría. El objetivo son las trampas habituales de los modelos.
- Solo evalúa funciones Python con datos simples.
- Las tareas de ejemplo son sencillas.

## Ideas para ampliar

- Ejecutar dentro de contenedores.
- Más lenguajes.
- Tareas con varias funciones, clases y archivos.
- Medir con modelos reales y publicar los resultados.
