# Informe — v5.4.0: §4.4 director de chats y §4.5 workflows nativos

Todo lo que sigue se midió en esta máquina, en
`…/scratchpad/orq/` (fuera de cualquier proyecto real). No se tocó ni un fichero
del repo `keel-skill`, no se cambió ninguna versión, no se comiteó nada.

**Limitación del entorno, dicha primero.** El clasificador de auto-mode de esta
sesión bloqueó de forma intermitente el lanzamiento de subprocesos `claude`
(mismo comando denegado y permitido en llamadas consecutivas). Todo lo que sigue
salió adelante, pero un tercio de los intentos se perdieron en eso. Para otra
ronda conviene una regla de permiso explícita: `Bash(claude:*)` y
`Bash(osascript:*)`.

---

## 1. La sonda `--resume` — resultado y qué cambia

### Qué se probó

Cuatro casos, con sesiones reales y sus transcripciones en disco.

**Caso A — sesión objetivo en otro directorio.** `--resume <id>` desde
`…/orq/proj` contra una sesión cuyo `cwd` era `/Users/joseconti`:

```
No conversation found with session ID: 2b2b9dba-7285-42e8-bb63-29ff41a3fad2
```

`--resume` **resuelve por el slug del directorio actual**, no por id global. Una
sesión sólo puede reanudar sesiones de su propio `cwd`.

**Caso B — director vivo e inactivo (`status: idle`), mismo `cwd`.** Funciona: el
proceso que reanuda contesta `ACK` y la transcripción crece en línea recta, sin
ramas. Pero **la ventana del director no ve nada**: el mensaje entra en el
FICHERO, no en el proceso.

**Caso C — director en medio de un turno.** Es el caso que decide todo. Sesión A
escribiendo 2000 líneas (12:16:53 → 12:17:23); a los 20 s, en pleno turno, se
dispara el `--resume`. Ambos procesos terminan con éxito. La transcripción
resultante:

```
user       10:16:53  u=6f345bbc  p=
…
user       10:17:13  u=d19c0b4f  p=c2181f2f  | Continue from where you left off.
assistant  10:17:13  u=82afa642  p=d19c0b4f  | No response requested.
user       10:17:13  u=908af5ed  p=82afa642  | AVISO_MID_TURN…
assistant  10:17:16  u=f2624a5a  p=908af5ed  | RECIBIDO_MID
assistant  10:16:55  u=7b4a4d49  p=c2181f2f  |            <-- rama de A
assistant  10:17:23  u=b3b2902e  p=7b4a4d49  | 1 2 3 4 …
```

Tres cosas a la vez: (1) el que reanuda **bifurca** — dos hijos del mismo
`c2181f2f`; (2) al encontrar un turno colgando **fabrica** un par
`Continue from where you left off.` / `No response requested.` que nadie
escribió; (3) los timestamps quedan desordenados.

**Caso D — ¿sobrevive el aviso?** Se reanuda otra vez la misma sesión y se le
pide citar el último mensaje de usuario:

```
Escribe los numeros del 1 al 2000, uno por linea, sin comentarios ni texto adicional.
```

El `AVISO_MID_TURN` **no está**. La rama del que llegó tarde quedó huérfana: el
aviso no es que no se entregue, es que **desaparece en silencio** del historial
reanudable.

### Veredicto de la sonda

`claude --resume` **no entrega un turno en una sesión viva. No existe buzón.**
Arranca un proceso nuevo que lee la transcripción de disco y escribe en el mismo
fichero. Contra un director vivo el resultado es, según el momento: sin efecto
visible (inactivo) o pérdida silenciosa del mensaje más una transcripción
bifurcada con turnos inventados (en vuelo).

**Qué cambia:** la hipótesis "el worker avisa al director" queda **muerta**. El
director necesita bucle de vigilancia, que es exactamente el tercer coste que
el informe de v5.3.0 identificó. Nada se abarata.

**Qué sí encontramos en su lugar, y es mejor que lo que se buscaba:**

```
$ claude agents --json
[ { "pid": 86997,
    "cwd": "…/scratchpad/orq/proj",
    "kind": "interactive",
    "startedAt": 1785406693846,
    "sessionId": "55555555-5555-4555-8555-555555555555",
    "name": "DIRLIVE",
    "status": "idle" }, … ]
```

Un **registro nativo de sesiones vivas** con pid, cwd, tipo, id, nombre y estado
(`idle`/ocupado). No requiere TTY, es scriptable, y resuelve de golpe: descubrir
sesiones, detectar una sesión muerta, y saber si una está ocupada. Sustituye el
parseo de `*.jsonl` que el informe anterior daba por necesario.

