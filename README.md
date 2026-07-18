# Coding Challenge | Agentic Task Runner

A FastAPI app where a single agent, backed by the OpenAI Agents SDK, selects and
executes tools to fulfill a user's request, with a transparent execution trace
and persistent task history.

## What it does

- Enter a task in plain language (e.g. "add 5 and 6, then uppercase the result").
- The agent decides which tool(s) apply, executes them in sequence, and returns
  a final answer.
- Every run is logged with a full, numbered execution trace and saved to history.
- Past tasks are viewable and re-inspectable from the UI.

## Tools implemented

| Tool | Purpose |
|---|---|
| `TextProcessorTool` | uppercase / lowercase / word count |
| `CalculatorTool` | addition / subtraction / multiplication / division |
| `WeatherMockTool` | mock weather for a city (no external API) |
| `UnitConvertor` *(bonus)* | km↔miles, °C↔°F, kg↔lbs |
| `DirectAnswerTool` | used when no other tool applies — see *Assumptions and tradeoffs* |

## How to run

Create and activate a conda environment:

```bash
conda create -n agent-runner python=3.12
conda activate agent-runner
```

Copy the environment template and add your OpenAI API key:

```bash
Copy-Item .env.example .env
```

Then edit `.env` and replace `your-key-here` with your real key.

Install dependencies and run:

```bash
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:8000` in a browser.

**Environment**: tested on Python 3.12.

## Dependencies

```
openai-agents
pydantic
fastapi
uvicorn
python-dotenv
```

No frontend build step — the UI is plain HTML/CSS/JavaScript (`static/index.html`),
served as a static file, calling the API directly via `fetch()`.

## Architecture

```
app.py       — FastAPI routes: POST /run, GET /history, DELETE /history
agent.py     — Agent definition and tool registration
tools.py     — The five @function_tool implementations
utils.py     — Formats the SDK's raw trace into the numbered step format
storage.py   — JSON-file persistence (list/save/clear tasks)
static/      — Single-page frontend: submit a task, view result + trace,
               browse and re-inspect history
```

`app.py` is intentionally thin — routing only. Tool logic, trace formatting,
and persistence are each isolated in their own module, so any one piece can
be tested or replaced independently.

More detailed and visual tracing is available on https://platform.openai.com/trace.

## AI assistance

I used Claude throughout this build — most heavily for the FastAPI backend
wiring and the frontend (HTML/CSS/JS), both areas I'm actively upskilling
in as part of a deliberate pivot toward more hands-on software and agent
engineering. The agent design itself — the tool schema, the
`tool_choice="required"` trade-off (found through testing, detailed below),
the `DirectAnswerTool` fix, and the overall module structure — were my
decisions, and I tested and debugged every part directly rather than
submitting generated code unreviewed. Happy to walk through any part of the
design or the debugging process in detail. I also used Claude to help me write this ReadMe file based on my input.

## Assumptions and tradeoffs

**Manual orchestration vs. native SDK tool-calling.** I initially built a
custom planner/executor design — a structured-output "plan" step, followed
by a separate deterministic execution loop. It gave finer-grained control
(the trace was hand-assembled, not derived from SDK internals), but proved
cumbersome: it required re-implementing multi-turn state tracking the SDK
already handles natively, and made it hard to add new functions due to the
rigid structure of the output schema parsed from the user input and fed into
the agent — every new tool meant adding more fields to that shared schema.

The manual orchestration of the agents, as expected, allows for more
customization — such as fine-grained control over exactly what appears in
the trace at each step, independent of what the SDK exposes internally, and
the ability to enforce custom logic between steps (like the "resolved, do
not retry" tracking I added to stop the planner from repeating a blocked
answer).

But manual orchestration also introduced a concrete bug: since it planned
every step upfront in a single call, before any tool had actually executed,
the planner would sometimes invent a placeholder like `"<result of step 1>"`
for a step that depended on a prior result it hadn't computed yet. Combined
with the added complexity of having to update several components everytime a new tool or change was introduced — overengineering the instructions explicitly
warned against — I switched to native `@function_tool` + `tool_choice="required"`,
which resolves this entirely: each tool call happens with real prior results
already in context, since the SDK's own conversation loop handles that
automatically.

**`tool_choice="required"` has its own trade-off.** Forcing every response
through a tool call fixes a different problem — the model silently skipping
a tool it judges "unnecessary" for a trivial sub-task — but without a
dedicated fallback, it also forces the model to call *some* tool even on
inputs with no real task (e.g. a bare "hi"), typically misusing whichever
tool seems closest. Fixed by adding `DirectAnswerTool` as an explicit,
honest "no other tool applies" option, with instructions naming exactly
when to use it instead of the others.

**Mock tools are intentionally simple.** `WeatherMockTool` returns a fixed
value; it isn't wired to `UnitConvertor` for temperature conversion, since
the mock returns a formatted display string, not a raw number a conversion
tool could consume. Fine for this scope, called out explicitly rather than
silently glossed over.

**Uppercasing a number is a known no-op.** `TextProcessorTool.upper()` on
a numeric string like `"11"` returns `"11"` unchanged, since digits have
no letter case. Found via testing a compound prompt ("add 5 and 6, then
uppercase the result") — technically correct behavior, but a UX gap I
didn't resolve (would need number-to-words conversion first).

**JSON-file persistence has no write locking.** `storage.py` reads,
modifies, and rewrites the whole file per save — fine for a single-user
demo, but two truly simultaneous requests could race and drop a write.
Named here rather than fixed, since adding locking would be more than this
scope needs.

## Limitations

This system uses an LLM to decide which tool applies and to determine when
a task is complete, which gives a transparent, step-by-step execution trace
and lets the agent decompose multi-part requests on its own. But that
flexibility depends entirely on the model making correct decisions — it can
still misjudge which tool applies, take an unnecessary step, or (as found
during testing) misuse a tool when none genuinely fits. The tools themselves
are also intentionally simple mocks, so this doesn't reflect the reliability
or scale demands of a production system.

## Possible improvements

- **Replace mock tools with real services** — e.g. a live weather API in
  place of `WeatherMockTool`, and wire `UnitConvertor` to consume its actual
  numeric output.
- **Independent validation of agent decisions**, rather than relying on the
  model to self-report correctly — schema validation, tool-authorization
  rules, or a secondary review step before a tool call executes.
- **Guardrails**: an earlier version of this project
  used an SDK `output_guardrail` to catch the model self-reporting an unsupported,
  non-tool answer. It didn't carry over into the final native `@function_tool`
  design, since `DirectAnswerTool` addresses the same failure mode more directly.
  A production version would likely still want a guardrail as an independent,
  code-level backstop — not relying solely on the model correctly choosing
  `DirectAnswerTool` every time.- **Automated tests** for each tool in isolation, and for the tool-selection
  logic against a fixed set of prompts.
- **File locking or a real database** for persistence, if this ever needed
  to support concurrent users. I've used Supabase in production for a
  real-time multi-agent system elsewhere; would likely reach for that here
  over the current JSON-file setup for the same reasons — hosted, easy to
  query, minimal ops overhead, and no risk of the write-race condition
  already flagged above.
- **UI Imporvements** can be done -- both in terms of the aestetics, and in terms of the way the reponses/traces are printed out -- to accommodate streaming and spacing the responses to complex prompts which lead to calling multiple agents, and show tool-calling interdependencies.

## Time spent

~10 hours total: ~5 hours experimentation (including an initial custom
planner/executor design that proved cumbersome — see *Assumptions and
tradeoffs* — before switching to native SDK tool-calling), and the
remainder modularizing the code into this FastAPI structure and building
and testing the frontend.
