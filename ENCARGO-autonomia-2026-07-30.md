# Encargo para Claude Code — Autonomía, ramas y contención de agentes en el skill Keel

**Repo:** `~/Documents/GitHub/keel-skill`
**Fecha del acuerdo:** 2026-07-30
**Quién lo pide:** José Conti

Lee este documento entero antes de tocar nada. Después lee el `SKILL.md`
completo de Keel y sus referencias de fases, y aplica las siete reglas que
vienen a continuación al protocolo del skill.

## Normas de ejecución de este encargo

- No cambies el número de versión salvo que José lo indique explícitamente.
  Es una regla inquebrantable en sus repos.
- Actualiza `docs/PROGRESS.md` y `docs/decisions.md` en el mismo momento en
  que hagas cada cambio, no al final.
- Pasa el linter del skill al terminar.
- Cuando acabes: dime qué ficheros has tocado, mergea a `develop` y sube.
  No toques `main`.
- Si alguna de estas reglas choca con algo que ya existe en el skill, no la
  apliques a ciegas: dilo, explica el choque y propón la resolución.

---

## REGLA 1 — Modo de permisos

### Problema

Keel trabaja en bloques largos de herramientas encadenadas. En `manual mode`
(el modo por defecto de Claude Code) el análisis estático de comandos no puede
casar con las reglas `allow` ningún comando que contenga variables de shell,
`&&`, `;` o pipes, así que abre un diálogo de permiso. José lo detectó el
2026-07-30: Keel se paraba cada pocos comandos. La causa combinada era
`manual mode` más el prefijo `export PATH=... && ...` que Keel ponía en cada
llamada, que por sí solo ya fuerza el diálogo.

### Qué añadir

Un paso nuevo, "Modo de permisos", en el bloque de arranque y mantenimiento
que se ejecuta antes de cualquier trabajo:

1. Comprobar el modo de permisos activo. Si es `manual`, resolverlo antes de
   continuar.
2. Vía preferida, persistente: crear o fusionar `.claude/settings.local.json`
   en la raíz del repo. Keel lo escribe por su cuenta y avisa al usuario; no
   pide permiso previo, porque el fichero es local y nunca se commitea. Nunca
   borra reglas que ya hubiera puesto el usuario: fusiona.
3. Vía alternativa, por sesión, si el usuario prefiere no tocar ficheros:
   arrancar con `claude --permission-mode auto`, o pulsar Shift+Tab hasta
   llegar a `auto`.
4. Verificar que `.claude/settings.local.json` está en `.gitignore`; si no,
   añadirlo.

### Contenido del fichero

El bloque `deny` definitivo está en la Regla 6, que amplía este. Escribe
directamente la versión completa de allí. La base es:

```json
{
  "permissions": {
    "defaultMode": "auto",
    "deny": [ "...ver Regla 6..." ]
  }
}
```

Sin bloque `env`. Ver el apartado "NO usar `env.PATH`" más abajo.

`git push` NO va en `permissions.ask`. Ver Regla 3.

### `bypassPermissions` está PROHIBIDO

Keel no propone, no sugiere y no genera nunca comandos de arranque con
`--permission-mode bypassPermissions` ni `--dangerously-skip-permissions`. Si
el usuario lo pide, Keel explica el motivo y ofrece `auto` en su lugar.

Motivos, los dos igual de importantes:

1. **Anula todas las reglas `deny`.** En `bypassPermissions` no se evalúa
   ningún check, así que todo el blindaje de la Regla 6 (`~/.claude/**`,
   `.git/**`, `rm -rf`, `git reset --hard`, `git push --force`) queda sin
   efecto. Es exactamente el escenario del incidente del 30/07, pero sin red.
2. **No elimina las interrupciones, las añade.** `bypassPermissions` muestra un
   aviso de aceptación de responsabilidad al arrancar que es insaltable por
   diseño. Es decir, en lo que respecta a la automatización desatendida es peor
   que `auto`, que no muestra nada.

`auto` es el único modo válido para trabajo desatendido: aprueba por
clasificador, no interrumpe, y respeta las reglas `deny`.

