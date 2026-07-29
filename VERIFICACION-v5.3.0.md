# Verificación de Keel v5.3.0 — informe final

**Para Cowork.** Redactado en la máquina de José (macOS Darwin 25.6.0, Apple Silicon), con Claude Code CLI 2.1.107/2.1.220 y extensión VS Code 2.1.220.

**Este informe cubre dos versiones.** Las secciones 1-11 verifican **v5.3.0**, que fue commiteada (`8e862a3`), etiquetada y mergeada mientras se redactaba. La sección 12 registra los arreglos que Code aplicó dentro de ese commit. La **sección 13** cubre **v5.3.1**, que corrige dos defectos que llegaron a producción en 5.3.0 y que la sección 11 no había detectado.

**Estado del repositorio al cerrar:** `HEAD` en `f5783c5` (v5.2.0), los 7 ficheros de v5.3.0 modificados y sin commitear. No se editó ningún fichero de la skill, no se tocó la versión ni el changelog, no se commiteó, etiquetó ni empujó nada. Todos los repos de prueba se crearon en un directorio scratch fuera del proyecto y se destruyeron al terminar. Este fichero es el único añadido, está sin trackear y puede borrarse tras leerlo.

**Nota sobre numeración:** los rótulos `4.3` y `4.4` de las secciones finales son etiquetas de hoja de ruta pedidas por José. **No son versiones de Keel.** La política de versionado sigue intacta: nadie ha subido ni propuesto subir ningún número.

---

## Resumen ejecutivo

Los 15 defectos del primer informe están corregidos y la coherencia mecánica pasa 9 de 9. El arreglo del defecto A3 —ruta absoluta más campo `Repo:`— **funciona**, demostrado con tres escenarios sobre repositorios reales.

**No recomiendo commitear todavía.** Quedan tres fallos que se manifiestan en silencio, uno de ellos descubierto ejecutando el mecanismo de verdad y más grave que el A3 original:

1. **Concurrencia por auto-encadenado** (nuevo, GRAVE) — `Chaining: start` puede producir varias sesiones vivas sobre el mismo repositorio sin que nada lo impida ni lo detecte.
2. **Dos checkouts del mismo repo en el mismo commit** (GRAVE) — worktree, segundo clon o copia: los tres chequeos pasan y la sesión continúa el directorio equivocado.
3. **Clon superficial** (GRAVE) — `Repo:` se calcula mal, con `exit 0` y sin aviso.

Los tres tienen arreglo barato y verificado, descrito en la sección 7.

---

## 1. Coherencia mecánica — 9 de 9 PASS

| # | Comprobación | Resultado | Evidencia |
|---|---|---|---|
| a | 5.3.0 en cuatro sitios, `## 5.3.0` último del CHANGELOG | PASS | `SKILL.md:5`, `SKILL.md:11`, cabecera de `MANIFEST.md`, `grep "^## " \| tail -1` → `506:## 5.3.0` |
| b | Tabla 2 con seis filas v5.3.0 = los seis ficheros cambiados | PASS | `diff` del conjunto contra `git diff --name-only` sin CHANGELOG → `IDENTICAL SETS`. `CHANGELOG.md` correctamente en v5.2.0 |
| c | Tabla 3: una fila v5.3.0 tras v5.2.0; recuento en prosa = acciones listadas | PASS | Orden `v5.0.0/v5.1.0/v5.2.0/v5.3.0`; prosa `Five actions`, marcadores `(1)…(5)` |
| d | Sello del lock v5.3.0, ítems 1..6 sin huecos, ítem 5 coherente | PASS | `project-state.md:385`. Ítem 5 leído entero: enumera los seis campos, exige ruta absoluta y explica por qué el nombre idéntico es el peligro |
| e | Cero vocabulario retirado | PASS | `cli-print` 0, `cli-start` 0, `Chaining: print` 0, `Chaining: open` 0. `Chaining: vscode` un hit, en `CHANGELOG.md:535`, dentro de `### Fixed` — la excepción permitida |
| f | `TERM_PROGRAM=vscode` solo donde se documenta el error | PASS | Dos hits: `CHANGELOG.md:532` (Fixed) y `project-state.md:326` (nota del registro) |
| g | Lista de campos idéntica en toda enumeración | PASS | Cuatro enumeraciones, todas `Repo / Generated / Keel / Commit / Position / Handover`: plantilla en `project-state.md`, lock `:429`, `MANIFEST.md:138`, `CHANGELOG.md:513` |
| h | `docs/continuation-prompt.md` en las cuatro listas de `.gitignore` | PASS | `MANIFEST.md:37`, `phase-5-development.md:81`, `assistant-config.md:328` y `:344`, `phase-7-release.md:18` |
| i | Vallas markdown balanceadas, rutas resuelven | PASS | 0/0/0/14/2/2/18, todas pares |

Sin regresiones respecto al primer informe.

---

## 2. Regresión del defecto A3 — el arreglo es real

Dos repositorios con raíces distintas (`alpha` = `3b69a6e`, `beta` = `3d2541b`), cada uno con su cabecera de seis campos correcta para sí mismo.

**S1 — caso correcto** (cwd = alpha, ruta absoluta de alpha):

```
CHECK Repo:    cabecera=3b69a6e   real=3b69a6e   PASS
CHECK Commit:  cabecera=f2f7340   real=f2f7340   PASS
CHECK Generated: 2026-07-29T18:11:21+02:00 vs mtime …+0200
VERDICT: CONTINUAR
```

**S2 — A3 con el arreglo** (cwd = beta, ruta absoluta de alpha):

```
CHECK Repo:    cabecera=3b69a6e   real=3d2541b
      *** FAIL: el traspaso pertenece a OTRO repositorio ***
CHECK Commit:  cabecera=f2f7340   real=9dff9e8   FAIL: commit desconocido
VERDICT: STOP — traspaso de otro repositorio
```

**S3 — A3 sin ruta absoluta** (comportamiento anterior, ruta relativa desde beta):

```
fichero leído = docs/continuation-prompt.md
realpath      = …/beta/docs/continuation-prompt.md      <- el de BETA
CHECK Repo:    3d2541b = 3d2541b   PASS
CHECK Commit:  9dff9e8 = 9dff9e8   PASS
CHECK Generated: fresco             PASS
Position: … slice 2.4 of beta
VERDICT: CONTINUAR
```

**Veredicto:** las dos mitades hacen lo que la skill afirma, y el razonamiento de que ninguna basta sola queda confirmado empíricamente. S3 demuestra —no asevera— el fallo que la ruta absoluta previene.

---

## 3. Robustez de `Repo:`

**Repo normal (a):** estable. Mismo valor tras commit nuevo, en otra rama y en clon fresco.

**Sin remoto (c):** funciona. La razón por la que la spec eligió el commit raíz sobre la URL del remoto **se sostiene**.

**Dos commits raíz (b):** la spec es ambigua.

```
$ git rev-list --max-parents=0 HEAD
91ada0914f3212ad91287c2e1ef437443dd193bf
7d6ca1ce748486b74e5d0ca63e4de28292ba1b1b
```

Dos líneas. El orden es determinista (idéntico en cinco ejecuciones, en el clon y tras nuevos commits), pero la spec no dice cuál tomar, y `V=$(...)` produce un valor de 81 caracteres con un salto de línea dentro que nunca casará con una cabecera de 7.

**Clon superficial (d): gap serio y silencioso.**

```
$ git rev-parse --is-shallow-repository     → true
$ git rev-list --max-parents=0 HEAD         → 9de650b5…   exit=0
  raíz REAL del mismo repositorio           → 3b69a6e…
  >>> NO COINCIDE
```

Devuelve el commit injertado, con `exit 0` y sin aviso. Y el valor cambia al profundizar:

```
antes de --unshallow : 9de650b
después              : 3b69a6e
```

Consecuencias: un traspaso escrito en CI (`--depth 1`) lleva un `Repo:` que ningún clon completo acepta, y el mismo directorio rechaza su propio traspaso tras un `--unshallow`. Existe guarda: `git rev-parse --is-shallow-repository`.

---

## 4. La superficie sin medir

Claude Code en el **terminal integrado de VS Code** sigue **sin medir**. Había una shell viva (pid 99136, padre = ptyHost de VS Code) pero macOS (SIP) no expone el entorno de procesos ajenos, y no se inyectaron pulsaciones en el editor del usuario.

Marcadores sí medidos:

```
# Extensión de VS Code
CLAUDECODE=1
CLAUDE_CODE_ENTRYPOINT=claude-vscode
TERM_PROGRAM               <SIN DEFINIR>
VSCODE_PID, VSCODE_IPC_HOOK, VSCODE_CWD, VSCODE_ESM_ENTRYPOINT,
VSCODE_CRASH_REPORTER_PROCESS_TYPE=extensionHost, …

# Terminal standalone (Terminal.app)
CLAUDECODE=1
CLAUDE_CODE_ENTRYPOINT=sdk-cli
TERM_PROGRAM=Apple_Terminal
TERM_PROGRAM_VERSION=470.2
grep -c '^VSCODE' → 0
```

Evidencia de código (**no** medición en ejecución): VS Code 1.130.0 instalado sí escribe `TERM_PROGRAM=vscode` en sus scripts de integración de shell. Eso implica que el terminal integrado es una **tercera superficie** —tendría `TERM_PROGRAM=vscode` *y* `VSCODE_*`— que con el registro actual no casa ninguna de las dos filas de Claude Code, porque la fila standalone exige *"zero `VSCODE_*`"*. Cae a *print*: falla seguro, pero es una superficie sin fila.

**El valor de `CLAUDE_CODE_ENTRYPOINT` allí es desconocido y no se infiere.** Para cerrarlo basta ejecutar, en esa shell:

```
env | sort | grep -E 'TERM_PROGRAM|CLAUDECODE|CLAUDE_CODE_ENTRYPOINT|^VSCODE'
```

> **CERRADO.** José ejecutó esa medición a petición de Cowork antes del commit de v5.3.0, y el resultado está incorporado en el registro (`project-state.md:395`). Code no presenció la ejecución; se registra aquí como medición del usuario en la máquina real, que es lo que la propia regla de la skill exige. El resultado **invierte la suposición del primer borrador**: el terminal integrado reporta `CLAUDE_CODE_ENTRYPOINT=cli` **con** `TERM_PROGRAM=vscode`, mientras que la extensión reporta `claude-vscode` **sin** `TERM_PROGRAM` — o sea que `TERM_PROGRAM=vscode` identifica el PANEL de terminal, no la extensión. Y `VSCODE_*` resultan ser dos familias disjuntas: `VSCODE_PID` / `VSCODE_IPC_HOOK` / `VSCODE_ESM_ENTRYPOINT` en el extension host, `VSCODE_GIT_ASKPASS_*` / `VSCODE_INJECTION` en el terminal integrado.
>
> Con eso, la regla del registro pasó a ser asimétrica y más robusta que la que este informe proponía: **`claude-vscode` es el único valor que se casa por nombre**, porque es el único cuyo COMPORTAMIENTO difiere (pre-rellena y no envía); todo lo demás con `CLAUDECODE=1` es la CLI. Eso resuelve el punto 11 de la sección 9 mejor que añadir una tercera fila, porque aguanta un `entrypoint` futuro que nadie ha visto.

---

## 5. El contrato de `scripts/keel-continue` — seis huecos

Se escribió un prototipo desechable en scratch implementando los seis puntos literalmente. Los puntos 1, 3, 5 y 6 se satisfacen. Los huecos:

1. **El punto 2 contradice una regla UNBREAKABLE.** El punto 2 dice rechazar e imprimir *por qué* ante un `Handover:` no `clean`. Pero `project-state.md` dice: *"Whenever a chat cannot be opened, for ANY reason … the full prompt is printed."* Un traspaso bloqueado es una razón. ¿Se imprime el prompt o no? Un implementador tiene que inventarlo.

2. **"Degradar, nunca subir" no es expresable** cuando la fila de la herramienta tiene un solo tier. La fila CLI solo sabe `start`; si la tarjeta pide `prefill`, degradar no produce ninguna acción ejecutable y hay que caer a imprimir. El contrato no lo dice.

3. **Sin especificar:** codificación del prompt para la URI (el prototipo tuvo que usar percent-encoding vía `python3`, dependencia que nadie pidió), qué significa *"clipboard where available"*, y qué hacer con una cabecera malformada.

4. **El chequeo `Generated:` vs mtime se llama mecánico pero no lo es tal como está escrito.** Medido en dos sesiones reales: cabecera `2026-07-29T18:25:08+02:00` contra mtime `2026-07-29T18:25:08+0200`. Los modelos lo resolvieron razonando que es el mismo huso; **un script que compare cadenas da falso positivo de traspaso manipulado en cada ejecución.** Hay que normalizar a epoch.

5. **Los "platform open commands" del contrato sirven para disparar una URI, no para abrir una sesión de CLI visible.** Verificado solo en macOS, vía `osascript` con Terminal.app. Linux (`gnome-terminal`/`konsole`/`xterm`) y Windows: **no verificado**. Sin esto, un implementador entrega sin darse cuenta la variante headless —que funciona, pero no abre ningún chat—, y el usuario cree que hay una sesión esperándole cuando no la hay.

6. **Los chequeos deben ejecutarse como comandos simples e independientes, y nadie lo dice.** Ver sección 4.3: es la diferencia entre automatización real y una puerta de permisos en cada eslabón.

---

## 6. Fallos silenciosos, por gravedad

### 6.1 (GRAVE, nuevo) Concurrencia por auto-encadenado

Descubierto ejecutando el mecanismo, no analizándolo. Al montar una prueba de cadena de tres chats con tope, dos sesiones lanzadas quedaron en vuelo mientras se reiniciaba el contador; al arrancar, encontraron el contador a cero y empezaron una cadena nueva. Registro real:

```
- chat 1 de 3 — 19:31:37 — pid 10741
- chat 2 de 3 — 19:31:39 — pid 11351
- chat 3 de 3 — 19:31:52 — pid 12384
- CADENA TERMINADA en el chat 3
- chat 4 de 3 — 19:31:53 — pid 12434      <-- pasó del tope
- CADENA TERMINADA en el chat 4
```

Cuatro sesiones vivas y cuatro ventanas en 16 segundos.

Tres propiedades del fallo:

- **El contador no ve las sesiones en vuelo.** Entre lanzar y ejecutar pasan segundos; en esa ventana el contador miente y el tope se salta por diseño.
- **El freno vive dentro de lo que frena.** Contador y tope en el mismo repositorio que la cadena modifica. Un `git checkout`, un `git clean`, un clon nuevo o una limpieza lo reinician.
- **Se le escapó a quien lo había escrito**, conociendo el diseño y el tope. Un usuario que active `start` sin haberlo escrito no tiene ninguna ventaja — y lo que la skill promete es que eso corra sin nadie mirando.

En un desarrollo real, dos sesiones vivas sobre el mismo repositorio producen commits intercalados en la misma rama, `docs/PROGRESS.md` pisado por la última, `docs/continuation-prompt.md` apuntando a un estado que ninguna dejó, y ediciones sobre lecturas que la otra acaba de invalidar. **Ninguno de los tres chequeos del courier se dispara**: mismo repo, mismo commit inicial, traspaso fresco.

