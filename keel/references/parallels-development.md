# Parallels host — one shared `keel-development` VM, dedicated VMs only when earned, and a disk that stays under control

Load this at four moments: the Phase 1 preflight and Phase 2 §4, when the playground host is chosen; the Phase 5 scaffold, when it is stood up; a post-update reconciliation that finds `prlctl` on the machine; and any time the disk is the problem.

The rule in one line: **when Parallels is available, a project that fits on an ordinary hosting account gets a site on one shared VM, not its own machine.** A VM per plugin repeats the operating system, the web server, the database and the language runtime for no benefit, and each repeated copy is disk the user pays for.

`references/playground-recipes.md` still defines WHAT each project type must exercise: seed data, reset, gate zero, the driver, evidence. This file replaces only WHERE that runs. Every duty of the recipe survives the move.

## Choosing the host

Detect before proposing, without changing anything:

1. `command -v prlctl`, then `prlctl list -a` exit 0. The binary answers "installed"; the list answers "usable", because `prlctl` needs an edition and a licence that allow it. A failure is `NOT OPERATIONAL`, never `MISSING`.
2. `prlctl list -i keel-development`: does the shared VM already exist on this machine?

| Finding | Host |
|---|---|
| Parallels usable, project fits the shared VM | `parallels-shared` — the default; a site on `keel-development` |
| Parallels usable, project needs its own server | `parallels-dedicated` — a linked clone, or its own VM |
| No Parallels, or a platform it cannot host | `docker` — the existing recipe, unchanged (`wp-env`, Compose) |

Parallels is paid software and Keel is used on machines without it, so Docker stays a complete, supported path. Keel never asks anyone to buy a tool to use it, and never installs Parallels itself. The choice is recorded on the card's `Playground host:` line and in `docs/03-technical-plan.md` §Testing, with the reason.

## Shared or dedicated — the hosting test

**A project goes on the shared VM when it would work on an ordinary hosting account:** files under a vhost, a database, a cache prefix, and nothing that needs root. WordPress and WooCommerce plugins, PrestaShop modules and FacturaScripts plugins are the expected case. Web apps qualify when they meet the same test.

**It needs a dedicated VM when any of these is true:**

- it installs system packages, kernel modules or `systemd` services of its own, or is itself a product installed on a server (a self-hosted platform, an appliance, a load-testing target);
- it needs root, its own network stack, or a privileged port other than the shared web server;
- it changes global Apache, PHP, database or Redis configuration, or needs an engine or major version the shared VM does not carry;
- it needs another operating system, or a measurement that other sites would disturb (load tests);
- its test data cannot coexist with the shared VM's disk cap.

**The shared server configuration belongs to no project (UNBREAKABLE).** No project edits global configuration, installs a package or restarts a shared service for its own benefit. Needing to is the signal that the project fails the test and moves to a dedicated VM; a quiet change on the shared box breaks the projects next to it, and the failure appears somewhere unrelated.

## The VM — `keel-development`