Esto ocurrió de verdad: el 2026-07-30 Claude Code generó por su cuenta un
comando de arranque con `bypassPermissions`. Documéntalo en `docs/decisions.md`
junto con la prohibición.

Añade además un aviso en `keel-doctor`: si detecta que la sesión corre en
`bypassPermissions`, lo reporta como riesgo y recomienda reiniciar en `auto`.

**Conflicto que hay que resolver, no ignorar:** el despacho del fan-out
(`references/project-state.md`, "Dispatching a worker", introducido en v5.4.1)
lanza cada worker con `--permission-mode bypassPermissions`, justificándolo en
que un worker desatendido no puede parar a pedir permiso. Con esta regla, eso
deja de ser aceptable: un worker en bypass no evalúa el bloque `deny`, así que
los agentes del fan-out corren sin ninguna de las barreras de la Regla 6.

Cámbialo a `--permission-mode auto`, que resuelve el mismo problema — el worker
no se detiene — sin desactivar las `deny`. Verifica que un worker despachado
así llega al final de su slice sin diálogos; si por algún motivo `auto` no
bastara, dilo y no lo cambies, pero entonces documenta en `docs/decisions.md`
el riesgo que queda abierto.

### Higiene asociada

Con `defaultMode: "auto"`, el prefijo `export PATH=... && ...` deja de causar
diálogos de permiso, pero sigue siendo ruido innecesario. Revisa `scripts/` y
las referencias de fases y elimínalo donde aparezca: Claude Code hereda el PATH
del shell desde el que se lanza.

El comando de arranque que Keel proponga al usuario, en el prompt de
continuación o en cualquier otro sitio, es siempre la forma limpia, sin flags
de permisos y sin prefijo de PATH:

```bash
claude "Lee <ruta>/docs/continuation-prompt.md y continua en modo autonomo"
```

El modo va en `~/.claude/settings.json` con `permissions.defaultMode: "auto"`,
no en la línea de comandos.

### `env.PATH` — la regla ya existe, añádele un síntoma

Keel ya documenta correctamente esta trampa en `references/keel-maintenance.md`:
`env.PATH` se escribe EXPANDIDO y ABSOLUTO, nunca con `${PATH}` ni `$HOME`,
incluyendo siempre `/usr/bin`, `/bin`, `/usr/sbin`, `/sbin`. **No cambies esa
regla.** El valor verificado para macOS con MacPorts y Homebrew es el que ya
está allí.

Lo único que falta es un síntoma más en la lista de consecuencias, observado
por José el 2026-07-30 con un `~/.claude/settings.json` de usuario que llevaba
`$HOME/...:${PATH}`:

> Además de `command not found`, un PATH roto impide encontrar el binario
> `security` de macOS, así que Claude Code no puede leer las credenciales del
> llavero. El síntoma es un bucle de identificación: cada chat nuevo pide
> identificarse, el usuario se identifica correctamente, y el siguiente chat
> vuelve a pedirlo. Es un síntoma especialmente engañoso porque no parece un
> problema de PATH.

Añádelo al párrafo que ya existe, y añade el mismo caso a los checks de la
Regla 1-bis.

---

## REGLA 1-bis — Auditoría y reparación del `~/.claude/settings.json` global

El `settings.local.json` del repo no basta: la configuración global del usuario
puede contener por sí sola los agujeros que causaron los incidentes. Keel debe
auditarla al arrancar y repararla.

### Auditoría

Leer `~/.claude/settings.json` y comprobar estos puntos. Es una lista cerrada;
si Keel encuentra otra cosa preocupante, la reporta pero no la toca.

**Bloqueantes — Keel los arregla:**

1. `permissions.defaultMode` ausente o igual a `manual`. Es la causa de que la
   sesión se pare cada pocos comandos.
2. Ausencia de `permissions.deny`, o `deny` sin las entradas de la capa 2 de la
   Regla 6.
3. Rutas bajo `~/.claude/` en `permissions.additionalDirectories`, en especial
   `~/.claude/projects/**` y `~/.claude/todos/**`. **Esto es lo que causó el
   incidente del 30/07**: el subagente no se saltó ninguna barrera, tenía
   permiso explícito de escritura sobre el directorio de estado de sesiones.
   Keel las elimina siempre.