**Corrección explícita del primer informe.** Este escenario se registró como `S-E`, severidad BAJA, con el argumento de que *"es la misma clase de riesgo que dos sesiones editando PROGRESS.md, que Keel ya asume"*. Esa valoración era válida asumiendo que las sesiones concurrentes las abre una persona. Con `start`, **el mecanismo las crea solo**: la concurrencia deja de ser un accidente del usuario y pasa a ser una consecuencia del diseño. Sube a GRAVE.

### 6.2 (GRAVE) Dos checkouts del mismo repositorio en el mismo commit

Copia de un repo en otra ruta, mismo HEAD, con trabajo sin commitear distinto y su propio traspaso:

```
raíz : original=3b69a6e   gemela=3b69a6e
HEAD : original=9de650b   gemela=9de650b

--- sesión en el ORIGINAL lee el traspaso de LA GEMELA ---
CHECK Repo:    PASS
CHECK Commit:  PASS
CHECK Generated: PASS
VERDICT: CONTINUAR
```

Con un **worktree** en el mismo commit, resultado idéntico. Ningún chequeo salta.

Es A3 en forma más estrecha pero muy real: **`Repo:` identifica el repositorio, y A3 es un fallo de directorio de trabajo.** Worktrees, segundos clones, copias en Dropbox y checkouts paralelos comparten raíz por definición. Los worktrees no son exóticos: el propio harness de Claude Code los crea.

### 6.3 (GRAVE) Clon superficial

Ver sección 3d.

### 6.4 (MEDIO) Dos commits raíz

Ver sección 3b.

### 6.5 (MEDIO) Traspaso escrito con el árbol sucio

```
git status --porcelain →  M docs/PROGRESS.md
Commit: cabecera=9de650b   HEAD=9de650b
CHECK Repo: PASS · CHECK Commit: PASS · VERDICT: CONTINUAR
```

Ningún chequeo mira el árbol de trabajo. La sesión siguiente hereda cambios sin commitear que cree inexistentes. Es realista: quien escribe el traspaso es una sesión quedándose sin contexto, justo cuando es más probable dejar cosas a medias.

### 6.6 (BAJO, de diseño) `start` dispara antes de verificar

El desajuste se detecta, pero lo detecta la sesión **nueva**, después de arrancar. Con `prefill` media una persona; con `start` la sesión ya se lanzó y consumió contexto cuando descubre que debe parar. `keel-continue` debería verificar antes de disparar, y su contrato no lo pide.

### No es problema: submódulos

```
raíz padre     : 784ac29
raíz submódulo : 3d2541b
show-toplevel desde dentro del submódulo → …/padre/sub
```

Raíces distintas y `--show-toplevel` correcto. `Repo:` los distingue.

---

## 7. La solución propuesta: que verifique un script, no el modelo

Un solo cambio arquitectónico que colapsa seis huecos y dos fallos silenciosos.

**El problema de raíz.** Cuando la sesión compone los chequeos ella misma, escribe una línea con `$()` anidados. El analizador que casa comandos contra la lista blanca no sabe descomponerla, devuelve `Parse error`, y **la lista blanca no sirve de nada aunque `git rev-parse` esté en ella**. Verificado dos veces en sesiones reales.

**La solución.** Keel genera `scripts/keel-handoff-verify` junto a `keel-verify` y `keel-doctor`, y el traspaso instruye a ejecutarlo. Lista blanca completa del proyecto:

```json
{ "permissions": { "allow": ["Bash(./scripts/keel-handoff-verify:*)"] } }
```

**Una entrada.** Resultado real, sesión lanzada sin intervención:

```
CHECK containment : OK        (… dentro de …/auto)
CHECK repo        : OK        f464823
CHECK commit      : OK        f464823
CHECK generated   : OK        desvio 0s
CHECK handover    : clean
CHECK tree        : cabecera='dirty' real=3 ficheros
VERDICT: CONTINUE
```

Sin huecos de aprobación, medido en los tiempos entre eventos del transcrito (`Bash → tool_result` en 1,7s y 0,3s; una puerta habría dejado minutos). Ciclo completo en 20 segundos.

**Lo que arregla, todo verificado:**

| Escenario | Con los chequeos en prosa | Con el script |
|---|---|---|
| Gemela / worktree (6.2) | `CONTINUAR` ✗ | `containment : MISMATCH` → **STOP** ✓ |
| Repositorio ajeno (S2) | STOP ✓ | STOP ✓ (por dos vías) |
| Clon superficial (6.3) | `Repo:` erróneo, exit 0 ✗ | `repo : UNAVAILABLE` ✓ |
| Dos raíces (6.4) | valor de 81 caracteres ✗ | `sort \| head -1` ✓ |
| `+02:00` vs `+0200` (hueco 4) | falso positivo ✗ | normalizado a epoch ✓ |
| `Parse error` en cada eslabón (hueco 6) | puerta en A, B y C ✗ | ninguna puerta ✓ |

Los tres escenarios de fallo probados contra el script: la gemela da `VERDICT: STOP`, el repositorio ajeno también, y el shallow se declara no fiable en lugar de mentir.

**Cambio en la skill:** una frase, no seis.

> Los tres chequeos del courier no los ejecuta la sesión componiendo comandos de git. Los ejecuta `scripts/keel-handoff-verify`, generado en el scaffold junto a `keel-verify` y `keel-doctor`, y el traspaso instruye a ejecutarlo. La lista blanca del proyecto lleva una sola entrada para él.

Eso convierte seis huecos en un artefacto con contrato propio — lo mismo que Keel ya hace con `keel-verify` y `keel-doctor`, y coherente con su propia frase: *"a check that cannot be run is a promise, and this skill does not write promises as checks."* Hoy los tres chequeos del courier son exactamente eso, una promesa.

El prototipo escrito hoy funciona pero es solo BSD/macOS (`stat -f`, `date -j`). Falta Linux y Windows.

---

## 8. Registro por herramienta

| Herramienta | Veredicto | Detalle |
|---|---|---|
| **Claude Code, extensión VS Code** | VERIFICADO | La URI `vscode://anthropic.claude-code/open?prompt=…` pre-rellena y **nunca envía**. Cuatro disparos, cero envíos. Prueba estructural del bundle instalado (2.1.220): el handler de `/open` lee exactamente `session` y `prompt`, y **no existe parámetro de envío ni de carpeta/workspace**, por lo que siempre aterriza en la ventana ACTIVA de VS Code |
| **Claude Code, terminal standalone** | VERIFICADO | `claude "<prompt>"` **envía automáticamente**. En CLI no existe el pre-rellenado esperando Enter. Hereda el `cwd`, luego no puede aterrizar en el repositorio equivocado |
| **Cursor** | DOCUMENTADO, SIN PROBAR | `cursor://anysphere.cursor-deeplink/prompt?text=…`. Doc oficial: *"opens Cursor with the prompt pre-filled… Deeplinks never trigger automatic execution"* (cursor.com/docs/integrations/deeplinks). No instalado; esquema no registrado en LaunchServices. Marcador de entorno: `CURSOR_TRACE_ID`/`CURSOR_AGENT` solo en foro de comunidad → **no verificado** |
| **Codex** | DOCUMENTADO, SIN PROBAR | `codex "PROMPT"` posicional documentado (learn.chatgpt.com/docs/developer-commands). La doc **no dice** si auto-envía o pre-rellena → no verificado. Ningún esquema URI. No instalado |
| **Gemini CLI** | DOCUMENTADO, SIN PROBAR | Instalado pero **inejecutable**: el login falla con *"This client is no longer supported for Gemini Code Assist for individuals… migrate to the Antigravity suite"*. Doc: `-p/--prompt` y el posicional son modo headless — ejecutan y salen, es enviar, no pre-rellenar. Ningún URI |
| **GitHub Copilot** | NO ENCONTRADO | Sin deeplink de chat ni argumento de prompt inicial en doc oficial |
| **Windsurf** | NO ENCONTRADO | Solo `windsurf://windsurf-mcp-registry?serverName=…`, para el registro MCP. No abre chat con prompt |