Dos avisos medidos: las sesiones `-p` (print) **no aparecen** en ese registro —
sólo interactivas y `--bg`; y `--session-id <uuid>` permite **asignar** el id de
antemano, así que el que lanza ya conoce el id del lanzado sin buscarlo.

### Fichero de señal vs. aviso

La pregunta del enunciado — cuál de los dos se cree el director — tiene ahora
respuesta simple: **sólo el fichero**. El aviso no existe como mecanismo. El
`printf > tmp && mv` atómico funcionó en las tres rodajas del prototipo, y es
la única autoridad sobre "terminó".

---

## 2. El problema difícil: N × `PROGRESS.md`

Medido con git puro, sin agentes.

### Hipótesis 3 (mía, no estaba en el enunciado): `merge=union`. **Muerta.**

Con `docs/PROGRESS.md merge=union` en `.gitattributes` y dos ramas que sólo
AÑADEN líneas, el merge sale limpio y correcto. Pero un `PROGRESS.md` de Keel no
se añade: se reescribe (fase actual, versión, posición). Con dos ramas que
reescriben esas líneas:

```
**Fase actual:** 4 — QA
**Version:** 0.2.0

## Log
- init
- slice A hecho
**Fase actual:** 3 — Construccion     <-- duplicado, valor contradictorio
**Version:** 0.1.1
## Log                                 <-- segunda cabecera
- slice B hecho
```

Merge **sin conflicto** y fichero **corrupto**: dos "Fase actual" que se
contradicen y ningún marcador que avise. Peor que un conflicto. Descartada.

### Sin `.gitattributes`: el conflicto es inevitable y siempre en el mismo sitio

Tres worktrees, tres ramas, cada worker toca su fichero de código y su
`PROGRESS.md`:

```
Auto-merging docs/PROGRESS.md
CONFLICT (content): Merge conflict in docs/PROGRESS.md
Automatic merge failed
--- status ---
A  b.txt
UU docs/PROGRESS.md
```

El **código fusiona limpio**. El único conflicto, en el 100 % de los merges y con
N workers N−1 veces, es `PROGRESS.md`. Con el `PROGRESS.md` estructurado real el
conflicto no es de una línea: es el bloque entero.

### Hipótesis 1 confirmada: los workers no escriben `PROGRESS.md`

Tres worktrees, cada worker escribe sólo su parte en
`docs/.keel/slices/<n>.json` — rutas distintas, nunca la misma:

```
-- merge ta:  create mode 100644 docs/.keel/slices/a.json
-- merge tb:  create mode 100644 docs/.keel/slices/b.json
-- merge tc:  create mode 100644 docs/.keel/slices/c.json
=== estado ===        (git status --porcelain: vacío)
PROGRESS intacto:
**Fase actual:** 3 — Construccion
```

**Tres merges, cero conflictos.** Y en el prototipo real con director esto se
repitió: fusionó dos ramas y reescribió `PROGRESS.md` él mismo, sin un solo
conflicto.

**Qué escribe el worker en su lugar:** un `docs/.keel/slices/<n>.json`
comiteado en su propia rama (`slice`, `status`, `branch`, `commit`,
`needs_user`). No stdout — `claude -p` no escribe nada hasta el final y un worker
muerto deja el log vacío (medido: `w1.log`, `w2.log`, 0 líneas mientras
trabajaban). No la transcripción — es del proceso, no del proyecto, y ya vimos
que se le inventan turnos.

Esto **invierte una regla de Keel** y necesita registrarse como decisión
deliberada: *el estado vivo lo escribe una sola sesión, la que posee el árbol
principal; un worker en un worktree escribe un parte, nunca el estado.*

### Hipótesis 2 confirmada: los workers no consumen prompts de continuación

El director del prototipo escribió sus propios prompts de rodaja, completos y
autosuficientes, empezando por la ruta absoluta del worktree:

```
Trabajas EXCLUSIVAMENTE en el worktree absoluto:
…/scratchpad/orq/w1
No toques ningun otro directorio. No leas ni escribas docs/PROGRESS.md bajo ningun concepto.
TAREA: …
CIERRE OBLIGATORIO, en este orden exacto: …
```

Y hay una razón mecánica por la que la preocupación del §4.5 punto 2 no puede
surgir: `docs/continuation-prompt.md` está **en `.gitignore`**, así que un
worktree nuevo **no lo contiene**:

```
--- contenido docs/ en worktree ---
PROGRESS.md
--- continuation-prompt en el worktree? ---
NO
```

El que necesita hand-off es el DIRECTOR, no los workers.

---

## 3. La fórmula, tal como funcionó

Prototipo real: un director y tres workers en tres rodajas, de punta a punta.
Funcionó. Esto es lo que hizo, exactamente.

### Reparto de trabajo

| | Director (árbol principal, `main`) | Worker (su worktree, su rama) |
|---|---|---|
| Código | nunca | siempre |
| `docs/PROGRESS.md` | **sólo él**, tras cada merge | prohibido explícitamente en el prompt |
| Parte de estado | lo lee | escribe `docs/.keel/slices/<n>.json` y lo comitea |
| Señal de fin | la espera | `printf > .tmp && mv .tmp .done` |
| Merge | sólo él | nunca |
| Prompt de rodaja | lo escribe, completo | lo recibe, no lee ficheros de estado |
| Carril único | el de `main` | el de su propio worktree |

### Comandos

Despacho de una rodaja (lo hizo el director solo, a partir de `DIRECTOR.md`):

```bash
git worktree add -q ../w<N> -b slice-<N>
claude --session-id <uuid> --model sonnet -p --permission-mode bypassPermissions \
  "$(cat ../slice-<N>.prompt)" > ../w<N>.log 2>&1 &
```

Espera (una sola llamada Bash bloqueante, con techo — esto importa, ver §4):

```bash
until [ -f /tmp/orq-done/<N>.done ]; do sleep 5; done
```

Cierre obligatorio del worker, en el prompt, en este orden:

```
1. git add -A && git commit -m "slice <N>: …"
2. escribir docs/.keel/slices/<N>.json  {slice,status,branch,commit,needs_user}  y comitearlo
3. printf '<N> done\n' > /tmp/orq-done/<N>.tmp && mv /tmp/orq-done/<N>.tmp /tmp/orq-done/<N>.done
4. terminar
```

El orden no es decorativo: el commit va **antes** de la señal, así que una señal
existente implica trabajo comiteado, nunca al revés.

### Resultado del prototipo

```
b053787 director: fusiona rodajas 1 y 2, actualiza PROGRESS
8f41eb9 Merge branch 'slice-2'
bf378bc slice 2: parte
a333b6d slice 1: parte
bdebcf8 slice 1: suma.js + test
1649461 slice 2: resta.js + test
```

Dos ramas fusionadas, cero conflictos, `PROGRESS.md` reescrito por el director:

```
**Rodajas hechas:** 1 (suma), 2 (resta)
## Log
- rodaja 1: src/suma.js + test/suma.test.js — done, fusionada en main (bdebcf8)
- rodaja 2: src/resta.js + test/resta.test.js — done, fusionada en main (1649461)
```

### El modo de fallo que importa: el worker necesita al usuario

Rodaja 3: `divide(a, b)` sin especificar qué hace con `b = 0`. El worker no se lo
inventó:

```json
{"slice":"3","status":"blocked","branch":"slice-3","commit":"4416bf5",
 "needs_user":"¿Qué debe devolver o hacer divide(a, b) cuando b es 0? (lanzar excepción, devolver Infinity/NaN, devolver null, etc.)"}
```

Y el director hizo lo correcto sin que nadie se lo recordara en ese turno:

```
- Worker marcó `status:"blocked"` — no fusiono a `main`, tal como manda la regla.
- Rama `slice-3` y worktree `../w3` quedan sin tocar hasta que decidas.
- `docs/PROGRESS.md` actualizado y commiteado (737dd9c) con el bloqueo anotado.
- **Pregunta para ti**: ¿qué debe hacer `divide(a, b)` cuando `b` es 0 …?
```

**Esto es lo único que un subagente nativo no puede hacer**, y es la mejor
defensa del §4.4 que salió de la ronda: la pregunta llega a un sitio donde hay
una persona, y la respuesta vuelve al mismo hilo que ya sabe el resto.

### El carril único bajo worktrees

Los tres worktrees dan tres `--show-toplevel` distintos:

```
…/orq/proj      …/orq/wt-a      …/orq/wt-b
```