4. `env.PATH` con variables sin expandir (`${PATH}`, `$HOME`, cualquier otra) o
   sin los directorios de sistema. Keel lo **corrige** por el valor expandido y
   absoluto que ya especifica `references/keel-maintenance.md`. Un PATH roto
   aquí envenena todos los proyectos de la máquina, no solo uno, y su síntoma
   más engañoso es el bucle de identificación descrito en la Regla 1.

**Avisos — Keel los reporta, no los toca:**

5. Entradas basura en `allow`, residuo de comandos partidos por el parser al
   pulsar "Yes, and don't ask again": `Bash(done)`, `Bash(fi)`, `Bash(do)`,
   entradas con `__NEW_LINE_`, y reglas `Read(...)` con comillas escapadas o
   rutas que no son rutas. No hacen daño, pero ensucian y confunden.
6. Entradas de `allow` con rutas absolutas de un solo uso
   (`Bash(git -C /ruta/concreta/... log ...)`). Proponer sustituirlas por la
   regla genérica equivalente.
7. Presencia en `allow` de ejecución arbitraria: `Bash(bash:*)`,
   `Bash(python3:*)`, `Bash(perl:*)`, `Bash(curl:*)`, `Bash(chmod:*)`. Son
   legítimas y probablemente necesarias, pero equivalen a permitirlo todo, y
   las `deny` no alcanzan a lo que se ejecute desde dentro de un script. Keel
   lo dice una vez y no insiste.
8. `skipDangerousModePermissionPrompt: true`. Está para saltar el aviso de
   `bypassPermissions`, que es un modo prohibido (Regla 1). Proponer quitarlo.

### Reparación

Keel arregla los puntos 1 a 4 por su cuenta, sin pedir permiso, y avisa de qué
ha cambiado. El fichero es local del usuario y no se commitea en ningún repo.

Antes de escribir, **siempre** copia de seguridad:

```bash
cp ~/.claude/settings.json ~/.claude/settings.json.bak
```

La escritura es una fusión, nunca un reemplazo: se conserva íntegra la lista
`allow` del usuario y todo lo que Keel no entienda. Solo se añade lo que falta
y se eliminan las rutas del punto 3.

Los puntos 5 a 8 se reportan al usuario con la lista concreta de lo encontrado
y se aplican solo si él lo pide.

Si por lo que sea Keel no puede escribir el fichero, genera la versión
corregida en `/tmp/settings.json.keel` y le da al usuario el comando exacto
para copiarla. No se queda esperando ni continúa como si nada.

### Verificación

`keel-doctor` incluye estos mismos ocho puntos como checks, con las severidades
indicadas: bloqueantes del 1 al 4, avisos del 5 al 8.

---

## REGLA 2 — Estrategia de ramas: `develop` como integración

- El repo tiene una rama `develop`. Si no existe, Keel la crea a partir de
  `main`/`master` en el arranque y la publica.
- Keel abre sus ramas de trabajo (feature, fix, issue) siempre partiendo de
  `develop`.
- **El merge de esas ramas a `develop` lo hace SIEMPRE Claude Code, sin
  preguntar**, junto con el push a remoto. No se espera confirmación del
  usuario. Aplica muy especialmente en modo automático.
- **El merge de `develop` a `main`/`master` lo hace la persona.** Keel no lo
  ejecuta nunca por iniciativa propia. Solo lo hace si el usuario lo pide
  explícitamente, y lo mismo para crear un tag o una release.
- Cuando `develop` acumula trabajo listo para producción, Keel lo señala en
  `docs/PROGRESS.md` y en el prompt de continuación, pero no actúa.

El orden exacto de las operaciones de merge está en la Regla 7, que distingue
entre merge directo y merge por pull request.

---

## REGLA 3 — Push siempre por Code

Subir a Git es responsabilidad de Claude Code, no del usuario. Nada de dejar
commits locales sin pushear "para que los revise el humano".