**Nota sobre la redacción actual.** `SKILL.md:252` y `project-state.md:304` dicen *"today only Claude Code has one recorded"*. Es cierto como afirmación sobre el registro de Keel y **falso como afirmación sobre el mundo**: Cursor documenta el mismo mecanismo con idéntica semántica. Por la regla propia de Keel es correcto que hoy no tenga fila; lo que hay que corregir es la frase. Propuesta: *"la única verificada hasta hoy"*.

---

## 4.3 — Automatización del traspaso: qué se puede y a qué precio

Etiqueta de hoja de ruta pedida por José para todo lo verificado hoy sobre encadenado automático.

### El mapa completo, todo medido

| Vía | Gestos del usuario | ¿Ventana visible? | ¿Repositorio correcto? |
|---|---|---|---|
| URI `vscode://` | 1 Enter | Sí | **No garantizado** — la ventana activa |
| CLI en terminal visible | **0** (tras autorizar la carpeta una vez) | **Sí** | Sí, por el `cwd` |
| CLI headless desde la sesión | **0** | **No** | Sí, por el `cwd` |
| `/clear` en el mismo chat | 2 (escribir `/clear`, pegar y Enter) | Sí (la misma) | Sí |

`/clear` está documentado en el binario instalado como *"Start a new session with empty context; previous session stays on disk (resumable with /resume)"*. Es la vía **más segura** —misma ventana, mismo repo, permisos ya concedidos, A3 imposible— y la **menos automatizable**: no existe herramienta para que una sesión vacíe su propio contexto. Merece una frase en `project-state.md`, porque hoy la skill habla siempre de *"the next chat"* y nunca del caso más frecuente: el chat sigue vivo pero el contexto está lleno.

### Los tres requisitos de la automatización real

`Chaining: start` **sí** entrega continuación desatendida, pero necesita tres cosas y hoy no está escrita ninguna:

1. **Lista blanca del proyecto** cubriendo la verificación del traspaso. Con la solución de la sección 7, una sola entrada.
2. **Confianza de carpeta**, concedida una vez por proyecto. Es persistente y no se repite. *(Añadir `.claude/settings.json` provoca este diálogo la primera vez, avisando de cuántos permisos pre-aprueba la carpeta — comportamiento correcto, pero conviene anticiparlo al usuario.)*
3. **Comandos simples e independientes.** Con `$()` anidados el analizador da `Parse error` y la lista blanca queda inservible **en cada eslabón de la cadena, no solo en el primero**. Verificado: A→B→C pregunta en los tres.

### La pregunta que debe hacerse al principio, y el aviso obligatorio

**Requisito de diseño explícito.** La pregunta del `Chaining:` no debe formularse como una preferencia de configuración enterrada en la tarjeta de proyecto. Debe hacerse **al inicio**, junto al resto de decisiones de arranque, y con esta forma:

> **¿Quieres que el desarrollo se encadene de forma automática entre chats?**
>
> - `off` (recomendado) — cada chat termina dejando el traspaso escrito y el prompt listo para copiar. Tú decides cuándo sigue.
> - `prefill` — el chat siguiente se abre con la instrucción ya escrita; tú pulsas Enter.
> - `start` — el chat siguiente se abre **y arranca solo**, sin que toques nada.
>
> **Si eliges `start`, esto ocurre en la CLI, no en el editor.** Es la única forma verificada de automatizar el ciclo completo: la URI de VS Code pre-rellena y no envía, y su manejador no acepta ningún parámetro que lo cambie. Elegir `start` significa que el desarrollo salta a sesiones de línea de comandos.
>
> **Y significa que el desarrollo avanzará sin nadie mirando.** Antes de elegirlo, decide si eso es aceptable en este proyecto.

Dos razones para que el aviso sea explícito y no una nota al pie:

- **Cambia la herramienta, no solo una opción.** Un usuario que trabaja en VS Code y elige `start` esperando que su editor haga algo se encuentra con ventanas de terminal. Eso hay que decirlo antes, no después.
- **Cambia quién supervisa.** `off` y `prefill` mantienen a una persona entre eslabón y eslabón. `start` la quita. Hoy esa persona es el único mecanismo que impide que la cadena se bifurque (sección 6.1).

### Recomendación

**`start` no debería ofrecerse hasta que exista el cerrojo de vía única.** Un cerrojo que comprueba la sesión **que llega**, no la que lanza —porque quien lanza no puede saber quién más está en vuelo, que es exactamente lo que falló hoy—, con el fichero de cerrojo **fuera del repositorio**, para que un `git clean` no borre el freno.

Mientras tanto, `off` por defecto y `prefill` como máximo disponible.

---

## 4.4 — Un chat director que orquesta sesiones de CLI (propuesta, NO verificado)

Etiqueta de hoja de ruta pedida por José. **Las piezas están verificadas; el conjunto no. No se construyó ni se probó ningún orquestador.**

### Piezas verificadas hoy

- **Lanzar una sesión desde otra**: `claude "<prompt>"` desde la herramienta Bash de un chat. Corrió entero y devolvió resultado por stdout.
- **Capturar su salida**: en headless (`< /dev/null`) el que lanza lee lo producido.
- **Leer el estado de cualquier sesión**: los transcritos viven en `~/.claude/projects/<slug>/*.jsonl` y son parseables. De ahí salieron los tiempos entre eventos que prueban la ausencia de puertas de permisos.
- **Lanzar sesiones visibles** que una persona pueda retomar, vía `osascript`.
- **Detectar si siguen vivas**, por PID.

### La objeción principal

**Ya existe nativamente y funciona mejor.** Claude Code ofrece subagentes y workflows, con contabilidad de coste, cancelación, límite de concurrencia y `isolation: "worktree"`. Lanzar procesos `claude` a mano reimplementa eso sin nada de ello.

Y choca con la sección 6.1: varios trabajadores sobre un mismo checkout es justo el escenario que se descontroló hoy. **Orquestación sin aislamiento no es orquestación, es una colisión programada.**

### Cuándo tendría sentido para Keel

La distinción útil:

- **Trabajo paralelo** (revisar N ficheros, auditar N dimensiones) → subagentes nativos. No hace falta nada de esto.
- **Chats de verdad que una persona pueda retomar** —el caso de Keel, donde cada sprint es una conversación— → ahí sí, porque un subagente no es un chat: nace, responde y muere, y nadie puede entrar en él.

Eso sugiere una figura que hoy no existe en Keel: un **chat director** que nunca toca código, solo mantiene `docs/PROGRESS.md`, decide la siguiente rebanada y despacha un chat de desarrollo por rebanada. Necesitaría tres cosas ausentes hoy:

1. **Un worktree por trabajador**, no un checkout compartido.
2. **El cerrojo de vía única** de la sección 4.3.
3. **Que el director no desarrolle**, o se le llena el contexto vigilando y deja de dirigir.

---

## 4.5 — Workflows nativos para las fases de abanico (propuesta, NO verificado en esta sesión)

Etiqueta de hoja de ruta pedida por José. **No se ejecutó ningún workflow durante esta verificación.** Lo que sigue describe el mecanismo tal como lo expone el harness de Claude Code y por qué encaja con Keel; nada de ello se probó aquí y no debe darse por verificado.

### Qué es

Claude Code expone una herramienta `Workflow`: un script en JavaScript que orquesta subagentes de forma **determinista**, con control de flujo real —bucles, condicionales, abanicos— en lugar de dejar la orquestación al criterio del modelo. Las primitivas relevantes:

- `agent(prompt, opts)` — lanza un subagente. Con `schema` (un JSON Schema) devuelve un objeto validado en vez de texto, así que el resultado es consumible por código y no hay que parsear prosa.
- `parallel(thunks)` — concurrencia con barrera: espera a todos.
- `pipeline(items, ...stages)` — cada elemento recorre todas las etapas por su cuenta, **sin barrera entre ellas**. El coste en tiempo es la cadena más lenta, no la suma de máximos por etapa.
- `phase(title)` y `log(msg)` — agrupación y progreso visible.
- `opts.isolation: 'worktree'` — **cada agente en su propio worktree de git**.

Además: tope de concurrencia automático, contabilidad de coste, cancelación, y reanudación por `runId` que reutiliza el prefijo de llamadas no modificadas.

### Por qué esto importa para Keel

Resuelve exactamente las tres carencias que la sección 4.4 identificaba en un orquestador hecho a mano:

| Carencia de 4.4 | Respuesta del mecanismo nativo |
|---|---|
| Sin aislamiento → colisión sobre el mismo checkout (6.1) | `isolation: 'worktree'` por agente |
| Sin límite de concurrencia ni cancelación | Tope automático y cancelación integrados |
| Sin contabilidad de coste | Contabilizado por el harness |

Y encaja con algo que Keel **ya hace**: v5.2.0 introdujo el despacho en paralelo de verificadores ("fast means fanned out, never trimmed") y la regla de un agente por unidad independiente — pantallas en la pasada de fidelidad de Fase 4, locales en la revisión de guía de Fase 6, dimensiones de auditoría en la adopción. Hoy eso se describe en prosa y lo ejecuta el criterio del modelo. Un workflow lo convierte en un script que hace siempre lo mismo, con las cuatro excepciones seriales de v5.2.0 expresadas como código en vez de como una regla que hay que recordar.

Candidatos naturales, por orden de encaje:

1. **La pasada de conformidad de v5.0.0** — recorrer cada fila aplicable de la Tabla 1 del manifiesto más cada acción de la Tabla 3 posterior a la línea base. Es un abanico sobre una lista conocida con salida estructurada: el caso de uso exacto de `pipeline` + `schema`.
2. **El gate de Fase 7** — `security-auditor` + `guide-qa` en paralelo, más los verificadores condicionales que el proyecto tenga.
3. **La pasada de fidelidad de Fase 4** — captura única del entorno, luego un auditor por pantalla leyendo las capturas en paralelo. v5.2.0 ya describe este patrón literalmente.
4. **La auditoría de adopción** — una dimensión por agente.

### El límite, y es el mismo que en 4.4

**Un agente de workflow no es un chat.** Nace, responde y muere; nadie puede entrar en él, retomarlo ni corregirlo a mitad. Por eso los workflows sirven para las partes de Keel que son **verificación y abanico**, y no para las que son **conversación**: un sprint de desarrollo donde el usuario decide, aprueba una Design Request o responde a una fila de "When to stop and ask" necesita un chat de verdad, que es lo que la sección 4.3 resuelve por la vía de la CLI.

La división que propondría:

- **Fases de abanico y gates** → workflows nativos. Determinista, aislado, contabilizado.
- **Sprints de desarrollo** → chats, encadenados o no según `Chaining:`.

Son mecanismos complementarios, no alternativos, y confundirlos es lo que produce las colisiones de la sección 6.1.

### Qué habría que verificar antes de escribir nada en la skill

Nada de lo anterior está probado. Antes de que Keel lo adopte haría falta, como mínimo:

1. Ejecutar un workflow real sobre un proyecto Keel y comprobar que la salida estructurada es utilizable para rellenar `docs/keel-conformance.md` sin post-proceso.
2. Comprobar el comportamiento de `isolation: 'worktree'` con la sección 6.2 en mente: cada worktree comparte el commit raíz, así que **un agente en un worktree que leyera un traspaso vería exactamente el fallo silencioso 6.2**. Hay que confirmar que los agentes de workflow no consumen `docs/continuation-prompt.md`, o aplicarles la comprobación de contención de la sección 7.
3. Confirmar la disponibilidad: la herramienta exige opt-in explícito del usuario y puede no estar presente en todos los entornos. Keel no puede depender de ella sin una alternativa en línea, igual que ya hace con los subagentes.

El punto 2 no es teórico: es la intersección exacta entre este apartado y el fallo silencioso más difícil de ver de todo el informe.

---

## 9. Texto que se sabe incorrecto o incompleto

Propuestas, **no aplicadas**. La decisión es de José.

| # | Ubicación | Problema | Reemplazo propuesto |
|---|---|---|---|
| 1 | `references/project-state.md`, tabla de chequeos (~257) y §"Why `Repo:` exists" | `Repo:` no distingue dos checkouts del mismo repositorio (6.2) | Cuarto chequeo mecánico: la ruta real del fichero está dentro de `git rev-parse --show-toplevel`. Y matizar: *"`Repo:` identifica el repositorio, no el directorio de trabajo"* |
| 2 | `references/project-state.md`, spec de `Repo:` (~232) | Falla en clon superficial con exit 0 (6.3) | *"En un clon superficial este comando devuelve el commit injertado, no la raíz, y sin error: comprueba `git rev-parse --is-shallow-repository` primero; si es `true`, escribe `Repo: unavailable (shallow)`"* |
| 3 | `references/project-state.md`, misma spec | Con dos raíces devuelve dos líneas (6.4) | `git rev-list --max-parents=0 HEAD \| sort \| head -1` |
| 4 | `references/project-state.md` cabecera + las otras tres enumeraciones (lock `:429`, `MANIFEST.md:138`, `CHANGELOG.md:513`) | Ningún campo mira el árbol de trabajo (6.5) | Añadir `Tree: clean` / `Tree: dirty (N)`. **Tocar los cuatro sitios a la vez** o se rompe el invariante de la fila 1g |
| 5 | `references/project-state.md`, contrato punto 2 | Contradice la regla UNBREAKABLE de impresión | Decidir y escribirlo. Sugerencia: un `Handover:` no `clean` imprime el motivo **y** el prompt, marcado como bloqueado, y sale 0 |
| 6 | `references/project-state.md`, contrato punto 4 | "Degradar" inexpresable con un solo tier | *"Si tras degradar la fila de la herramienta no tiene acción en el tier resultante, imprime"* |
| 7 | `references/project-state.md`, contrato punto nuevo | No pide verificar antes de disparar (6.6) | *"Verifica `Repo:` y `Commit:` antes de disparar cualquier acción; un desajuste imprime en vez de encadenar"* |
| 8 | `references/project-state.md`, contrato, "platform open commands" | Cubren disparar una URI, no abrir una sesión CLI visible (hueco 5) | Especificar por plataforma, o declarar `start` verificado **solo en macOS** |
| 9 | `references/project-state.md`, los tres chequeos del courier | Se describen en prosa; el modelo los compone con `$()` anidados y la lista blanca queda inservible | Sección 7: los ejecuta `scripts/keel-handoff-verify`, una entrada en la lista blanca |
| 10 | `references/project-state.md`, chequeo `Generated:` | Llamado mecánico; `+02:00` vs `+0200` falla en comparación de cadenas | Normalizar a epoch antes de comparar |
| 11 | `references/project-state.md`, registro, fila "standalone terminal" | Exige *"zero `VSCODE_*`"*; el terminal integrado de VS Code las tendrá | Pendiente de la medición de la sección 4. Falla seguro, pero probablemente necesita una tercera fila |
| 12 | `SKILL.md:252`, `project-state.md:304` | *"today only Claude Code has one recorded"* — falso sobre el mundo | *"la única verificada hasta hoy"* |
| 13 | `references/project-state.md`, §Chaining | `start` puede producir sesiones concurrentes sin freno (6.1) | Cerrojo de vía única comprobado por la sesión que llega, con el fichero **fuera del repositorio**. Y no ofrecer `start` hasta que exista |
| 14 | `references/project-state.md`, §Chaining + Phase 1/adopción | La pregunta del `Chaining:` no advierte de que `start` salta a CLI ni de que quita la supervisión | Formulación completa en la sección 4.3 |
| 15 | `references/project-state.md`, §"The continuation file" | Solo contempla abrir chats nuevos; ignora el caso más frecuente | Añadir que el traspaso se consume igual con `/clear` en la misma ventana, y que ése es el camino recomendado cuando el chat vive pero el contexto está lleno |