- **OS:** Ubuntu Server LTS, in the host's native architecture, the current LTS whose PHP packages are confirmed available. Hosting is mostly Linux with Apache-compatible rules, and PrestaShop and FacturaScripts rely on `.htaccess`.
- **Parallels Tools are installed in the guest** (`prlctl installtools`, then the unattended installer). Shared folders need them, and they need `build-essential` and the kernel headers first.
- **Close the default sharing before anything runs on it (UNBREAKABLE).** Out of the box Parallels exposes the user's iCloud and Dropbox inside the guest, writable, under `/media/psf`. Run `prlctl set keel-development --shared-cloud off --smart-mount off --shf-host-defined off`, then `sudo systemctl restart prltoolsd` in the guest, because a sharing change does not reach the guest until that restart and the share can look empty. Verify with `ls /media/psf`: only the shares Keel added may appear.
- **Software:** Apache with PHP-FPM, several PHP versions side by side (the versions the Keel projects' support matrices promise, from a maintained packaging source), MariaDB, Redis, Composer, Node LTS, WP-CLI, Xdebug (off by default), Mailpit to capture outgoing mail, and `cloudflared` for `references/inbound-tunnel.md`.
- **Size:** 4 vCPU and 8 GB of RAM to start, raised when evidence says so. **Expanding disk with a declared maximum of 120 GB.** A cap is what makes growth a visible event instead of a surprise.
- **Provisioning is a script, never a sequence of hand-typed commands:** `keel-site provision` is idempotent, so a lost VM is rebuilt, not mourned. After it passes, take a snapshot named `baseline`.
- **Everything on it is disposable.** Sites are rebuilt from the repository and the seed. Anything that cannot be rebuilt does not belong here, and a shared-VM backup is therefore not needed.
- **Sandbox credentials only, synthetic data only**, as in every playground. Production credentials never enter this VM.

## Sites — one project, one isolated tenant

Each site gets its own vhost, document root, database and database user, PHP-FPM pool running as its own Unix user with the PHP version of its support matrix, Redis key prefix, and `open_basedir`. Isolation between sites protects test results and contains mistakes; it is not a security boundary against hostile code, which is why audits go elsewhere (below).

**Source reaches the VM through a read-only Parallels shared folder scoped to that repository**, bind-mounted read-only into the site (`wp-content/plugins/<slug>`, `modules/<slug>`, `Plugins/<slug>`). Share one repository at a time, never the whole projects directory. Build and install dependencies on the host, where it is fast; the VM reads the result.

- **A bind mount, never a symlink.** With a symlink WordPress resolves the plugin to its real path, so `plugin_basename()` returns `media/psf/...` and anything that depends on the plugin's identity breaks. Measured: 7 integration failures that disappeared with the bind mount.
- **Bind mounts do not survive a reboot.** A systemd oneshot ordered after `prltoolsd` restores them and waits for the share to have content. Without it the site still answers 200, with the plugin silently missing.
- **Tools that write into the source need redirecting.** PHPUnit runs with `--do-not-cache-result`, because the source is read-only.

**Parallel workers do not each get a site.** Workers develop and run only cheap static checks (`references/parallel-development.md`), and the full suite runs once per batch, so one project site plus one test site cover normal work. A slice that needs its own live drive at the same time as another gets a temporary `<slug>-<slice>` site, retired when the slice integrates.

## `scripts/keel-site` — the contract

Generated at the scaffold, in the same way as `scripts/keel-doctor`, only for projects on `parallels-shared`. Every command is non-interactive, reports what it did, returns nonzero on failure and reaches the VM over SSH with a dedicated key (`prlctl exec` also works once Parallels Tools are installed).

| Command | Does |
|---|---|
| `provision` | Creates or converges the VM; idempotent; never run implicitly by another command |
| `create <site>` | Creates the tenant, installs the platform at the pinned version, maps the plugin, removes the default content a bare install adds, warms the tests database, seeds |
| `start` / `stop` | Starts or suspends the VM. Suspending is refused while another project's work is using it |
| `url <site>` | Prints the site's address |
| `wp <site> <args>`, `sql <site> <args>` | Runs WP-CLI or SQL as that site's user |
| `test <site> <args>` | Runs PHPUnit from the site's plugin path, against a real load of the platform |
| `reset <site>` | Clean plus seed: the known state. Touches that site only |
| `retire <site>` | Removes the vhost, pool, mount, database and its user, cache keys, Unix user AND its group (the web server belongs to it, so `userdel` alone leaves it behind and the next `create` fails), and reports the space |
| `list` | Every site: project, last use, disk |
| `doctor` | VM state, versions, disk against the cap, sites unused for 30 days |

Two traps `create` must absorb, both measured:

- **`wp core install` on WordPress 7.0 and later adds a `wp_navigation` post.** Specs and seeds that rely on hard-coded IDs shift by one. Delete it and reset `AUTO_INCREMENT` before any plugin activates.
- **The first PHPUnit run on an empty tests database is not representative.** WooCommerce installs itself during that run, and two tests failed on it and passed on every later run, on both PHP versions. `create` runs a warm-up, and a result counts from the second run on.

`reset` is per site, deliberately. A VM snapshot restores every project's state at once, so **restoring `baseline` is a maintenance act, never a test step.**

### What replaces `wp-env`

| With `wp-env` | On `keel-development` |
|---|---|
| `.wp-env.json` pinned versions | Same versions, recorded in `docs/03-technical-plan.md` and read by `keel-site create` |
| `wp-env start` | `keel-site start` |
| `wp-env run cli wp …` | `keel-site wp <site> …` |
| `wp-env run tests-cli … phpunit` | `keel-site test <site> …`; the WordPress test library is installed per site, with the same PHPUnit major limit |
| `lifecycleScripts.afterStart` seed | `keel-site create` and `reset` |
| Playwright `webServer` starting wp-env | `baseURL` from `keel-site url`; Playwright stays on the host, headless, recorded as always |
| Debug log inside the container | The site's own `debug.log`, read back at each test point |

`scripts/playground-tunnel` keeps its contract: it forwards to the site's address and points that site's public URL at the tunnel, and every other site is untouched. `cloudflared` runs inside the VM. Measured: a forged payment notification arrived from the public URL and was refused, the site's URL was restored, and the public address stopped answering. The driver does not take over the user's screen: the VM runs headless.

A project's own scripts and specs that call `npx wp-env run` must move to `keel-site` as part of the migration. Tests that shell out to it are easy to miss, so search for them.

## Sites that talk to each other

Isolation separates files, databases and Unix users. **It must never separate the network.** Real systems span several sites: an API, a licence manager and a client that asks both questions and updates itself from one of them. They stay on the shared VM as separate tenants, and they must reach each other exactly as they would in production.

**`IP:port` does not work for this.** WordPress refuses, in `wp_safe_remote_*`, private addresses and every port except 80, 443 and 8080, and `download_url()`, which the updater uses, goes through it. So a test of an update or a licence call on that scheme fails for a reason production does not have. Measured: `A valid URL was not provided.`

**Connected sites use real names and real HTTPS:**

- **`<site>.keel.test` on ports 80 and 443**, name-based vhosts on the same Apache. `.test` is reserved and can never collide with a real domain.
- **Names resolve inside the VM** through its `/etc/hosts`.
- **A local certificate authority** signs a `*.keel.test` wildcard and is installed in the guest's trust store. It exists only in this VM and is never trusted on the host by default.
- **A development-only must-use plugin in each connected WordPress site** does two things for `*.keel.test` hosts and nothing else: returns true from `http_request_host_is_external`, and points `sslcertificates` at a copy of the system bundle inside the site's root, because WordPress ships its own bundle and `open_basedir` would hide the system one. It lives only on the VM, never in the repository's shipped code. **The product's own code stays unmodified**, so what is exercised is what ships.

Non-WordPress clients need only the names and the CA.

**A site stands alone on `IP:port` unless it declares partners.** That scheme needs no change on the host and is enough for a plugin that calls nothing else on the VM. The technical plan lists a project's partner sites beside its inbound calls, and those sites are created with names.

**The evidence for connected sites is a real exchange in both directions of the contract:** the call made through the same HTTP functions the product uses, from `php-fpm` as well as from the CLI because `open_basedir` applies only to the former, a negative case (an invalid licence gets no package), and the update applied through the platform's real updater. Then confirm isolation still holds: the client's PHP, its Unix user and its database user each fail to read the other tenant.

Reaching a named site from a browser on the host needs host-side name resolution, which needs the user's OK because it requires `sudo`: an `/etc/hosts` line, or a resolver for `keel.test`. Keel asks; it never edits host resolution silently. This route has not been measured yet.

## Machines: contract

**A machine is deleted as soon as it is no longer needed. Machines are never accumulated for specific tests and left there.** It applies equally to a Parallels VM or clone and to a Docker container, Compose stack, volume or image built for a project: the host does not change the rule. It has three parts:

- **Every machine declares its lease when created.** Parallels: `prlctl set <vm> --description "keel-lease: owner=<project> until=<YYYY-MM-DD|never>"`. Docker: `--label keel.lease.until=<YYYY-MM-DD|never>`, or the same label on each Compose service. A machine for a specific test takes the date that test ends. `never` is only for a machine with a named, ongoing use, such as `keel-development`.
- **The session that created a machine for a job deletes it when the job ends,** in that session. Parallels, after checking `keel-site list` shows no dependants: `prlctl stop <vm> --kill`, then `prlctl delete <vm>`. Docker: `docker compose down -v --rmi local`, or `docker rm -f` with that test's volumes and images, by name and never with a global prune. An audit, matrix or load-test machine never outlives its check, and reusing one for a later test needs a lease that says so.
- **A machine belongs to its project, and that project decides.** A session never deletes a machine it did not create, and never touches another project's. For its own project's machines it declares the lease or proposes deletion to the user, once, at reconciliation. `sweep` lists every machine with an expired lease or none at all, on both hosts, and never deletes one, because a script cannot know whether it is still wanted. With the Docker daemon stopped it cannot see containers.

## Dedicated VMs — linked clones first

A project that fails the hosting test starts from a **linked clone**, which stores only what differs from its parent:

```
prlctl snapshot keel-development --name clone-base
prlctl clone keel-development --name <project>-play --linked
```

A linked clone depends on its parent. Deleting or rebuilding the parent breaks every clone, so `keel-site list` shows the dependants and `provision` refuses to replace a parent that has any. Where the project genuinely shares nothing with the template, or will outlive it, a full VM is the honest choice; record why in the technical plan.

Dedicated VMs follow the same rules as everything else here: a declared disk maximum, a reset, sandbox credentials only, and retirement when the project goes idle.

**Disposable linked clones also carry two jobs that must not run on the shared VM:**

- **Security audits.** `references/security-audit.md` executes target code in the playground. On a shared VM that code sits beside other projects' sites and sandbox credentials, so an audit that executes anything runs in a throwaway clone, deleted when it ends.
- **Version matrices.** MariaDB and MySQL do not coexist cleanly on one system, and neither do two major versions of an engine. The less common combination runs in a clone, for the length of that check.

## Migrating a project from Docker

The trigger is the post-update reconciliation (`references/project-state.md`, standing check 3), which puts the migration in the catch-up plan. The user approves it per project, and that OK covers the deletion in step 6, because the deletion is the point of the migration. It is never bundled silently with other rows, and it is recorded as a D-entry that supersedes any earlier decision choosing `wp-env` or Docker.

**The migration is a task, not a reconciliation step.** It takes real time and depends on a working VM, so it does not hold the reconciliation or `Keel baseline:` back: an approved row is recorded as `Playground migration pending` in PROGRESS.md open items and runs at the start of the next work on that project.

Do not start while a parallel run or an open sprint batch is in flight. A running hotfix goes first.

1. **Classify** with the hosting test and record the result.
2. **Inventory what Docker holds for this project:** containers, volumes and images, identified by the Compose project label (`com.docker.compose.project`) or the `wp-env` instance hash. Record names and sizes.
3. **Protect what the seed cannot rebuild.** Look inside every data volume. Dump databases to a gitignored path outside the volume. A large volume is a question, not a formality: find out what it holds and why before anything is moved.
4. **Stand up the site** with `keel-site create` or a linked clone.
5. **Verify on the new host.** `scripts/keel-doctor --check`, gate zero, the full suite, and each main flow driven live, with the inbound tunnel where the plan lists one. Compare against the last result on Docker; the same failures may exist on both, but nothing may be newly red. Update `docs/03-technical-plan.md`, `docs/playground.md`, the affected scripts and the card.
6. **Only then delete, and only what step 2 listed:**
   - **Never `docker system prune` or any machine-wide command.** The other projects live on the same daemon.
   - Remove this project's containers, then its volumes.
   - Remove an image only when no remaining container uses it. `mariadb:lts` and its like are shared.
   - Keep the repository's `.wp-env.json` or Compose file when CI or another contributor uses it. Otherwise delete it in a commit.
7. **Report** the space freed and record the migration, with its evidence, in `docs/05-test-points.md` and `docs/decisions.md`.

**A migration that fails verification leaves Docker intact.** The row stays open with the reason, the project keeps working where it was, and the failure becomes an L-entry. Destroying the working environment before the new one is proven is the one mistake this procedure exists to prevent.

## What the first real project proved

Pilot on an existing WooCommerce plugin, as two sites on one VM, with Docker running the same tree as the comparison:

| Check | Result |
|---|---|
| Floor site (PHP 7.4, WordPress 7.0, WooCommerce 7.4): unit, integration, browser | 41, 410 and 67 of 67 passed |
| Ceiling site (PHP 8.4, WordPress 7.1, WooCommerce 11.2): unit, integration, browser | 41 and 410 passed; browser 63 of 67, the same 4 failures on Docker |
| VM disk with both sites and the suites run | 8.6 GB |
| Reboot | Services, share and mounts return |
| Public tunnel into one site | Reached from outside, forged notification refused, URL restored, tunnel closed |
| API, licence manager and client as three tenants | Update applied through the real updater; isolation held |

**The comparison is what made these numbers mean something.** Run the same tree on the old host before calling a failure new or old. Twice here the plausible explanation was wrong, and only the comparison and a repeated run found the real cause.

## The disk — what actually fills it

Measured on a real development machine with 695 GB in use, the virtual machines were not the main cost:

| Source | Size |
|---|---|
| Parallel-development worktrees left behind (253 retired, 113 GB of real free space gained) | 208 GB by `du` |
| Language build cache | 96 GB |
| Virtual machines | 131 GB |
| Docker | 63 GB |

So every rule below ships together with the shared VM, and none of them depends on Parallels.

- **No dead traces.** SKILL.md's rule applies to every item below: what no longer serves is removed when its work ends, verified and never forced.
- **Worktrees are retired, not accumulated.** `keel-parallel reap-worktrees` at each batch verification and sprint close (`references/parallel-development.md`, "Retiring worktrees"). Each one carries its own `node_modules` and `vendor`.
- **Sites and VMs are retired.** A site or VM goes when its use ends ("Machines: contract"). When a project goes idle, or `keel-site doctor` lists a site unused for 30 days, propose `retire`. A rebuild costs minutes; a forgotten site costs disk for ever.
- **Expanding disks do not give space back by themselves.** Deleting files inside a VM frees it there, not on the host. With the VM stopped, compact it: `prl_disk_tool compact --hdd <path>.hdd`.
- **Snapshots hold deleted data alive.** Keep `baseline` and `clone-base`; delete the rest once they have served.
- **Build caches are capped by review, not left to grow.** `go clean -cache`, `brew cleanup`, and the equivalents regenerate everything they delete. Above 20 GB, the doctor reports the size and the command; it runs under `--fix`, with the user's OK, because the next build pays the time.
- **Before touching any of it, measure.** The biggest number is rarely where anyone expected it. `du` first, then a decision.

## Definition of done (this reference)

- The card carries `Playground host:`, and the choice rests on detection, not on an assumption.
- A `parallels-shared` project passed the hosting test, has its isolated tenant, and runs every duty of its recipe through `scripts/keel-site`; no project changed the shared configuration.
- A dedicated VM records why it failed the test, and its disk has a declared maximum.
- Security audits that execute code ran in a throwaway clone, never on the shared VM.
- A migrated project deleted its Docker resources only after verification on the new host, only those in its inventory, and left the evidence.
- Worktrees, sites and VMs that are no longer used were retired, and the doctor reports what remains.