Esto corrige un patrón real: en `docs/PROGRESS.md` hay varias entradas con
PENDIENTE push acumuladas de versiones anteriores. Al aplicar esta regla,
revisa esas entradas y resuélvelas.

Deja constancia de la regla en `docs/decisions.md`.

---

## REGLA 4 — Avanzar sin paradas

Cuando Keel termina un bloque de trabajo y queda trabajo pendiente en la cola
que NO depende de lo recién hecho, debe continuar sin detenerse a preguntar,
abriendo un chat nuevo si el contexto lo exige.

Solo se para cuando:

- el siguiente paso depende de algo que aún no está hecho, o
- necesita una decisión que solo puede tomar la persona.

Añade esto a la plantilla de `docs/continuation-prompt.md` (en
`references/project-state.md`), como instrucción explícita para el chat de
relevo, junto con:

- el paso de comprobación del modo de permisos (Regla 1), para que el relevo
  no arranque en `manual`;
- el estado de ramas: en qué rama está el trabajo, qué queda por mergear a
  `develop`, y si hay algo esperando decisión humana para `main`.

El prompt de continuación debe dejar indicado al siguiente chat que también él
continúa sin parar mientras haya trabajo independiente en la cola.

---

## REGLA 5 — Historial de merges y limpieza de ramas

### `--no-ff` obligatorio

El merge a `develop` se hace SIEMPRE con `git merge --no-ff`, nunca
fast-forward. El commit de merge es el registro histórico: conserva el nombre
de la rama y el conjunto de commits que aportó. Sin `--no-ff` la rama
desaparece del historial y luego no hay forma de saber qué se integró, que es
justo lo que se quiere evitar al borrar ramas.

Mensaje del commit de merge, formato fijo para poder buscarlo después:

```
merge(<rama>): <resumen en una línea> [#<issue si lo hay>]
```

### Borrado de la rama

Inmediatamente después del merge y del push de `develop`:

- `git branch -d <rama>` — con `-d`, **nunca `-D`**. Si git se niega porque la
  rama no está totalmente integrada, eso es señal de que el merge no está
  completo: Keel PARA, lo reporta y no fuerza el borrado.
- `git push origin --delete <rama>`.

Antes de borrar, verificar que la rama está realmente contenida en `develop`
(`git branch --merged develop`). Solo borrar si aparece ahí.

No se borra nunca `develop`, ni `main`/`master`, ni ninguna rama que la persona
haya creado a mano y Keel no haya mergeado.

El orden concreto cambia si el proyecto usa pull requests: ver Regla 7.

### Historial

No hace falta un fichero de registro aparte; el historial vive en git.

- En `docs/PROGRESS.md`, la entrada de cada trabajo cerrado anota el hash del
  commit de merge en `develop`. Una línea, no un bloque.
- Para consultar el historial de integraciones:
  `git log --merges --first-parent develop`.

Documenta en `docs/decisions.md` el porqué de `--no-ff`: es lo que permite
borrar las ramas sin perder la trazabilidad.

---

## REGLA 6 — Agentes de solo lectura: contención dura

### Incidente que la motiva

2026-07-30, proyecto `deca-pretiumgestion-com`: un subagente de auditoría de
seguridad, cuyo encargo era leer e informar, borró un fichero de estado de
sesión bajo `~/.claude/projects/`. No hubo pérdida, pero fue una acción fuera
de su remit y obligó a contrastar todo su informe con un agente distinto.

Documenta el caso en `docs/decisions.md` como justificación de la regla.

La defensa tiene que ser de permisos, no de prompt: un agente al que le dices
"solo lee" puede desobedecer; uno que no tiene la herramienta, no.

Tres capas, de fuera hacia dentro. Keel las aplica todas, no una.

### Capa 1 — Herramientas: el agente no tiene con qué destruir

Todo subagente de Keel cuyo encargo sea leer, auditar, revisar o informar se
define con lista de herramientas cerrada. En su fichero
`.claude/agents/<nombre>.md`, frontmatter:

```yaml
tools: Read, Grep, Glob, WebFetch
```