---

## 11. Tercera pasada — revisión de los cambios de Cowork

Estado: 8 ficheros modificados (7 de skill + `CHANGELOG.md`), `HEAD` en `f5783c5`, nada commiteado.

### Coherencia mecánica: 8 de 9 PASS

| # | Resultado | Evidencia |
|---|---|---|
| a | PASS | 5.3.0 en los cuatro sitios; `## 5.3.0` último (línea 506) |
| b | PASS | Tabla 2 con **siete** filas v5.3.0; `diff` contra `git diff --name-only` sin CHANGELOG → `CONJUNTOS IDENTICOS`. `CHANGELOG.md` sigue en v5.2.0 |
| c | **FAIL** | Prosa dice `Eight actions` y hay ocho marcadores, pero **en orden `1,2,3,4,7,8,5,6`** |
| d | PASS | Sello v5.3.0 en `:459`; ítems `1 2 3 4 5 6` entre los delimitadores |
| e | PASS | `cli-print` 0, `cli-start` 0, `Chaining: print` 0, `Chaining: open` 0; un `Chaining: vscode` en `CHANGELOG.md:541`, sección Fixed |
| f | PASS | Dos hits de `TERM_PROGRAM=vscode`, ambos documentando el error |
| g | PASS | Las cuatro enumeraciones listan los **siete** campos con `Tree` incluido: plantilla, lock `:503`, `MANIFEST.md:140`, `CHANGELOG.md:513` |
| h | PASS | Presente en las cuatro listas de `.gitignore` |
| i | PASS | Vallas balanceadas en los ocho ficheros (0/0/0/14/4/2/2/22) |

### Arreglos verificados

Todos los sustantivos del informe están escritos y son correctos:

- **Containment** como primer chequeo y con la razón explícita de por qué va primero (`project-state.md:271`, `:278`).
- **Guarda de shallow** con `Repo: unavailable (shallow)` y el traspaso del peso a containment (`:250`, `:254`).
- **`sort | head -1`** para raíces múltiples (`:251`).
- **Epoch, nunca cadenas**, con el `+02:00` vs `+0200` nombrado (`:288`).
- **`Tree:`** en la cabecera y como sexto chequeo.
- **`keel-handoff-verify`** como artefacto UNBREAKABLE, con la explicación del `Parse error` y la entrada única de lista blanca (`:280`-`:283`).
- **La pregunta del `Chaining:`** en `phase-1-discovery.md:302`-`:312`, con el aviso de que `start` salta a CLI y de que quita la supervisión, más *"offer `prefill` as the maximum where either condition fails, and say which one"* — exactamente lo pedido.
- **`/clear`** recogido como el caso más frecuente y el más seguro (`:296`).
- **Portabilidad** anotada como gap real, no como detalle (`:417`).
- **La exclusión por `VSCODE_*`** eliminada del registro con su razón (`:387`) — corregía un defecto que el propio informe no había detectado.

**Sobre las decisiones de Cowork.** La resolución de `start` como puerta con tres requisitos previos —cerrojo, acción verificada que abra sesión visible, entrada de lista blanca con confianza de carpeta— respeta a la vez la decisión de José (existe, opt-in por proyecto) y la recomendación del informe (no ofrecerlo sin el cerrojo). Es una interpretación correcta y mejor que cualquiera de las dos por separado. No escribir §4.4 ni §4.5 en la skill es lo correcto por la regla propia de la skill.

**Y su observación sobre el punto 2 de §4.5 es cierta, verificada:** un agente en worktree leyendo el traspaso del repo principal da `containment : MISMATCH`, porque `git rev-parse --show-toplevel` devuelve la ruta del worktree y el fichero está fuera de ella. Queda cubierto de facto sin necesidad de afirmar nada sobre workflows.

### Hallazgos nuevos

**N1 (GRAVE) — el cerrojo hereda la trampa del shallow que el propio documento acaba de describir.**
`project-state.md:327` y `MANIFEST.md:47` llavean el cerrojo por *"the repo's root-commit hash"*. Trece líneas antes, `:250`-`:254` explica que en un clon superficial ese comando devuelve el commit injertado y **que el valor cambia tras `git fetch --unshallow`**. Consecuencias, todas sobre el mecanismo que precisamente habilita `start`:

- Un clon superficial y uno completo del mismo repositorio obtienen **claves distintas** → dos "vías únicas" para un mismo repositorio, y el cerrojo no ve nada.
- Tras `--unshallow`, la clave **cambia en el mismo directorio** → una sesión viva que sostiene el cerrojo con la clave antigua es invisible para la siguiente, que usa la nueva. El cerrojo se anula exactamente en el escenario que motiva su existencia.
- `Repo: unavailable (shallow)` dice explícitamente que no se escriba hash, pero el cerrojo **necesita una clave igualmente** y no se especifica cuál.

Reemplazo propuesto en `:327`: *"…keyed by the repo's root-commit hash, obtained with the same guard as `Repo:` above — in a shallow clone the hash is not the root and changes on `--unshallow`, so the key is derived from the real path of `git rev-parse --show-toplevel` instead, which is stable per working directory and is what single-lane actually means."* Y la misma corrección en `MANIFEST.md:47`.

Nota de diseño: llavear por el directorio de trabajo y no por el repositorio es además **más correcto conceptualmente**. Lo que hay que serializar es el árbol donde se escribe, no el repositorio abstracto — es la misma distinción repositorio/directorio que el documento ya defiende para `Repo:` frente a containment. Dos worktrees del mismo repositorio son dos vías legítimas, no una.

**N2 (MEDIO) — el mensaje de cierre afirma algo que puede ser falso.**
`project-state.md:364`-`:365`: el mensaje obligatorio de cierre dice *"A continuation chat is being launched"* y, bajo `start`, que al usuario no le queda *"nothing at all"* por hacer. Pero `:329` establece que una sesión que no logra tomar el cerrojo *"prints the prompt and exits 0"*. En ese caso el chat de continuación **no continúa**, y bajo `start` el usuario por definición no está mirando. La sesión que cerró ya se cerró afirmando lo contrario y no tiene forma de saberlo.

La tabla de `:306` lo repite sin matizar: `start` → *"Human gesture left: None"*.

Reemplazo propuesto: bajo `start`, el mensaje de cierre dice que se ha lanzado un chat de continuación **y que si la vía estuviera ocupada esa ventana lo dirá y mostrará el prompt**; y la tabla de `:306` cambia `None` por `None — unless the lane is busy, in which case the new window prints the prompt`.

**N3 (MEDIO) — las ocho acciones de la Tabla 3 están numeradas fuera de orden.**
`MANIFEST.md:140`, marcadores en este orden de lectura:

```
(1) Add docs/continuation-prompt.md to .gitignore
(2) From the next session that ends mid-work, write the continuation prompt…
(3) When READING one, verify it before acting
(4) Containment, Repo and an ABSOLUTE launch path are all three required…
(7) Ask the Chaining: question once and add the card line
(8) The single-lane lock
(5) Generate scripts/keel-handoff-verify at the next scaffold…
(6) scripts/keel-continue runs that script BEFORE firing
```

