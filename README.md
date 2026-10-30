<div align="center">

# HoloAeon

### A Zero-Dependency, Bio-Inspired Cognitive Framework for General-Purpose Multi-Agent Systems

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-green.svg)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/dependencies-0-success.svg)](pyproject.toml)
[![Tests](https://img.shields.io/badge/tests-24%20passed-success.svg)](#-testing)
[![SelfTest](https://img.shields.io/badge/selftest-16%2F16-success.svg)](#-testing)

[English](README.md) · [中文](README.zh-CN.md)

</div>

---

HoloAeon is a **pure standard-library, fully offline, deterministic** cognitive framework
for building multi-agent systems on top of any large language model. It provides a layered
set of primitives — envelopes, a message bus, agents, skills, memory, a heartbeat scheduler,
a security guard, an adaptive collaboration graph, a parallel actor cluster, hyperdimensional
representations, and a model-adapter layer — plus **nine ready-to-use domain packs** that span
the everyday work of knowledge professionals, including a deterministic **optimization &
self-organizing search** layer (see [ALGORITHM.md](ALGORITHM.md)).

> **Naming.** *Holo* (whole, holographic) + *Aeon* (a high-dimensional, timeless being in
> Gnostic cosmology). It signals the project's inspiration: a system in which every local part
> carries a summary of the whole, and structure self-organizes across scales.

> **On the biological vocabulary.** Terms such as "heartbeat", "skin", "cytoskeleton",
> "meridian", and "Hebbian field" are **cognitive-architecture metaphors**. They describe
> synchronization, boundary control, routing, structural support, and self-organization in a
> multi-agent system — not biological organs or medical structures. A precise
> [metaphor → engineering-concept map](#-metaphor--engineering-concept-map) is included below.

---

## Why HoloAeon

Most agent frameworks start at a high level ("give me a crew of agents") and hide the
foundational primitives. HoloAeon is built **bottom-up**, so every high-level mechanism is a
composition of small, inspectable, testable parts.

| Principle | What it means in practice |
|---|---|
| **Zero dependencies** | Only the Python standard library. `pip install` pulls in nothing; `dependencies = []`. |
| **Offline by default** | No network calls, no bundled API keys, no telemetry. Runs on an air-gapped machine. |
| **Deterministic** | Given the same inputs, every run produces the same outputs (reproducible, `DIFF=0`). |
| **Logical, sparse topology** | The large matrix is a *logical* coordinate space. It is never pre-allocated; nodes activate sparsely. |
| **Orthogonal mechanisms** | Each layer has one responsibility; synchronization, routing, security, and learning do not overlap. |
| **Model-agnostic** | A dedicated adapter layer lets you point the framework at any local, private, or cloud model. |

---

## Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│                      Application / User                      │
├─────────────────────────────────────────────────────────────┤
│  Domain Packs  writing · literature · research · data        │
│                 growth · business · quant · optimization     │
├─────────────────────────────────────────────────────────────┤
│                        Kernel (facade)                       │
│        submit · collab · choose_agent · tick · health         │
│   cold/hot plug · internal fusion · external fusion          │
├──────────────┬──────────────────────────────────────────────┤
│  Scheduler   │  Guard (L1–L8)        Memory (3 layers)        │
│  heartbeat   │  boundary & safety   working / long / archive │
├──────────────┴──────────────────────────────────────────────┤
│            Adaptive Graph  (hexagonal, Hebbian)              │
│   shortest path · bottleneck · fan-in · self-organize ·      │
│   root-cause · cycle detection                               │
├─────────────────────────────────────────────────────────────┤
│    Bus (topics / addresses / routes)  ·  Envelope             │
├─────────────────────────────────────────────────────────────┤
│  Agent + Skill Registry      Hypervector Space (HRR)         │
├─────────────────────────────────────────────────────────────┤
│  Actor Cluster (parallel)        Model Adapter (any LLM)     │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Primitives

### `Envelope` — the universal message
Every communication is a self-contained envelope with sender, recipient, topic, payload,
metadata, a trace, and a `mode` tag (`simulated` by default). Envelopes support
`create`, `broadcast`, `reply`, `forward`, visited-node tracking, and dict round-trip.

### `Bus` — the message backbone
A thread-safe bus with three delivery patterns:
- **Pub/Sub** — many subscribers per topic;
- **Direct addressing** — `register_address("id", handler)`;
- **Routes** — a topic's broadcast can be redirected to a specific address.

Handler exceptions are converted into structured failure receipts — they never crash the bus.

### `Skill` & `SkillRegistry`
A skill is a named, deterministic callable with a manifest (description, tags, input/output).
The registry matches natural-language requests to skills using token overlap and tag weights,
and returns ranked candidates.

### `Memory` — three-layer store
| Layer | Role |
|---|---|
| `working` | Current task context; small capacity; can be promoted on `consolidate` |
| `longterm` | Cross-task knowledge with strength and tags |
| `archive` | Stable facts and reference material |

Provides `put/get/recall` (token-based relevance), `consolidate`, `decay`, and JSON
persistence. Thread-safe.

### `Agent`
An agent owns a profile, a skill registry, and a bounded set of skills. It decides which skill
matches a request, invokes it with **signature-aware argument binding** (matching parameters by
name, with int/float coercion), and returns a structured result. Agents also expose `suggest`,
`snapshot`, and `reply_to`.

---

## Core Mechanisms

### `Scheduler` — the heartbeat
A periodic synchronization signal. Each tick performs liveness detection, context refresh,
state snapshots, consistency checks, weight decay/enhancement, isolation of degraded nodes,
and re-election. The default configuration uses 70 heartbeat bodies over a fixed id range,
with 768-dimensional state vectors and exponential smoothing (α = 0.18) — all configurable.

### `Guard` — the security boundary (L1–L8)
A layered, **semantic** boundary controller. It admits or blocks envelopes based on
permissions, structural validity, and dangerous-pattern detection (e.g. `os.system`,
`eval`, credential access). Every decision is a `Verdict` with a layer and reason, and is
optionally written to an audit log.

### `AdaptiveGraph` — the collaboration graph
Agents are placed on a **hexagonal lattice** (the radius-2 tiling yields 19 positions).
The graph supports:
- **Dijkstra shortest path**, with prior flow edges as guidance;
- **Load application, fan-in, and bottleneck detection**;
- **Cycle detection** (the hexagonal tiling naturally contains rings);
- **Hebbian step** — co-activated nodes strengthen their shared edge;
- **Self-organization** — nodes with similar state vectors grow weak links;
- **Root-cause analysis** — trace the heaviest upstream edges from a bottleneck.

### `Cluster` — parallel actors
A cluster wraps agents as mailbox-based actors and runs many tasks concurrently behind a
barrier, reporting `ok`, `faults`, `consistent`, elapsed time, and per-task results. It
supports one level of forwarding for resilient routing.

### `HypervectorSpace` — hyperdimensional representation
A self-contained Holographic Reduced Representation (HRR) built on a **hand-written radix-2
Cooley–Tukey FFT** (no NumPy). It provides `make`, `bind` (circular convolution), `unbind`
(approximate inverse), `bundle` (addition), `permute`, and `cosine` similarity — useful for
fast, robust associative memory and analogical binding.

### `ModelAdapter` — any model, one interface
Register model backends (local, private, or cloud) with cost, context window, latency, and
modality. The adapter routes by **8 strategies** (cheapest, largest-context, lowest-latency,
modality-match, …), formats messages across **10 masking/message formats**, and records
**8 usage metrics** for cost and capacity tracking.

---

## The Nine Domain Packs

HoloAeon ships nine packs that cover the full spectrum of knowledge work. Installing all of
them yields **25 agents, 47 skills, and 9 end-to-end workflows**.

| Pack | Example capabilities | Roles |
|---|---|---|
| **writing** | outline, word count, readability, structure check | planner, drafter, editor |
| **literature** | search planning, reading notes, quality review | searcher, reader, reviewer |
| **research** | study design, sample size, hypothesis, analysis plan | designer, executor, analyzer |
| **data** | cleaning, descriptive stats, profile, reporting | cleaner, analyst, reporter |
| **growth** | SMART goals, habit planning, weekly review | goal coach, habit coach, review coach |
| **business** | business model canvas, KPI, unit economics, risk | strategist, operator, risk manager |
| **quant** | returns, Sharpe, drawdown, risk metrics | analyst, researcher, risk |
| **optimization** | golden-section, gradient descent, Newton, conjugate gradient, simplex, penalty, genetic algorithm | line searcher, gradient solver, global solver |
| **gaoyi** | NL→HASM compile, VM execution, assembly replay (deterministic intent routing) | gaoyi translator |

Each pack is a self-contained `DomainPack` and can be installed independently. The
optimization pack runs only on **built-in safe benchmarks** — it never evaluates arbitrary
expressions. See [ALGORITHM.md](ALGORITHM.md) for the full algorithmic mapping. The
**gaoyi** pack deterministically compiles natural-language requests into the project's own
HASM assembly and runs them on a built-in VM; HASM is not a real CPU instruction set and
unknown intents are reported as `UNKNOWN` rather than guessed.

### Cross-cutting extension packs (10th – 14th)

These packs are **registered outside `PACK_ORDER`** on purpose: they add capability
without adding agents, so the nine-pack totals above (25 agents / 47 skills) stay stable.
They are reachable through `get_extra_pack(key)` and verified separately by
G18 / G19 / G20 / G21 / G22.

| Extra pack | What it adds | Skills | Roles | Workflows |
|---|---|---|---|---|
| **sovereignty** | anti-algorithm cognitive shaping: 16-domain query forging, anti-label strategy, 23 protocol families, 10 platform families × 13 duties | 17 | 0 | 5 (R0–R4) |
| **subdistill** | SD-Distill sub-discipline distillation: 16 domains → 127 sub-disciplines → SKC knowledge cards, seven-stage pipeline, seven auxiliary losses, temperature curriculum | 15 | 0 | 7 (S1–S7) |
| **omnilife** | Omni-Life everyday sovereignty: wardrobe / food / shelter / mobility / learning / SaaS, anchored on the 127 sub-discipline codes — skin-layer inducer folding, meridian local hand-off, deterministic life planners | 18 | 0 | 6 (L1–L6) |
| **omnicore** | Omni-Core cognitive engine rewrite: addressing invariants, pure-function heartbeat, SKC distillation, Hebbian update, skin gate, self-declaration, whitepaper outline | 20 | 0 | 6 (M1–M6) |
| **metab** | METAB governance layer: six-chromosome genome admission, four-question state classification, eight-stage lifecycle, three-tier authorization (fail-closed), gut dual channel, trust radius, combination whitelist, redlines | 26 | 0 | 8 (T1–T8) |

`subdistill` keeps the mother matrix dimensions **unchanged** and asserts it in code:

```
127 × 10  sub-discipline slots + 61 reserved rows      = 1331 rows
127 × 855 sub-discipline nodes + 56 global co-ordinators = 108641 nodes
```

`omnilife` **adds no rows and no nodes** — it only consumes the same 127 codes as life-domain
anchors, and `pack_summary()["addressing_unchanged"]` proves it. It is deliberately narrow
about what software may do in the physical world:

- price watching is a **blank ledger the human fills in** (`concurrent_probe=False`,
  `proxy_switch=False`); concurrent multi-endpoint probing, proxy switching and price scraping
  are refused by name;
- inducement folding emits **rules for the platform's own "not interested / mute" controls**,
  never DOM injection (`dom_injection=False`);
- cross-SaaS routing is a **manual export → local archive → human reference** hand-off
  (`api_calls=0`, `network=False`);
- nutrition output carries `dose_any=False`, `individual_medical_advice=False` and a fixed
  disclaimer; travel routing runs on a user-supplied weight graph, never live traffic.

`omnicore` takes a single-file "digital-life engine" draft and rewrites it as ordinary
deterministic software. **Five defects in the draft were reproduced, then fixed** (recorded in
`CORRECTIONS`, asserted by G21): a sparse table silently overwritten by
`self._cells = profile`; `self._inbox.append(...)` on a `defaultdict`; an empty `route =`
assignment that makes the module a `SyntaxError`; `numpy` + `np.random` contradicting a
"zero-dependency" claim; and a daemon thread plus sqlite writes plus a non-existent PyPI
package name. The rewrite keeps the *design intent* and drops the *unverifiable parts*:

- heartbeat is a **pure function** `heartbeat_pulse(epoch)` — no thread, no sleep, no timer;
- checkpoints return `persistence="host_managed"` and write nothing to disk;
- the 5% temperature burst uses `sha256(epoch) % 100 < 5` instead of a random source;
- "digital life / breath / immunity / city-state" is labelled `metaphor=True` everywhere;
- browser plug-ins that retarget streaming/e-commerce recommendation slots are refused.

`metab` turns a governance spec into **decidable checks**. It executes nothing: it answers
"may this symbiote enter, which state does this change belong to, what is missing, why is it
refused". Each of its 26 skills returns a verdict, and every verdict cites the axiom it serves.

- admission requires **all six chromosomes** (phenotype / purity / lineage / toxicity /
  energy / rhythm); a missing degradation path or a missing attention quota is a veto;
- state classification is four questions in fixed precedence, and an **unmatched change
  defaults to the conservative circulation state**, never to the hot state;
- eight internal contradictions in the spec are listed with two resolutions each and one
  adopted choice (`CONFLICTS` K1–K8) — e.g. irreversible points are pushed *outside* the
  system (K1), and "one-key disable" means stop-and-fail-over, not skeleton rollback (K6);
- lineage is a verifiable hash chain; a tampered node is reported by index and the chain
  is judged untrusted;
- combination safety runs on a whitelist: unknown pairs **do not take effect**, amplified
  pairs need a whole-combination review.

All five packs are offline, deterministic and zero-dependency. `subdistill` ships the 127-item
taxonomy in `data/taxonomy_127.json` and forces a medical disclaimer gate on every MED/TCM
artifact; `analogizes` relations must carry a counterexample before they may be called
verified.

### Versioned releases (add-only, never overwritten)

Every release ships as a versioned zip under [`releases/`](releases/RELEASES.md), with a
`SHA256SUMS.txt` next to it and an entry in the version index. Older zips are kept as-is, so
any version can be unpacked, self-tested and run independently of the current checkout.

```bash
python scripts/make_release.py          # -> holoaeon_v<version>_<date>.zip (idempotent)
```

See **[releases/RELEASES.md](releases/RELEASES.md)** for the version index, per-version
highlights, upgrade path and verification records.

---

## Quick Start

### Requirements
Python 3.8+ only. No `pip install` is required to use the package directly.

### Option A — use from a clone
```bash
git clone https://github.com/weideyouni/holoaeon.git
cd holoaeon
python examples/01_basic_matrix.py
```

### Option B — installable (still zero dependencies)
```bash
pip install -e .
```

### Minimal example
```python
from holoaeon import Kernel
from holoaeon.agent import Agent

k = Kernel()
k.skills.register_fn("echo", lambda task: "echo:" + task,
                     description="echo the text")
k.register_agent(Agent("a1", "echoer"))

result = k.submit("please echo hello")
print(result["results"][0]["output"])   # echo:please echo hello
```

### Install a domain pack
```python
from holoaeon import Kernel
from holoaeon.packs import DataPack

k = Kernel()
DataPack().install(k)

stats = k.submit("basic stats", to="data_analyst",
                 args={"csv_text": "a,b\n1,10\n2,20\n3,30"})
print(stats["results"][0]["output"])
```

---

## Local Launcher — Cold/Hot Plug & Internal/External Fusion

A single executable entry point demonstrates the framework's pluggability and fusion
protocols on your own machine:

```bash
python scripts/launch_local.py status                 # health snapshot
python scripts/launch_local.py demo                   # full fusion walkthrough
python scripts/launch_local.py run "task text"        # submit a task (auto-select agent)
python scripts/launch_local.py hotplug optimization   # load a pack at runtime, no restart
python scripts/launch_local.py selftest               # 16 self-test groups
```

- **Cold plug** — at startup, `bootstrap()` installs all domain packs, binds the internal
  collaboration graph, and registers the external model backends.
- **Hot plug** — while the system is running, a new pack is installed without a restart
  (the `hotplug` command adds 7 skills in place).
- **Internal fusion** — components communicate in-process via envelopes/bus, are orchestrated
  by the graph, share memory, and synchronize on the heartbeat, all behind the guard.
- **External fusion** — the `ModelAdapter` registers local and cloud backends and makes
  offline routing decisions (e.g. cheap task → local, long-context task → cloud).

---

## Deployment Topologies

HoloAeon's design scales from a single laptop to a distributed cluster:

| Topology | How it maps |
|---|---|
| **Personal laptop** | Run the `Kernel` in-process; point the `ModelAdapter` at a local model. Fully offline. |
| **On-premise / private server** | Host agents as long-running actors behind the `Guard`; keep memory and data inside the trust boundary. |
| **Cloud / distributed** | Run the `Cluster` across nodes, use the `Bus` for inter-node routing, and route to cloud models via the adapter — each message still passes the guard and is tagged with its mode. |

The same primitives compose in all three; only the deployment boundary changes.

---

## Project Structure

```
holoaeon/
├── spec.py            # identities, configuration dataclasses, lock checks
├── envelope.py        # universal message envelope
├── bus.py             # pub/sub, addressing, routes
├── skill.py           # skill manifest & registry, matching
├── memory.py          # three-layer memory
├── agent.py           # agent primitive, signature-aware skill invocation
├── scheduler.py       # heartbeat scheduler
├── guard.py           # L1–L8 security boundary
├── kernel.py          # top-level facade
├── graph.py           # adaptive hexagonal collaboration graph
├── cluster.py         # parallel actor cluster
├── hypervector.py     # HRR + hand-written FFT
├── model_adapter.py   # any-LLM adapter layer
├── redline.py         # AST red-line scanner
├── selftest.py        # G1–G17 self-test suite
└── packs/             # nine domain packs (incl. optimization.py, gaoyi_pack.py)
examples/              # four runnable walkthroughs
tests/                 # unittest suite
scripts/               # red-line scanner & local launcher
docs/                  # in-depth documentation
ALGORITHM.md           # cognitive optimization & self-organizing search
```

---

## Metaphor → Engineering Concept Map

| Metaphor | Engineering concept |
|---|---|
| Heartbeat | Periodic scheduler tick for synchronization, snapshots, and health checks |
| Skin | Layered security guard / boundary controller |
| Meridian | Semantic routing network connecting tasks, tools, memory, and models |
| Cytoskeleton | Structural support: lifecycle, persistence, registry, recovery |
| Hebbian field | Co-activation-based weight adaptation (self-organizing links) |
| Resonance | Dynamic alignment of agents via shared state and relevance |
| Holographic | Each local node carries a partial summary of global state |

These are organizational metaphors only; the empirical machinery is implemented as ordinary,
deterministic software.

---

## Testing

```bash
# Self-test suite (G1–G22)
python -c "from holoaeon.selftest import run_all; print(run_all(verbose=True))"

# Unit tests
python -m unittest discover -s tests -v

# Red-line scan (network / dependency / dangerous-call checks)
python scripts/redline_scan.py
```

Current status: **22/22 self-test groups pass**, **25 unit tests pass**, and the red-line
scan reports **zero violations** across all source files.

---

## Relationship to Other Frameworks

HoloAeon does not aim to replace LangChain, LlamaIndex, AutoGen, CrewAI, Semantic Kernel, or
similar projects. It focuses on the layer below orchestration — **cognitive topology,
deterministic primitives, and self-organizing collaboration**. It can serve as:
- an upper cognitive protocol;
- a multi-agent matrix coordinator;
- a semantic communication bus;
- a self-organizing collaboration testbed;
- a model-agnostic cognitive foundation for applications.

---

## Roadmap

- **v0.1** — Core primitives, mechanisms, seven domain packs, self-test, and docs.
- **v0.2** — Optimization & self-organizing search layer, local launcher, cold/hot plug,
  and internal/external fusion protocols.
- **v0.3** — GaoYi pack: deterministic NL→HASM compilation and a built-in VM for
  intent routing (nine packs).
- **v0.4** — Two cross-cutting extension packs: **sovereignty** (cognitive sovereignty:
  17 skills, 0 agents, R0–R4) and **subdistill** (SD-Distill: 127 sub-disciplines,
  seven-stage distillation, seven auxiliary losses, C1–C4 temperature curriculum).
  Twenty-five agents / forty-seven skills of the nine-pack core remain unchanged.
- **v0.5** — Third extension pack: **omnilife** (everyday sovereignty across wardrobe,
  food, shelter, mobility, learning and SaaS; 18 skills, 0 agents, L1–L6). Adds no rows and
  no nodes; refuses concurrent price probing, proxy switching and DOM injection by design.
- **v0.6** — Fourth extension pack: **omnicore** (the Omni-Core engine draft rewritten as
  deterministic software; 20 skills, 0 agents, M1–M6). Five defects of the draft reproduced
  and fixed; pure-function heartbeat, host-managed checkpoints, `metaphor=True` throughout.
- **v0.7** — Fifth extension pack: **metab** (the METAB metabolism layer as decidable
  governance; 26 skills, 0 agents, T1–T8). Six-chromosome admission, four-question state
  classification, eight-stage lifecycle, three-tier authorization, gut dual channel, trust
  radius, combination whitelist; eight internal contradictions resolved explicitly (current).
- **v0.8** — Pluggable persistence backends and inter-node bus transports.
- **v0.9** — Declarative graph/topology definitions and a pack-authoring toolkit.
- **v1.0** — Stable cognitive framework with a frozen API and full documentation.

---

## Contributing

Issues and pull requests are welcome. Before submitting, please read the relevant docs in
`docs/` and ensure the self-test, unit tests, and red-line scan all pass. When opening a PR,
include a description of the change, affected modules, tests/examples, and documentation
updates. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

Licensed under the **Apache License 2.0**. You may use, modify, distribute, and commercially
apply the software while retaining the copyright and license notices. See [LICENSE](LICENSE).

---

## Disclaimer

The biological and cosmological vocabulary in this project is metaphorical and used solely to
describe the synchronization, boundary, routing, support, and self-organization of multi-agent
software. It is not medical, biological, or clinical advice, and it does not claim to model real
organs, physiological structures, or supernatural entities. All simulated receipts are tagged
`simulated`; **simulation is not proof**, and human judgment remains the final authority.