Sin `Write`, sin `Edit`, sin `Bash`, sin `NotebookEdit`. Nunca `tools: *` para
un rol de lectura.

Si el agente necesita ejecutar algo para auditar (correr los tests, un linter),
se le da `Bash` pero se le añade la capa 2 con reglas específicas; no se le da
nunca `Write` ni `Edit`.

Ojo: **`Bash` es la puerta trasera de `Write`**, porque `echo ... > fichero`
escribe igual. Un agente al que le quitas `Write` pero le dejas `Bash` sin
acotar sigue pudiendo destruir cosas. Ahí la barrera real es el bloque `deny`
de la capa 2.

Revisa todos los agentes que Keel ya define y aplícales esta lista. Los roles
afectados son, como mínimo: el auditor de seguridad, el code-reviewer, los
verificadores del fan-out paralelo y el lector del split lectura/ejecución.

### Capa 2 — Permisos: rutas prohibidas para todo el mundo

Bloque `deny` completo del `.claude/settings.local.json` de la Regla 1. Las
reglas `deny` sí casan aunque el comando lleve asignaciones de variables o esté
compuesto, así que son la barrera fiable:

```json
{
  "permissions": {
    "defaultMode": "auto",
    "deny": [
      "Bash(rm -rf /*)",
      "Bash(sudo *)",
      "Bash(curl * | sh)",
      "Bash(rm *~/.claude*)",
      "Bash(rm *.git/*)",
      "Bash(git clean *)",
      "Bash(git reset --hard *)",
      "Bash(git checkout -- *)",
      "Bash(git push --force *)",
      "Bash(git branch -D *)",
      "Bash(git filter-branch *)",
      "Bash(git filter-repo *)",
      "Write(~/.claude/projects/**)",
      "Edit(~/.claude/projects/**)",
      "Write(~/.claude/todos/**)",
      "Edit(~/.claude/todos/**)",
      "Write(.git/**)",
      "Edit(.git/**)"
    ]
  }
}
```

Verifica la sintaxis exacta de las reglas de rutas con `/permissions` antes de
darlo por bueno; si algún patrón no lo reconoce Claude Code, ajústalo y déjalo
anotado en `docs/decisions.md`.

Precedencia a tener presente: `deny` gana siempre, por encima de `allow`, del
modo `auto` y de cualquier hook.

Nota importante sobre `defaultMode: "auto"`: el clasificador aprueba por su
cuenta, así que sin este `deny` explícito un borrado plausible puede pasar. El
`deny` es lo que hace seguro el modo automático, no al revés.

`~/.claude/projects/` queda fuera del repo, así que el `deny` es la única
barrera real ahí: dentro del repo salvaría el historial de git, fuera no.

**Por qué el `deny` es `~/.claude/projects/**` y no `~/.claude/**`:** si se
prohíbe todo `~/.claude/`, Keel tampoco puede arreglar su propio
`~/.claude/settings.json` (Regla 1-bis), y las reglas `deny` no las puede
saltar nadie, ni él mismo. Se protege lo que se rompió de verdad — el estado de
sesiones y los todos — y se deja `settings.json` editable. Los agentes de
lectura siguen sin poder tocarlo porque en la capa 1 no tienen `Write` ni
`Edit` en absoluto.

### Capa 3 — Contrato en el encargo

Toda plantilla de encargo a un subagente de lectura empieza con esta línea:

> Tu encargo es leer e informar. No escribes, no borras, no modificas nada, ni
> dentro ni fuera del repo. Si detectas algo que requiere un cambio, lo
> describes en tu informe y no lo aplicas. Salirte de esto invalida tu informe
> entero.

Y la contrapartida, dirigida al orquestador: **el informe de un agente que ha
mutado estado fuera de su encargo se considera no fiable y se contrasta con un
agente distinto antes de usarlo.** Es lo que se hizo en el incidente y
funcionó; codifícalo en vez de dejarlo al criterio del momento.

### Quién escribe los informes

El informe de un subagente viaja como su mensaje de retorno, no como fichero.
Por eso quitarle `Write` no le impide informar.