La Tabla 3 es la lista de acciones que una reconciliación aplica en orden. Quien la aplique leyendo de arriba abajo las ejecuta desordenadas, y aquí importa: la acción 5 genera `keel-handoff-verify` y la 6 hace que `keel-continue` lo ejecute, pero ambas aparecen **después** de la 7 y la 8, que dependen de que existan. O se renumera para casar con el orden de lectura, o se reordena el texto para casar con los números.

**N4 (MENOR) — el punto 8 del contrato está mal redactado y separado de la lista.**
`project-state.md:411`: *"Under `start`, take the single-lane lock is NOT this script's job"* — falta el gerundio: *"taking the single-lane lock is NOT this script's job"*. Y la línea 410 está en blanco, separando el punto 8 de los siete anteriores; en el resto del documento las listas del contrato van seguidas.

### Veredicto de la tercera pasada

Los tres fallos silenciosos graves del informe (6.1, 6.2, 6.3) están resueltos y bien resueltos. Los seis huecos del contrato, también. La pregunta del `Chaining:` quedó como se pidió.

**Queda N1 antes de commitear.** No es de redacción: el cerrojo es el requisito que habilita `start`, y tal como está llaveado se anula solo en clones superficiales y tras un `--unshallow`. Es la misma trampa que el documento acaba de documentar, reaparecida una sección más abajo — que es exactamente el patrón de todo este trabajo.

N2, N3 y N4 son baratos y van en la misma pasada.

---

## 12. Cambios aplicados por Code — registro exacto para revisión

**Autorizados por José** tras la sección 11. Siete ediciones en **dos ficheros**: `keel/references/project-state.md` y `keel/MANIFEST.md`. **No se tocó la versión, ni el CHANGELOG, ni ningún otro fichero de skill. Nada commiteado.**

### N1 — llaveado del cerrojo (2 ediciones)

**1. `keel/references/project-state.md:327`**

ANTES:
> - **The lock file lives OUTSIDE the repository** (the user's state directory, keyed by the repo's root-commit hash). A lock inside the tree is a brake the chain can erase: a `git clean`, a checkout, or a fresh clone resets it, and the thing it protects is the thing that modifies it.

DESPUÉS:
> - **The lock file lives OUTSIDE the repository** (the user's state directory), **keyed by the REAL path of `git rev-parse --show-toplevel`** — not by the root-commit hash. A lock inside the tree is a brake the chain can erase: a `git clean`, a checkout, or a fresh clone resets it, and the thing it protects is the thing that modifies it. The key is the working directory for two reasons: the root-commit hash carries the shallow trap described above (it is not the root in a shallow clone and it CHANGES on `--unshallow`, so a live session's lock would become invisible to the next one in the same directory), and what has to be serialised is the tree being written to, not the repository in the abstract — two worktrees of one repository are two legitimate lanes, exactly as containment already treats them.

**2. `keel/MANIFEST.md:47`** (Tabla 1, primera celda de la fila del cerrojo)

ANTES: `Single-lane lock (outside the repo, in the user's state dir, keyed by root-commit hash)`

DESPUÉS: `Single-lane lock (outside the repo, in the user's state dir, keyed by the real path of `git rev-parse --show-toplevel` — never the root-commit hash, which is wrong in a shallow clone and changes on `--unshallow`)`

**Justificación registrada:** el propio CHANGELOG (`:521`) enmarca el fallo como *"Two sessions on one **checkout**"*. La unidad a serializar ya era el directorio de trabajo; el llaveado por hash de raíz lo contradecía y además heredaba la trampa documentada en `:250`-`:254`.

### N2 — el mensaje de cierre no puede prometer "nada que hacer" (2 ediciones)

**3. `keel/references/project-state.md:306`** (tabla de valores de `Chaining:`)

ANTES: `| `start` | The tool's recorded action launches AND submits | None |`

DESPUÉS: `| `start` | The tool's recorded action launches AND submits | None — unless the lane is busy, in which case the new window prints the prompt |`

**4. `keel/references/project-state.md`, punto 3 del mensaje de cierre obligatorio**

ANTES:
> 3. What is left for them to do: press Enter in the window that just opened (`prefill`), or nothing at all (`start`).

DESPUÉS:
> 3. What is left for them to do: press Enter in the window that just opened (`prefill`), or nothing at all (`start`) — **and, under `start`, that if the single lane is already busy the new window will say so and print the prompt instead of continuing.** The closing session cannot know: the lock is taken by the ARRIVING session, after this one has finished. Promising an unconditional "nothing to do" is the one claim in this message that can be false, and the user is by definition not watching.

### N3 — orden de las ocho acciones de la Tabla 3 (1 edición)

**5. `keel/MANIFEST.md:140`.** Se **reordenaron los bloques de texto**, no los números: los números ya eran correctos por dependencia (la acción 5 genera `keel-handoff-verify` y la 6 hace que `keel-continue` lo ejecute; ambas deben preceder a la 7, la pregunta del `Chaining:`, y a la 8, el cerrojo). Orden de lectura antes `1,2,3,4,7,8,5,6`; después `1,2,3,4,5,6,7,8`. **Ni una palabra del texto de las acciones fue modificada** — solo se movieron los bloques `**(7)…` y `**(8)…` detrás de `**(6)…`.

### N4 — punto 8 del contrato (1 edición)

**6. `keel/references/project-state.md:410-411`.** Se eliminó la línea en blanco que separaba el punto 8 de los siete anteriores, y se corrigió la gramática:

ANTES: `8. Under `start`, take the single-lane lock is NOT this script's job…`
DESPUÉS: `8. Under `start`, taking the single-lane lock is NOT this script's job…`

### N5 — defecto NUEVO, encontrado al aplicar N3 (1 edición)

**7. `keel/MANIFEST.md:140`.** La fila de la Tabla 3 contenía **dos pipes sin escapar** dentro de `` `git rev-list --max-parents=0 HEAD | sort | head -1` ``, lo que la partía en cuatro celdas en vez de dos y rompía la tabla al renderizar.

ANTES: `` `git rev-list --max-parents=0 HEAD | sort | head -1` ``
DESPUÉS: `` `git rev-list --max-parents=0 HEAD \| sort \| head -1` ``

Era **anterior** a la reordenación de N3 y no lo introdujo Code; se detectó al comprobar la integridad de la fila después de editarla. Nótese que `project-state.md:272` **sí** lo escapaba correctamente — el error estaba solo en el manifiesto.

Se hizo un barrido de toda la skill buscando el mismo defecto (pipes sin escapar dentro de backticks en filas de tabla): **eran los dos únicos casos, y ahora son cero.**

### Re-auditoría tras los cambios: 9 de 9 PASS

| # | Resultado |
|---|---|
| a | 5.3.0 en los cuatro sitios; `## 5.3.0` último (`CHANGELOG.md:506`) |
| b | Tabla 2 con siete filas v5.3.0, conjunto idéntico a `git diff --name-only` sin CHANGELOG; `CHANGELOG.md` en v5.2.0 |
| c | Una fila v5.3.0; prosa `Eight actions`; marcadores `1 2 3 4 5 6 7 8` **en orden**; la fila rinde como **2 celdas** |
| d | Sello `KEEL:BEGIN — v5.3.0`; ítems `1 2 3 4 5 6` |
| e | `cli-print` 0, `cli-start` 0; un `Chaining: vscode` en la sección Fixed del CHANGELOG |
| f | Dos hits de `TERM_PROGRAM=vscode`, ambos documentando el error |
| g | Enumeraciones de los siete campos íntegras |
| h | `docs/continuation-prompt.md` en las cuatro listas |
| i | Vallas balanceadas en los ocho ficheros; cero pipes sin escapar en toda la skill |

### Lo que Code NO tocó, y sigue abierto