Luego **tres carriles distintos y no se serializan**. Y está bien: es lo que
`references/project-state.md` línea 328 ya dice ("two worktrees of one repository
are two legitimate lanes"). La medición lo confirma y no hay que cambiar nada.

Lo que sí hay que decir en voz alta: la unidad que necesita serialización no es
la rodaja, es el **merge**. Y como sólo el director fusiona, el carril de `main`
—el suyo— ya lo cubre. La fórmula es coherente con el lock existente sin
tocarlo.

**La contención sigue funcionando exactamente donde debe.** Un worktree comparte
root-commit y `HEAD` con el principal:

```
worktree: rootcommit a70719b…  HEAD adb13d8…
main:     rootcommit a70719b…  HEAD adb13d8…
```

`Repo:` y `Commit:` pasan los dos. Sólo la contención distingue, y distingue:

```
TOP =…/orq/wt-probe
REAL=…/orq/proj/docs/continuation-prompt.md
CONTENCION: FALLA -> VERDICT STOP (correcto)
```

---

## 4. El contexto del director — números

Medido en la transcripción real del director del prototipo, sumando
`input_tokens + cache_creation + cache_read` por llamada:

```
base (tras leer DIRECTOR.md)                        39.845
fin turno 1 — despacha 2 rodajas                    48.356   (+8.511)
fin turno 2 — 2 partes, 2 merges, PROGRESS, limpieza 55.590   (+4.987)
fin turno 3 — 1 rodaja + espera + bloqueo + escalado 62.630   (+7.040)
```

- **Despachar:** ~4.250 tokens por rodaja.
- **Cerrar** (parte + merge + `PROGRESS.md` + limpieza): ~2.500 por rodaja.
- **Ciclo completo: ~6.750–7.000 tokens de contexto por rodaja.**
- Una rodaja que se bloquea y hay que escalar: ~6.150 en un solo turno.

**Cuándo deja de poder dirigir.** Con ventana de 200 k y compactación en torno al
80 %, quedan ~160 k útiles. `(160.000 − 40.000) / 7.000 ≈ **17 rodajas**`.

Pero eso es un **suelo**, no una previsión: en el juguete el prompt de rodaja
pesaba 1,2 KB y el `PROGRESS.md` 7 líneas. En proyectos reales de este disco:

```
docs/PROGRESS.md            4.245 B (keel-docs-theme)
docs/PROGRESS.md           17.653 B (mcp-content-manager-for-wordpress)
docs/continuation-prompt.md 1.594–5.713 B
```

Un `PROGRESS.md` de 4–18 KB **leído y reescrito en cada rodaja** más un prompt de
rodaja del tamaño de un prompt de continuación multiplica el coste por 2–3.
Realista: **15–20 k por rodaja → 6 a 9 rodajas antes de degradar.** Con ventana
de 1 M, unas 50.

**Corrección a mi propio informe de v5.3.0.** Dije que el bucle de vigilancia era
lo que llenaría el contexto del director. **Es falso**, y el turno 3 lo demuestra:
un `until [ -f …done ]; do sleep 5; done` es UNA llamada Bash que devuelve UNA
línea, cueste 40 s o 15 min. Lo que llena el contexto es el `PROGRESS.md`, que se
lee y se reescribe entero en cada rodaja. El bucle era el sospechoso equivocado.

---

## 5. Cerrar ventanas de workers terminados — medido, y la recomendación es no

Todo con `osascript` y Terminal.app en esta máquina.

**Matar el hijo deja la ventana viva.** `kill -TERM` al proceso en primer plano:
el hijo muere, y la ventana sigue abierta con un `zsh` inactivo
(`name = "joseconti — -zsh"`). Confirmado.

**Cerrar la ventana mata al hijo, pero tarde y sin aviso.** Ventana con
`sleep 900`, `close (first window whose id is 8035)` a las 12:19:55:

```
12:19:55 t+5s:  VIVO ventanas=2
…
12:20:32 t+35s: VIVO ventanas=2
12:20:32 t+40s: MUERTO ventanas=1
```

**~40 s** entre pedir el cierre y que ocurra. En otra ronda de la misma prueba,
**~78 s**. `close` **no devuelve error y no confirma nada**: el director no puede
saber si la ventana se cerró sin sondear. Y `close window id N` falla para
acceder a pestañas (`No puede obtenerse tab 1 of window id 8010`, error −1728);
sólo `close (first window whose id is N)` funciona.

**El cierre es una muerte dura.** Ventana con tres traps instalados:

```
trap "echo GOT_TERM >> /tmp/sig.log" TERM
trap "echo GOT_HUP  >> /tmp/sig.log" HUP
trap "echo GOT_INT  >> /tmp/sig.log" INT
```

La ventana se cerró y **`/tmp/sig.log` nunca se creó**. Ningún handler corrió.
(Matiz honesto: zsh aplaza los traps hasta que termina el job en primer plano, así
que esto no prueba qué señal exacta llegó — pero sí prueba lo que importa: **no
hay gancho de limpieza en el que se pueda confiar**.)

**Qué deja atrás un worker muerto.** `SIGTERM` a un `claude -p` en pleno turno:
muere con TERM, y su transcripción queda con el turno de usuario **sin respuesta**.
Al reanudarla:

```
$ claude --resume 66666666-… -p "cita el último mensaje de usuario"
Dos mensajes de usuario antes de este. El último fue: "Continue from where you left off."
```

El coste real de matar un worker, dicho sin adornos: **se pierde la salida del
turno truncado y la historia reanudable gana un turno de usuario fabricado que
nadie escribió.** `--resume` existe, sí, pero no devuelve un historial fiel.

Y el carril: `references/project-state.md` especifica que el lock guarda PID y
hora de arranque "so a stale lock … is detectable rather than permanent" — no
especifica **liberación al salir**. Como el cierre de ventana no ejecuta ningún
handler, el worker **no puede** liberar su carril. Cerrar ventanas convierte el
lock huérfano de excepción en camino normal, tal como temía el enunciado.

### Recomendación

**No cerrar ventanas.** Ni opt-in. Tres razones, todas medidas: latencia de
40–78 s sin confirmación; muerte dura sin ganchos de limpieza, con un worker
posiblemente en mitad de un commit; y carril huérfano garantizado. Abrir una
ventana no pedida se puso detrás de la tarjeta del proyecto en v5.3.0; cerrarla
es más destructivo y la mecánica es peor.

Lo que sí es defendible, si algún día se quiere: **`kill -TERM` al `claude` del
worker cuando su done-signal ya existe** (el commit ya está hecho, por el orden
del cierre obligatorio) **y dejar la ventana abierta**. Eso libera la sesión sin
destruir nada y deja el rastro a la vista. Pero incluso eso necesita que el lock
se libere explícitamente, que hoy no se especifica.

---

## 6. Callejones sin salida

1. **El worker avisa al director con `--resume`.** Muerto, y es el resultado
   principal de la ronda. No hay buzón: `--resume` bifurca la transcripción,
   inventa un par de turnos y el aviso se pierde en silencio si el director
   estaba en vuelo. No volver a intentarlo.
2. **`--resume` por id global.** Muerto. Está acotado al slug del `cwd`, así que
   un worker en un worktree **no puede** reanudar al director aunque quisiera —
   distinto directorio, distinto slug.
3. **`.gitattributes` con `merge=union` para `PROGRESS.md`.** Muerto y peligroso:
   con un `PROGRESS.md` estructurado produce un merge limpio y un fichero
   corrupto, con dos "Fase actual" contradictorias y sin marcador de conflicto.
4. **Cerrar la ventana del worker desde el director.** Muerto en la práctica:
   40–78 s de latencia, sin confirmación, sin ganchos de limpieza.
5. **`claude agents --json` como detector de fin de worker.** Muerto para
   workers `-p`: las sesiones print **no aparecen** en el registro. Sirve para
   sesiones interactivas y `--bg`, no para el shape del prototipo.
6. **stdout del worker como parte.** Muerto: `claude -p` no escribe nada hasta el
   final, así que un worker en curso o muerto deja el log a 0 líneas y el
   director no puede distinguir "trabajando" de "muerto" mirando el log.
7. **El bucle de vigilancia como problema de contexto.** No era un callejón:
   era un miedo infundado. Ver §4.

---

## 7. §4.5 — workflows nativos

### 7.1 Se ejecutó un barrido de conformidad real

Un workflow de 5 agentes (4 barredores + 1 escritor) sobre
`/Users/joseconti/Documents/GitHub/keel-docs-theme` en **solo lectura**,
escribiendo el resultado en el scratch. 31 filas de la Tabla 1, salida
estructurada con `schema`:

```
agent_count 5 · agents_done 5 · agents_error 0 · subagent_tokens 147.529 · duration 110 s
{"filas":31,"escrito":"37","markdownLength":6795}
```

Calidad de la evidencia, sin retoque:

```
| `.claude/skills/keel/` | declined | Path absent (`find . -iname '.claude*'` → no results…);
  rejected in docs/decisions.md D-005: "CLAUDE.md + AGENTS.md lock block only; no embedded
  skill copy…" |
| `docs/threat-model.md` | present | exists, 3847 bytes, 48 lines; first line "# Threat model
  — keel-docs-theme". |
| `docs/05-test-points.md` | declined | declined per docs/decisions.md:87 … y :112 …
  ('disproportionate for a no-build static theme … Revisit if the theme gains runtime
  behavior') |
```

Total: 31 filas — present 15, missing 0, declined 8, n/a 8. Citas de `D-005`,
`D-008`, `D-011` correctas, `|` escapado bien, cero alucinaciones detectadas al
contrastar.

### 7.2 ¿Rellena el fichero sin post-procesado? Respuesta matizada, y es un sí

Tu precondición era: `schema` llena `docs/keel-conformance.md` **sin
post-procesado**. Lo que se midió:

- **Post-procesado por modelo: cero.** Las filas salen validadas contra el schema
  en la capa de la tool; ningún agente reescribe, resume ni reformatea nada.
- **Pero hacen falta dos piezas que no son "el schema":**
  1. Una **plantilla determinista en el script** (`rows.map(r => "| … |")`). Son
     seis líneas de JavaScript, sin modelo, reproducibles. Eso es código, no
     post-procesado — pero hay que escribirlo.
  2. **Un agente para escribir el fichero**, porque el script de workflow **no
     tiene acceso a disco**. Aquí se resolvió con un agente `write:` al que se le
     pasa el markdown ya montado y se le prohíbe cambiar una palabra (devolvió 37
     líneas, coincidiendo con el markdown generado). La alternativa más limpia es
     que el workflow **devuelva** el markdown y lo escriba la sesión principal
     con Write, sin gastar un agente.

Conclusión operativa: **la precondición se cumple**, con la corrección de que
"sin post-procesado" significa "sin un modelo entre los datos y el fichero", no
"sin código".

### 7.3 El fallo metodológico que apareció, y hay que escribirlo en la skill

Los agentes **citaron el `docs/keel-conformance.md` que ya existía en el
proyecto** como evidencia de sus propios veredictos:

```
| `docs/00-competitive-landscape.md` | declined | File absent (test -f fails);
  docs/keel-conformance.md:19 records declined citing D-011 … |
```

Un barrido de conformidad que lee el barrido anterior es **autoconfirmatorio**: si
la fila anterior estaba mal, se reproduce el error con aire de evidencia. El
prompt del barrido tiene que **prohibir explícitamente leer
`docs/keel-conformance.md`**; los únicos autorizados son el disco, `MANIFEST.md`
y `docs/decisions.md`. Esto vale igual para el barrido inline: no es un problema
de los workflows, lo destapó el workflow.

### 7.4 `isolation: 'worktree'` y la contención

- **Un agente de workflow nunca lee su propio `docs/continuation-prompt.md`**,
  porque el fichero está en `.gitignore` y por tanto **no existe** en un worktree
  nuevo (medido, §2). No hay conflicto que gestionar.
- Si se le pasa la **ruta absoluta** del hand-off del árbol principal, la
  contención **dispara correctamente** y devuelve `STOP` (medido, §3).
- **Lo que sí no cubre el primitivo:** `isolation: 'worktree'` aísla **ficheros**,
  no **entornos**. La regla de fan-out de Keel no protege contra colisiones de
  ficheros, protege contra dos verificadores EJECUTANTES compartiendo un puerto,
  una base de datos, una semilla, un origen. Dos worktrees no arreglan eso: dos
  `playground-qa` en dos worktreesse pelean por el mismo puerto igual. La regla
  "un solo ejecutante por entorno" hay que seguir codificándola como **etapa
  serie**, y `isolation` no aporta nada ahí.
- No verificado: que la tool cree efectivamente un worktree de git con
  `--show-toplevel` distinto. No se probó **a propósito**: el único repo git a
  mano era `keel-skill` y crear un worktree escribe en su `.git/`, lo que rompe
  la regla 1. La semántica de git por debajo sí está verificada; la de la tool
  queda **sin verificar**.

### 7.5 Disponibilidad — Keel no puede depender de la tool

Confirmado en el contrato de la propia tool en esta sesión: **requiere opt-in
explícito del usuario** (la palabra clave en el prompt, un ajuste de sesión, o
que el usuario lo pida con sus palabras) y **puede no existir** en el entorno. Hay
además un **límite de tamaño configurable** por el usuario (en esta sesión,
"mantén los workflows por debajo de 15 agentes") que Keel no controla.

Luego la situación es **idéntica** a la de los subagentes, y el fallback ya está
escrito: `references/assistant-config.md` cierra con *"Where the environment
provides no subagents … the checks run inline and therefore serially. That is a
property of the environment, not a licence to drop any of them: record it exactly
as the standing fallback already requires."* El fallback de los workflows es la
misma frase, con un escalón intermedio:

**workflow (si hay opt-in) → bloque paralelo de subagentes (si hay subagentes) →
inline y en serie.** Los tres producen la misma tabla; sólo cambia el reloj de
pared. Y ninguno se salta un chequeo.

### 7.6 Qué encaja y qué no

**Encaja limpio, se vuelve código determinista:**

- El **barrido de conformidad v5.0.0**: las filas de la Tabla 1 y las acciones de
  la Tabla 3 son una lista enumerable — el caso canónico de "un verificador sobre
  muchas unidades independientes". Es el mejor candidato y ya está probado.
- El resto de las unidades que la regla ya enumera: **pantallas** del recorrido de
  fidelidad de Fase 4 (sobre capturas, no sobre navegador), **locales** de
  `guide-qa`, **dimensiones** de la auditoría de adopción, **dominios de rúbrica**
  de §6a, **competidores** del escaneo de Fase 1.
- **El merge/dedup de hallazgos.** "Merging is the main session's job" pasa de ser
  disciplina a ser `dedupeByFileAndLine(...)` en el script: determinista, no
  omitible, y sin gastar un modelo en deduplicar.
- **El tope de concurrencia** ("the environment caps concurrency") es nativo:
  `min(16, cores − 2)`, sin nada que escribir.
- **La regla del check global** ("a per-unit split never silently drops the
  cross-unit checks") se vuelve un agente extra explícito en el script, visible en
  el código en vez de confiado a la memoria.

**No encaja, sigue siendo juicio:**

- **Qué verificadores pide una puerta.** Seis de los nueve agentes son
  condicionales; depende de lo que el proyecto tenga. Eso se decide leyendo la
  tarjeta del proyecto, no se enumera en un script.
- **El reparto lector/ejecutante y "un solo ejecutante por entorno".** El script
  puede *implementarlo* como etapa serie, pero *decidir* qué agente ejecuta y qué
  entorno comparte es juicio, y `isolation` no ayuda (§7.4).
- **La excepción de `test-driver`.** "Corre primero y solo, *sólo en una ejecución
  en la que adapte algo*" depende del **resultado** de esa ejecución. Se puede
  modelar como dos etapas con una condición, pero la condición la evalúa el
  modelo.
- **El veredicto de la puerta.** Un workflow devuelve el conjunto fusionado;
  aprobar o no la puerta lo sigue haciendo la sesión.

### 7.7 ¿Se puede escribir ya en la skill?

**Sí, con una condición.** Lo que está probado y es escribible ahora:

- El barrido de conformidad como workflow, con el schema por filas y la plantilla
  determinista en el script.
- La cadena de fallback de tres escalones de §7.5.
- La prohibición de leer el `docs/keel-conformance.md` anterior (§7.3), que es un
  arreglo del barrido **en cualquier modalidad**.
- El dedup y el tope de concurrencia como código.

La condición: **no escribir nada sobre `isolation: 'worktree'`**, que es lo único
del §4.5 que sigue sin verificar y lo único que no hace falta — un barrido de
conformidad **sólo lee**, y no necesita aislamiento ninguno.

---

## 8. Veredicto sobre §4.4

**El director funciona.** Se construyó, corrió tres rodajas con tres workers,
fusionó sin conflictos, escribió el estado él solo y escaló una decisión de
producto al usuario sin inventársela. La fórmula existe y está en §3.

**Y aun así, mi recomendación es no meterlo en v5.4.0.**

Lo que se le objetaba se mantiene casi entero. Frente a subagentes y workflows
nativos, el director:

- **paga ~7 k de contexto por rodaja en un juguete y 15–20 k en un proyecto real
  → degrada entre la 6ª y la 9ª rodaja.** Un workflow no tiene ese techo: 31
  filas con 5 agentes y 147 k tokens, y el contexto del que orquesta no crece con
  el trabajo.
- **no tiene contabilidad de coste, ni cancelación, ni tope de concurrencia.** Los
  nativos sí, gratis.
- **necesita un bucle de espera y `bypassPermissions` en cada worker**, y en el
  camino de cierre de ventanas es peor que no hacer nada (§5).
- y todo su andamiaje —worktrees, señales atómicas, partes JSON, la inversión de
  la regla de `PROGRESS.md`— **es infraestructura nueva que Keel tendría que
  mantener** para conseguir paralelismo que ya tiene.

Su única baza sigue siendo exactamente la que decías: **un chat en el que hay una
persona.** Y esa baza es real — el bloqueo de la rodaja 3 lo demuestra: la
pregunta llegó a un hilo que ya sabía el resto y podía recibir la respuesta. Un
subagente nace, contesta y muere; no puede preguntar.

Pero esa baza **no necesita un director.** La consigue algo mucho más pequeño:
**una sesión de Keel normal que, en un solo turno, despacha N workers en
worktrees, espera sus señales y fusiona.** Es la misma fórmula de §3 sin el
personaje: el chat donde está la persona es el chat en el que ya trabajas, no un
segundo chat con un rol. Y así el techo de 6–9 rodajas desaparece, porque no hay
un director que acumule 40 rodajas de historia — hay un turno de fan-out por
sprint, como el que Keel ya describe en prosa.

**Recomendación concreta para v5.4.0:**

- **§4.4 como "director de chats": abandonar.** No se gana nada que justifique el
  andamiaje, y el número que lo mata es el techo de contexto.
- **Rescatar tres hallazgos de la ronda y quedárselos**, porque valen por sí
  mismos y no cuestan casi nada:
  1. La regla `PROGRESS.md`: **el estado vivo lo escribe la sesión que posee el
     árbol principal; un worker en un worktree escribe un parte
     `docs/.keel/slices/<n>.json`, nunca el estado.** Esto arregla un conflicto
     garantizado que hoy Keel no menciona, y aplica a cualquier trabajo en
     worktrees, con director o sin él.
  2. El **contrato de cierre del worker** (commit → parte → señal atómica, en ese
     orden), que es lo que hace que "existe la señal" implique "el trabajo está
     comiteado".
  3. **`claude agents --json`** como forma soportada de saber qué sesiones hay
     vivas, en qué directorio y si están ocupadas — con el aviso de que las
     sesiones `-p` no aparecen.
- **§4.5: escribir**, con las condiciones de §7.7.

Dicho de otro modo: el resultado negativo del §4.4 es el resultado útil de la
ronda, y la fórmula que se construyó para probarlo es lo que hay que conservar.

---

## 9. Lo que necesitaría Keel — propuesta, no aplicada

1. **Una decisión registrada que invierta la regla de `PROGRESS.md`** para trabajo
   en worktrees, con el texto del §8 punto 1 y el `docs/.keel/slices/<n>.json`
   como artefacto nuevo del MANIFEST (condicional: sólo si el proyecto hace
   fan-out con worktrees).
2. **`scripts/keel-handoff-verify` debe liberar el carril al salir**, y hoy no lo
   especifica: `references/project-state.md` sólo dice que un lock huérfano es
   *detectable*. Con worktrees y varios workers, el lock huérfano deja de ser
   excepción. Falta además la **política de recuperación**: qué se hace cuando el
   PID del lock ya no existe (¿se toma?, ¿se avisa?, ¿se pide OK?). Sin eso, el
   carril sólo funciona en el camino feliz.
3. **La cadena de fallback de tres escalones** (workflow → subagentes → inline y
   serie) en `references/assistant-config.md`, junto a la frase que ya está.
4. **La prohibición de leer el `docs/keel-conformance.md` anterior** en el barrido
   de conformidad, en cualquier modalidad. Es un arreglo, no una función nueva.
5. **Los prompts de rodaja son autosuficientes y no son prompts de continuación.**
   Si algún día se hace fan-out con worktrees, dejar dicho que el worker recibe un
   prompt completo con la ruta absoluta de SU worktree y no lee ningún fichero de
   estado — así el asunto de contención/worktree no llega a plantearse.
6. **Portabilidad de la gestión de ventanas: cerrar no.** Añadir a la nota de
   `start` que cerrar la ventana de otra sesión está medido en macOS y **no es
   fiable** (40–78 s sin confirmación, muerte dura sin ganchos), para que no se
   reproponga.

---

## Apéndice — qué queda en el scratch

```
…/scratchpad/orq/
  INFORME-v5.4.0.md      este informe
  DIRECTOR.md            las instrucciones que se le dieron al director
  slice-1.prompt         prompt de rodaja que el director escribió solo
  slice-2.prompt
  proj/                  repo de juguete: 3 rodajas, PROGRESS.md sin conflictos
  out/keel-conformance.md salida del workflow, 31 filas
```

Sesiones de prueba creadas (todas terminadas): `2b2b9dba`, `33333333`, `44444444`,
`55555555`, `66666666`, `77777777` (el director), más las de los tres workers.
Ninguna ventana de Terminal ni proceso `claude` de la prueba queda vivo.