Cuando un informe deba quedar en disco (`docs/security-review.md`,
`docs/audit-*.md`, o lo que corresponda):

- **Lo escribe el agente principal**, con el texto que devolvió el subagente.
  Nunca el subagente.
- Esto no es solo contención: es control de calidad. El principal ve el informe
  antes de persistirlo y puede contrastarlo.

Revisa las plantillas de encargo de Keel: si alguna le dice a un subagente
"escribe tu informe en `docs/...`", reescríbela como "devuelve tu informe; el
orquestador lo persiste".

Única excepción admisible: un agente que genere un artefacto voluminoso donde
devolverlo por contexto sea inviable, por ejemplo un volcado de datos. En ese
caso se le da `Write`, pero:

- se le indica una ruta única y concreta dentro del repo, nunca un directorio
  general;
- se le prohíbe explícitamente cualquier otra escritura en el contrato;
- las reglas `deny` de la capa 2 siguen cubriendo `~/.claude/**` y `.git/**`;
- el agente principal verifica que solo apareció ese fichero
  (`git status --porcelain`) antes de dar el trabajo por bueno.

Los roles de auditoría, revisión y verificación no entran en la excepción: van
sin `Write` y sin `Edit`, sin discusión.

---

## REGLA 7 — Merge directo o por pull request: detección y orden correcto

Concreta el momento exacto de borrar la rama de las Reglas 2 y 5. Hay dos
flujos posibles y hay que decidir cuál se usa **antes** de tocar nada, porque
el orden de las operaciones es distinto y mezclarlos produce estados
inconsistentes en la forja.

### Paso 0 — Keel decide el flujo al arrancar, no sobre la marcha

Comprueba, en este orden, y anota el resultado en `docs/decisions.md` para que
no se vuelva a decidir en cada ciclo:

1. ¿Hay `gh` autenticado y remoto en GitHub (o equivalente en la forja que
   sea)? Si no, flujo A.
2. ¿Tiene `develop` protección de rama que exija PR? Compruébalo con
   `gh api repos/{owner}/{repo}/branches/develop/protection`. Si la exige,
   flujo B obligatorio.
3. Si no la exige, gana lo que diga `docs/decisions.md`. Si no dice nada, por
   defecto flujo A, y Keel lo anota.

Nunca alternar entre flujos dentro del mismo proyecto sin dejarlo escrito.

Comprobación previa al ciclo de merge: `gh auth status` y existencia de
`develop` en remoto. Si `gh` no está autenticado y el proyecto es flujo B, Keel
para y lo dice, en vez de caer al flujo A por su cuenta.

### FLUJO A — Merge directo en local (por defecto)

Orden estricto, sin saltarse pasos:

1. `git fetch origin` y `git switch <rama>`.
2. Integrar `develop` en la rama de trabajo primero: `git merge origin/develop`.
   Los conflictos se resuelven **aquí**, en la rama de trabajo, nunca en
   `develop`. Así `develop` no queda jamás en estado de conflicto.
3. Correr las pruebas sobre la rama ya integrada. Si fallan, se para: no se
   mergea.
4. `git switch develop && git pull --ff-only origin develop`. Si este pull no
   puede ser fast-forward, alguien tocó `develop`: volver al paso 2 y repetir.
5. `git merge --no-ff <rama> -m "merge(<rama>): <resumen> [#issue]"`.
6. `git push origin develop`. Si el push es rechazado, no forzar nunca: volver
   al paso 4.
7. Verificar contención: `git branch --merged develop | grep <rama>`. Solo si
   aparece, continuar.
8. Borrar: `git branch -d <rama>` y luego `git push origin --delete <rama>`.

### FLUJO B — Por pull request

El orden cambia: la rama remota se borra al final y solo cuando el PR conste
como `MERGED`.

1. Pasos 1 a 3 del flujo A idénticos: integrar `develop` en la rama de trabajo
   y resolver los conflictos ahí, con las pruebas en verde. Esto garantiza que
   el PR nace mergeable y la forja nunca muestra conflictos.