- **La versión, el CHANGELOG y los otros seis ficheros de skill.** Intactos.
- **`scripts/keel-handoff-verify` y el cerrojo**: especificados, sin escribir. El prototipo de Code es BSD/macOS (`stat -f`, `date -j`); faltan las formas GNU (`stat -c`, `date -d`) y Windows. Sigue siendo un gap real: un script generado que solo corre en la máquina que lo generó es un check que no se puede ejecutar.
- **`start` en Linux y Windows**: sin verificar. Hoy resuelve solo en macOS.
- **La medición del terminal integrado de VS Code**: sigue pendiente y necesita al usuario.

---

## 13. v5.3.1 — dos defectos que llegaron a producción

v5.3.0 se commiteó (`8e862a3`), etiquetó y mergeó. Estos dos defectos estaban dentro y la sección 11 no los detectó, porque comprobaba coherencia entre lo escrito y no si lo escrito tenía dónde ejecutarse. Bump autorizado explícitamente por José.

### G1 — `scripts/keel-handoff-verify` exigido por el índice, ausente del contrato

Menciones en `references/phase-5-development.md`, que **es** la referencia del scaffold de Fase 5:

```
keel-verify            12
keel-doctor             2
keel-continue           2
keel-handoff-verify     0     <---
```

`MANIFEST.md` Tabla 1 lo exigía desde *"Phase 5 scaffold"* y `project-state.md` afirmaba que se genera *"at the Phase 5 scaffold beside `keel-verify` and `keel-doctor`"*. La referencia que ejecuta el scaffold no lo nombraba. Por la **regla de autoridad del propio manifiesto** (*"the phase references are the contract… if they ever disagree, the reference wins"*), el artefacto no se creaba.

Con un efecto invertido: la acción (5) de la Tabla 3 sí lo mandaba generar en la reconciliación, de modo que **los proyectos anteriores a v5.3.0 lo tendrían y los nuevos no.**

**Arreglo.** Dos párrafos en `phase-5-development.md`, justo antes de §1a. Se genera **siempre**, no condicionado a `Chaining:` — todo proyecto escribe `docs/continuation-prompt.md` al cerrar sea cual sea el valor de la tarjeta, luego todo proyecto necesita el script que lo verifica. Su entrada única de lista blanca entra en el mismo momento.

### G2 — el cerrojo era una puerta sin llave

Tabla 1 decía *"Required from: Before `start` is offered"* — una condición, no un paso. Búsqueda en toda la skill de quién lo crea y cuándo: **cero resultados**; `single-lane` tenía 0 menciones en la referencia del scaffold. `start` estaba bloqueado tras un artefacto que ningún procedimiento producía.

**Arreglo, y es una decisión de diseño de Code que conviene revisar.** El carril lo toma **`scripts/keel-handoff-verify`**, el mismo script que la sesión que llega ya ejecuta antes de actuar. Razones:

- Es el momento exacto en que hay que reclamar el carril: **no queda ventana entre verificar y empezar a trabajar** en la que una segunda sesión pueda colarse. Esa ventana es literalmente lo que produjo las cuatro sesiones de la sección 6.1.
- Un script en vez de dos, **una entrada de lista blanca en vez de dos**, y ningún paso que el usuario tenga que recordar.
- En tarjetas que no son `Chaining: start`, el script corre sus cinco chequeos y no toma nada.

La fila de Tabla 1 del cerrojo se reescribió: ya no finge ser una ruta dentro del proyecto (no lo es — vive en el directorio de estado del usuario), sino que nombra al script que lo toma y su momento.

### Ficheros tocados en v5.3.1

| Fichero | Cambio |
|---|---|
| `keel/SKILL.md` | Versión: frontmatter y encabezado |
| `keel/MANIFEST.md` | Cabecera; Tabla 1 filas 46-47 (G1 y G2); Tabla 2 ×4 filas a v5.3.1; nueva fila v5.3.1 en Tabla 3 con sus dos acciones |
| `keel/CHANGELOG.md` | Nueva sección `## 5.3.1`, última, con su bloque **Fixed** |
| `keel/references/phase-5-development.md` | Los dos párrafos de G1 y G2, antes de §1a |
| `keel/references/project-state.md` | Ancla procedimental del cerrojo en §"The single-lane lock"; sello del lock a `v5.3.1` |
| `README.md` | Línea de versión — **ver abajo** |

### Un quinto punto de versión que nadie tenía en la lista

El repositorio tiene su propio linter, `tests/lint-release.py`, y al ejecutarlo falló:

```
FAIL  README.md version line: says 5.3.0, frontmatter says 5.3.1
1 check(s) FAILED — this tree is not releasable.
```

`README.md:7` lleva una línea `**Version:**`. La especificación de la Tarea 1 hablaba de **cuatro** sitios; son **cinco**. Corregido, y tras corregirlo:

```
All checks passed. Releasable.
```

Vale la pena señalarlo porque es exactamente la tesis de la sección 7 funcionando en el propio repositorio de Keel: el chequeo que nadie recordaba lo cazó una máquina, no una revisión.

### Auditoría de v5.3.1

| # | Resultado |
|---|---|
| a | 5.3.1 en los **cinco** puntos (frontmatter, encabezado SKILL, cabecera MANIFEST, README, `## 5.3.1` último en CHANGELOG) |
| b | Tabla 2: cuatro filas v5.3.1, conjunto idéntico a `git diff --name-only v5.3.0` restringido a `keel/` sin CHANGELOG. `README.md` correctamente fuera (no es fichero de skill) |
| c | Una fila v5.3.1 en Tabla 3, última, con dos acciones y dos celdas |
| d | Sello `KEEL:BEGIN — v5.3.1`; ítems `1 2 3 4 5 6` |
| e-f | Vocabulario retirado en cero; `TERM_PROGRAM=vscode` solo donde se documenta la medición y el error |
| g | G1 y G2 anclados en `phase-5-development.md` (antes 0 menciones cada uno) |
| h-j | `.gitignore` en las cuatro listas; vallas pares; cero pipes sin escapar |
| — | **`tests/lint-release.py`: All checks passed. Releasable.** |

### El patrón, cuarta aparición

G1 y G2 son la misma forma que A3, que 6.2 y que N1: **algo registrado en un sitio y ausente del sitio que lo ejecuta.** La regla de autoridad del manifiesto existe porque esa forma reaparece — decide qué lado gana cuando hay desacuerdo — y en ambos casos ganó el lado silencioso. Está escrito así en el CHANGELOG, porque es lo que hay que recordar de esta versión.

**Nada commiteado, etiquetado ni empujado.** El árbol queda listo con el linter en verde; la decisión de publicar es de José.

---

## 10. Veredicto

**La parte mecánica está lista:** 9 de 9, los 15 defectos del primer informe corregidos, sin regresiones. **El arreglo de A3 es real** y está demostrado con tres escenarios.

**No recomiendo commitear todavía**, por tres fallos que se manifiestan en silencio y son de la misma familia que el A3 original:

- **6.1** — concurrencia por auto-encadenado. El más grave, y el único descubierto ejecutando en lugar de leyendo.
- **6.2** — dos checkouts del mismo repositorio en el mismo commit.
- **6.3** — clon superficial.

Los tres tienen arreglo barato y verificado. **La solución de la sección 7 resuelve 6.2, 6.3, 6.4 y tres huecos del contrato de una vez**, y es un cambio de una frase en la skill más un script generado en el scaffold. Queda aparte 6.1, que necesita el cerrojo, y la decisión de producto de la sección 4.3 sobre cómo y cuándo ofrecer `start`.

Con eso resuelto —y sin subir ninguna versión, que sigue siendo decisión exclusiva de José— la daría por lista.

**Sigue pendiente y necesita al usuario:** la medición del terminal integrado de VS Code (sección 4), un único comando.