2. `git push -u origin <rama>`. Si la rama ya existía en remoto y hubo
   reintegración, usar `git push --force-with-lease`, nunca `--force` a secas,
   y solo sobre la propia rama de trabajo. Jamás force-push sobre `develop` ni
   sobre `main`.
3. `gh pr create --base develop --head <rama> --title "..." --body "..."`.
4. Esperar a CI: `gh pr checks <n> --watch`. Si falla, se corrige en la rama y
   se repite; no se mergea con checks en rojo.
5. `gh pr merge <n> --merge --delete-branch`.
   - `--merge` obligatorio. **Nunca `--squash` ni `--rebase`**: ambos rompen la
     regla del historial, porque no dejan commit de merge con el nombre de la
     rama y `git log --merges` deja de servir.
   - `--delete-branch` borra la rama remota en el mismo acto y en el orden
     correcto, después de que el PR esté cerrado como merged. Es lo que evita
     el estado inconsistente.
6. Verificar el estado real, no asumirlo:
   `gh pr view <n> --json state,mergedAt`. Solo continuar si `state` es
   `MERGED` y `mergedAt` no es nulo.
7. `git switch develop && git pull --ff-only origin develop`.
8. Borrar la rama local: `git branch -d <rama>`. Si el remoto ya no existe,
   `git fetch --prune` antes.

### Prohibiciones que Keel no cruza nunca, en ningún flujo

- No borrar una rama remota con un PR abierto contra ella. Si hay que abandonar
  el trabajo, primero `gh pr close <n>`, y solo después borrar.
- No usar `git branch -D`. Si `-d` se niega, el merge no está completo: parar y
  reportar.
- No forzar el push a `develop`, `main` ni `master` bajo ninguna circunstancia.
- No resolver conflictos en `develop`. Siempre en la rama de trabajo.
- Si un PR aparece como `CLOSED` sin `mergedAt`, el trabajo NO está integrado:
  no borrar la rama y reportarlo al usuario.
- Si el PR lo abrió otra persona, Keel no lo mergea ni borra su rama.

---

## Comprobaciones nuevas en `keel-doctor`

Añade estos checks. Donde encaje mejor en `keel-verify`, ponlos ahí y dilo.

**Bloqueantes:**

- Agentes de rol lector en `.claude/agents/*.md` que declaren `Write`, `Edit`,
  `NotebookEdit` o `tools: *`. Es exactamente el agujero del incidente del
  30/07.
- Ramas locales o remotas ya contenidas en `develop` que sigan existiendo, si
  son más de tres: indica que la limpieza no se está ejecutando.

**Avisos:**

- Sesión corriendo en `bypassPermissions`: reportar como riesgo y recomendar
  reiniciar en `auto`, porque en ese modo los `deny` no se evalúan.
- Modo de permisos activo, y presencia de `.claude/settings.local.json` con
  `defaultMode` distinto de `manual`.
- Ausencia del bloque `deny` de la capa 2 en `.claude/settings.local.json`.
- Ramas ya contenidas en `develop` que sigan existiendo (una a tres).
- PRs abiertos cuya rama de origen ya no existe en remoto: es el estado
  inconsistente; hay que cerrarlos a mano.
- Ramas remotas sin actividad y sin PR asociado.

---

## Resumen de ficheros que previsiblemente tocarás

- `SKILL.md` — pasos de arranque (Regla 1), flujo de git (Reglas 2, 3, 5, 7),
  contención de agentes (Regla 6), avance sin paradas (Regla 4).
- `references/project-state.md` — plantilla de `docs/continuation-prompt.md`.
- `references/` de las fases donde aparezca `export PATH=... && ...` o
  instrucciones de merge y borrado de ramas.
- `.claude/agents/*.md` — listas de herramientas.
- `scripts/keel-doctor` (y `keel-verify` si procede) — checks nuevos.
- `scripts/` en general — retirada del prefijo `export PATH`.
- `docs/PROGRESS.md` y `docs/decisions.md` — registro de todo lo anterior.

## Al terminar

Dime qué has tocado, qué checks nuevos has añadido y con qué severidad, y si
algo de este encargo chocaba con lo que ya había. Mergea a `develop` y sube.
No toques `main`.
