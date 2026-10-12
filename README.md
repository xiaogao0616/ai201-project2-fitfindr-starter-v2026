# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> The three tools and the planning branch are implemented. The query above
> returns outfit suggestions and a fit card when the model is available.
>
> The first five sections document the Unit 3 build. The sections after the
> Unit 4 marker document the test: run logs, verdicts, trace, and the fix.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr lets a user search thrift listings using a clothing description, size,
and optional maximum price. It selects the best matching listing and uses the
user's wardrobe to suggest an outfit. It then creates a fit card for the
selected item and outfit. If no listings match, the agent stops and explains
that the user should change the search conditions.

---

## Tool Inventory

### `search_listings`

- **What it does:** Searches listings by description keywords, optional size, and optional maximum price.
- **Inputs:** `description` (str), `size` (str or None), `max_price` (float or None)
- **Returns:** A list of listing dictionaries, sorted by keyword relevance, containing `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.
- **Matching rules:** Case-insensitive keyword overlap across title, description, category, style tags, colors, and brand; common stopwords are ignored. Any positive overlap qualifies. Higher scores come first; ties preserve data order. Returns at most `config.SEARCH_RESULT_LIMIT` (10) items. Price is an inclusive ceiling. Sizes match complete slash-separated tokens (M matches S/M, L does not match XL); parenthetical notes are ignored, and one-size items match any requested size.
- **When it has nothing:** Returns an empty list `[]` when no listings match, including descriptions with no searchable keywords.
- **Over MCP (Unit 4):** Registered in `mcp_server.py`; `run_agent()` calls it through `mcp_client.call_tool`. Results are identical to the direct call, including `[]`.

### `suggest_outfit`

- **What it does:** Uses the selected clothing item and the user's wardrobe to suggest one or two outfits.
- **Inputs:** `new_item` (dict), `wardrobe` (dict)
- **Returns:** A non-empty string containing outfit suggestions or general styling advice.
- **When it has nothing:** If the wardrobe has no items, returns general styling advice for the selected item.

### `create_fit_card`

- **What it does:** Creates a short social-media-style caption for the selected item and outfit.
- **Inputs:** `outfit` (str), `new_item` (dict)
- **Returns:** A two-to-four sentence string mentioning the item, price, platform, and outfit vibe.
- **When it has nothing:** If `outfit` is empty or whitespace, returns a descriptive message instead of raising an error.

---

## Planning Loop

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` explaining what the user could change and stop. Otherwise, select the first result and pass it to `suggest_outfit`, then pass the outfit suggestion and selected item to `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regular expressions extract the size and maximum price. The remaining text becomes the description.

**What moves through the session:** The query is parsed into `parsed`; search results go into `search_results`; the first result goes into `selected_item`; the outfit result goes into `outfit_suggestion`; and the final caption goes into `fit_card`.

---

## Sample Run

Captured from terminal runs. Normal runs may reuse cached model responses; the
three-card variation check explicitly disables caching. These are build checks,
not the five-trial Unit 4 acceptance evaluation.

**Full query**

```text
$ python app.py ask 'vintage graphic tee under $30'
Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here are two practical, Y2K-inspired outfits using the new butterfly baby tee and pieces from your wardrobe:

### Outfit 1: Classic Y2K Streetwear
This look plays on the iconic early 2000s proportion play of a fitted top and baggy bottoms.
* **New Item:** Y2K Baby Tee — Butterfly Print
* **Wardrobe Pieces Used:**
  * **Baggy straight-leg jeans, dark wash** (w_001)
  * **Chunky white sneakers** (w_007)
  * **Black crossbody bag** (w_010)

### Outfit 2: Edgy Casual Contrast
This outfit tones down the sweetness of the butterfly tee by pairing it with earth tones and utilitarian outerwear, creating a balanced, everyday look.
* **New Item:** Y2K Baby Tee — Butterfly Print
* **Wardrobe Pieces Used:**
  * **Wide-leg khaki trousers** (w_002)
  * **Vintage black denim jacket** (w_006)
  * **Black combat boots** (w_008)

  Fit card: Channel that early 2000s streetwear energy by pairing this Y2K Baby Tee — Butterfly Print with dark wash baggy jeans and chunky white sneakers. For just $18.0 on depop, it's the ultimate fitted top to balance out relaxed proportions. Grab it now and complete the look with your favorite black crossbody bag!

0 model calls this session, 2 served from cache
```

**search_listings**

```text
$ python -c "from tools import search_listings; print(search_listings('graphic tee', size='M', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}]
```

**suggest_outfit**

```text
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Here are two practical, everyday outfits featuring the new Vintage Levi's 501 Jeans:

### Outfit 1: Casual & Cozy Everyday
A relaxed, effortless look that leans into vintage basics. The fitted tank balances the oversized sweater for an easy high-low silhouette.

* **New Item:** Vintage Levi's 501 Jeans — Medium Wash
* **Wardrobe Pieces Used:**
  * White ribbed tank top (`w_003`)
  * Oversized grey crewneck sweatshirt (`w_004`)
  * Chunky white sneakers (`w_007`)
  * Black crossbody bag (`w_010`)

---

### Outfit 2: Edgy Streetwear
A classic denim-and-hoodie combination with sharp contrasts. Layering the cropped hoodie over the vintage wash gives it a cool, urban edge.

* **New Item:** Vintage Levi's 501 Jeans — Medium Wash
* **Wardrobe Pieces Used:**
  * Black cropped zip hoodie (`w_005`)
  * Black combat boots (`w_008`)
  * Brown leather belt (`w_009`)
```

**create_fit_card**

```text
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Scored these Vintage Levi's 501 Jeans in a gorgeous medium wash on depop for just $38! They give off that effortless, off-duty 90s model vibe when paired with a crisp oversized blazer and fresh white sneakers. It's the ultimate everyday look that feels both timeless and completely dialed-in.
```

**Empty search**

```text
$ python app.py ask 'rare astronaut costume under $1'
No listings matched your search. Try changing the description, removing the size filter, or increasing the maximum price.

0 model calls this session
```

**Empty wardrobe**

```text
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_empty_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_empty_wardrobe()))"
Here are two easy, versatile ways to style vintage medium-wash Levi's 501s:

**1. The Classic Casual Look**
* **Top:** A tucked-in, crisp white cotton t-shirt or a relaxed-fit grey crewneck sweatshirt.
* **Footwear:** Classic white canvas sneakers (like Converse or Vans) or retro runners.
* **Accessories:** A simple brown leather belt and a canvas tote bag.
* *Why it works:* It lets the vintage jeans take center stage with an effortless, timeless aesthetic.

**2. Elevated Denim-on-Denim**
* **Top:** A slightly darker or lighter button-down denim shirt worn open over a black baby tee, or fully buttoned and half-tucked.
* **Footwear:** Black leather loafers or ankle boots.
* **Accessories:** A structured black leather belt and minimalist silver jewelry.
* *Why it works:* Playing with different denim shades adds texture and a chic, intentionally styled edge to vintage staples.
```

**Three uncached fit cards**

```text
$ python -c "import config; config.CACHE_ENABLED = False; from tools import create_fit_card; from utils.data_loader import load_listings; cards = [create_fit_card('jeans and white sneakers', load_listings()[0]) for _ in range(3)]; [print(f'Run {i}: {card}') for i, card in enumerate(cards, 1)]; print(f'Unique outputs: {len(set(cards))}/3')"
Run 1: Scored these dreamy Vintage Levi's 501 Jeans in a classic medium wash on depop for just $38! They anchor the ultimate effortless off-duty look when paired with crisp white sneakers and an oversized vintage tee. It's giving cool, timeless everyday comfort that never goes out of style.
Run 2: Scored these Vintage Levi's 501 Jeans in a perfect medium wash on depop for just $38! They bring the ultimate effortlessly cool 90s indie-sleaze aesthetic to your everyday wardrobe. Just pair them with your favorite crisp white sneakers and an oversized vintage tee for a casual, coffee-run-ready vibe.
Run 3: Channeling total 90s off-duty model energy, these Vintage Levi's 501 Jeans—Medium Wash are an absolute must-have. Just style them with a classic baby tee and crisp white sneakers for that effortless weekend look. Snag this dreamy pair on depop right now for only $38.
Unique outputs: 3/3
```

**Local regression check (model calls mocked)**

```text
$ python test_agent.py
PASS: size and price filters, empty cases, session handoff, and early stop (mocked model).
```

---

## How I Used AI

The following two moments came from the final review with Codex.

**Moment 1 — checking the implementation**

- *What I asked for:* I asked Codex to check my completed milestones against the assignment before finishing the write-up.
- *What came back:* It found that `_size_tokens` used `p.strip().upper` instead of `p.strip().upper()`, so size filtering received method objects and could crash. It also checked the successful and empty-search branches and the session handoff.
- *What I changed:* With Codex's help, I added the missing parentheses and added `test_agent.py` to check size boundaries, price filtering, session handoff, and stopping before the model tools on an empty search. These local checks use mocked model outputs and do not claim to be the acceptance evaluation.

**Moment 2 — finishing the submission documentation**

- *What I asked for:* In the same request, I asked Codex to help finish the last milestone, the write-up and submission preparation.
- *What came back:* It identified a missing full-query transcript and abbreviated per-tool commands containing `...`. It ran the commands and also checked an empty wardrobe and three uncached captions for the same input; the three captions were different.
- *What I changed:* With Codex's help, I replaced the placeholders with runnable commands and captured text output, clarified the search rules, and recorded these actual uses of AI. My existing acceptance criteria were left unchanged.

**Moment 3: Unit 4 testing (Claude Code)**

- *What I asked for:* I asked Claude Code to work through the Unit 4 milestones with me: the MCP move, triggering the failure modes, running the evaluation, and the write-up.
- *What came back:* It registered `search_listings` in `mcp_server.py`, added the trace calls and a handler for MCP failures, and wrote `score_run.py`. That script applies my criteria, as written, to every `run_eval.py` try, including an identity check for criterion 3 that the run log alone can't show. It ran the before and after evaluations, diagnosed the criterion 4 miss as the model paraphrasing the title, and proposed a one-line prompt change.
- *What I changed / checked:* I kept the original targets in `criteria.md` unchanged, including the ones that turned out to be easy, and wrote that up as a finding instead of revising them. "Mentions the title" is scored literally, which is why the before run shows a miss.

**Repository for this unit and the next:** https://github.com/xiaogao0616/ai201-project2-fitfindr-starter-v2026

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

Produced by `python score_run.py --label before`, which runs `run_eval.py::main`
(five tries per scenario, caching off, temperature 0.9) and applies each
criterion exactly as written in `criteria.md`. Full output:
`results/run_2026-10-11_2229_before.md`; per-try PASS/FAIL reasons:
`results/scores_before.json`.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before suggest_outfit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. selected_item is the dict passed to suggest_outfit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card mentions item title and price | 4 of 5 | FAIL | PASS | FAIL | FAIL | PASS | MISSED (2/5) |
| 5. No returned listing over max_price | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Scenarios (`scenarios.py`): c1 `vintage graphic tee under $30`; c2
`designer ballgown size XXS under $5`; c3 `90s track jacket in size M`; c4
`silk slip dress in midi length under $40` (same item all five tries); c5
`vintage jacket under $25`. A sixth, diagnostic scenario (`denim jacket under $50`
with the empty wardrobe) is not one of the five.

**Real output from one try per criterion**, pasted as text. All of it was
produced by `agent.py::run_agent` (tools in `tools.py`, search via
`mcp_server.py::search_listings`), run by `run_eval.py::run_once` and scored by
`score_run.py::score`.

Criterion 1, try 1 (`tools.py::create_fit_card`):

```
- stopped early: no
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
- search_results: 10
Fit card:
Channel total early-2000s street style by pairing this cropped Y2K Baby Tee — Butterfly Print with baggy dark-wash jeans and chunky white sneakers. Grab it on depop for just $18.0 to instantly nail that effortless, everyday proportion play.
```

Criterion 2, try 1 (the branch in `agent.py::run_agent`):

```
- stopped early: yes — No listings matched your search. Try changing the description, removing the size filter, or increasing the maximum price.
- selected_item: (none)
- search_results: 0
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
[3] branch
      →    search empty, stopping before suggest_outfit
c2 try 1: PASS — suggest_outfit calls=0
```

Criterion 3, try 1 (session in `agent.py::run_agent`, checked by
`score_run.py` wrapping `agent.suggest_outfit` and comparing with `is`):

```
[3] select_item
      out: 90s Track Jacket — Navy/White Stripe ($45.0, poshmark)
      →    first (best-scoring) result
[4] suggest_outfit
      in:  new_item='90s Track Jacket — Navy/White Stripe', wardrobe=10 items
c3 try 1: PASS — same object
```

Criterion 4, try 1, a FAIL (`tools.py::create_fit_card`):

```
- selected_item: 90s Silk Slip Dress — Floral, Midi Length ($30.0, depop)
Fit card:
Channel your inner 90s icon by pairing this floral silk slip dress with a distressed denim jacket and chunky combat boots. It's the ultimate grunge-meets-feminine contrast for effortless everyday styling. Find it listed on depop for just $30.0!
c4 try 1: FAIL — title=NO, price=yes
```

Criterion 5, try 1 (`mcp_server.py::search_listings` → `tools.py::search_listings`):

```
[1] parse_query
      in:  vintage jacket under $25
      out: {'description': 'vintage jacket', 'size': None, 'max_price': 25.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage jacket', 'size': None, 'max_price': 25.0}
      out: 10 items: Y2K Baby Tee — Butterfly Print, Oversized Flannel Shirt — Plaid Red/Black, Graphic Tee — 2003 Tour Bootleg Style … +7 more
c5 try 1: PASS — 10 results, max $25.0, over ceiling: 0
```

---

## Verdicts and Diagnoses

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools | 4 of 5 | MET (5/5) | PASS = no `session["error"]` and a non-empty `fit_card`. All five tries returned a card. |
| 2 | Impossible query stops before the second tool | 5 of 5 | MET (5/5) | PASS = `error` set, `suggest_outfit` never called (counted by a wrapper, not read off the trace), and the message names what to change ("Try changing…"). |
| 3 | `selected_item` is the dict passed to `suggest_outfit` | 5 of 5 | MET (5/5) | PASS = `suggest_outfit` was called exactly once, and its `new_item` argument `is` `session["selected_item"]`: the same object, not merely one with an equal title. |
| 4 | Fit card mentions the item's title and price | 4 of 5 | MISSED (2/5) | PASS = the full listing title appears in the card (case-insensitive, dashes and commas ignored) AND the price appears as `$30` or `$30.0`. Paraphrases like "this floral silk slip dress" don't count as the title. 2 PASS is below the target of 4. |
| 5 | No returned listing over `max_price` | 5 of 5 | MET (5/5) | PASS = non-empty results and every `price <= max_price`, checked over all 10 results in the session, not just the 3 the trace shows. |

**Diagnoses**

*Criterion 4: missed, 2 of 5. Place: the model's output. Mechanism: the prompt in `tools.py::create_fit_card`.*
The price appeared in all five cards but the title in only two. In the other
three the model renamed the item: "this floral silk slip dress", "this floral
midi dress", "this floral midi slip dress". The prompt said "Mention the item
title… once" right next to "Do not write a product listing", so the model
treated the title as something to describe in its own words, not to quote.
The search, the session and the tool itself were all fine: the right item
reached the prompt every time (the criterion 3 check confirms it). The only
problem is what the prompt let the model do.

*Pattern.* It isn't specific to this item. The empty-wardrobe diagnostic runs
use a different item (`Denim Jacket — Light Wash, Cropped`), and only 2 of 5
of those cards used the exact title either ("this Light Wash Cropped Denim
Jacket", "this cropped light-wash Denim Jacket"). So it is one cause across
two items: the model paraphrases the title whenever the prompt allows it.

*On the four that were met.* Criteria 1, 2, 3 and 5 don't depend on how the
model words things. The branch, the session handoff and the price filter are
deterministic, so once they worked, 5/5 was close to guaranteed. My
criterion 1 target (4 of 5) was too low: I'd tighten it to 5 of 5 and run it
across several different queries, since the only thing that varies between
tries is the model, and the model never failed to return text. Criterion 5 is
also tested on only one query. A stronger version would check several price
ceilings, including one exactly equal to a listing's price.

*On how I read criterion 4.* "Mentions the title" could be read generously,
since "a floral slip dress" is arguably about the title. I scored the literal
reading, the listing's title text, because that is what makes the card point
to one specific listing. I didn't revise the criterion: it was measurable, and
I simply missed it.

---

## Loop Trace

Captured with `python app.py ask '...' --trace`. The search step goes through
MCP (`mcp_client.call_tool` → `mcp_server.py`) and is labelled `(via MCP)`.

**Happy path** (uncached, try 1 of the before run)

```
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
      →    first (best-scoring) result
[4] suggest_outfit
      in:  new_item='Y2K Baby Tee — Butterfly Print', wardrobe=10 items
      out: Here is a practical, Y2K-inspired outfit using the new baby tee and pieces from your wardrobe:  **Y2K Streetwe…
[5] create_fit_card
      in:  outfit=646 chars, new_item='Y2K Baby Tee — Butterfly Print'
      out: Channel total early-2000s street style by pairing this cropped Y2K Baby Tee — Butterfly Print with baggy dark-…
```

**Empty search** (stops after step 3 and never reaches the model):

```
$ python app.py ask 'designer ballgown size XXS under $5' --trace
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
[3] branch
      →    search empty, stopping before suggest_outfit

  No listings matched your search. Try changing the description, removing the size filter, or increasing the maximum price.

0 model calls this session
```

### Failure modes, triggered on purpose

**Empty search.** Handled since unit 3 (output above). The message names three things the user can change.

**Empty wardrobe.** `suggest_outfit` already had a prompt for an empty wardrobe. There was no crash and no empty string:

```
$ python app.py ask 'denim jacket under $50' --empty-wardrobe --trace
(running with an empty wardrobe)
...
[4] suggest_outfit
      in:  new_item='Denim Jacket — Light Wash, Cropped', wardrobe=0 items
      out: Here are two practical, everyday outfit ideas for this light-wash cropped denim jacket:  **1. The Off-Duty Cas…
[5] create_fit_card
      in:  outfit=992 chars, new_item='Denim Jacket — Light Wash, Cropped'
      out: Score this effortless Denim Jacket — Light Wash, Cropped for just $42 on Poshmark! It's the ultimate piece for…
```

**Model unavailable.** I ran it with one character of the key changed. The
bad key was set as an environment variable for that one command, so `.env` was
never edited, and the query wasn't in the cache:

```
$ python app.py ask 'black combat boots for winter'
...
[3] select_item
      out: Oversized Flannel Shirt — Plaid Red/Black ($22.0, thredUp)
[4] error
      →    ModelUnavailable: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.

  The search worked, but the outfit model couldn't be reached, so no outfit or fit card was made. The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. Best match meanwhile: Oversized Flannel Shirt — Plaid Red/Black ($22.0, thredUp).
```

Before this unit the handler existed, but it said only "The model is
unavailable: …". I changed it to say what still worked and to show the best
match, so the user still gets the listing when the model is down.

**Extra: the MCP server won't start.** I forced this by renaming
`mcp_server.py` for one run. Before, it would have ended in an uncaught
`MCPError` stack trace. Now `run_agent` catches it:

```
  The listing search service (MCP server) couldn't be reached, so nothing was searched. Run `python mcp_server.py` on its own to see why it won't start, then try again.
```

**On the MCP move:** `search_listings` is registered in `mcp_server.py` with
typed inputs (`description: str`, `size: str | None`, `max_price: float | None`,
matching the Tool Inventory). Its description is written for an outside agent:
it states the units, the size-matching rule, the fields each result has, and
that it returns `[]` when nothing matches. In `agent.py::run_agent` the direct
call became `call_tool("search_listings", session["parsed"])`. Nothing behaved
differently: direct and MCP results were identical (`==`) on three queries,
including one that matched nothing, and `test_agent.py` still passes. Two things
did change. Each search now starts a server process, which is a little slower,
and there is a new way for the agent to fail (the server not starting), which
now has its own handler.

---

## The Improvement

**What I changed:** one line of the prompt in `tools.py::create_fit_card`.

```diff
-Mention the item title, its price, and its platform once each. Describe the
+Use the ITEM TITLE below word for word, exactly as written, once; do not
+paraphrase or shorten it. Mention its price and platform once each. Describe the
 outfit vibe specifically. Do not write a product listing or use bullet points.
```

**Which failure it was meant to fix:** criterion 4, where the model paraphrased
the title instead of using it (3 of the 5 tries failed before). Nothing else
changed: same scenarios, same temperature, same model, caching off.

### Run Log — After

`python score_run.py --label after` → `results/run_2026-10-11_2232_after.md`,
`results/scores_after.json`.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before suggest_outfit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. selected_item is the dict passed to suggest_outfit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card mentions item title and price | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. No returned listing over max_price | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Criterion 4, try 2 after the change:

```
Channel your inner 90s grunge-chic aesthetic by layering this floral midi slip dress under a vintage black denim jacket and pairing it with combat boots. It's an effortlessly cool, sweet-meets-edgy look that is totally practical for everyday wear. Snag this 90s Silk Slip Dress — Floral, Midi Length for just $30.0 over on depop before it's gone!
```

**Did it help, and how do I know:** Yes. Criterion 4 went from 2/5 to 5/5, and
no other criterion changed. The empty-wardrobe diagnostic uses a different item
that the prompt wasn't tuned on, and its exact-title count also went from 2/5 to
5/5, so the result isn't a fluke of one listing. The caveat is sample size: ten
cards across two items is evidence, not proof.

---

## What's Still Broken

No criterion is missed after the fix, but that says as much about my targets as
about the agent:

- **Criterion 1's target was too easy.** It asked for 4 of 5 on a step that
  never failed. I'd tighten it to 5 of 5 across several different queries. I
  didn't change it now, because changing a target after seeing the result is
  exactly what this unit warns against. It belongs in the next set of criteria.
- **Prices read like Python floats.** Cards say "$30.0" and "$18.0" because the
  prompt passes `price` straight from the data. My criterion 4 rule accepts
  `$30.0`, so it isn't a miss, but it doesn't read like a real post. The fix is
  to format the price before it goes into the prompt. I didn't make it because
  the unit allows one improvement, and a second change would have muddied the
  before/after comparison.
- **The query parser only knows letter sizes.** `size 8` (shoes) and `W27`
  (denim) aren't extracted. So "platform sneakers size 8" searches with no size
  filter, and the 8 stays in the description. I'd add numeric and waist patterns
  to the regex in `agent.py::run_agent`. That's outside this unit's one change.
- **Each criterion is tested on only one query.** Criteria 3 and 5 especially
  would be stronger across several queries and price ceilings, including a
  price exactly at the ceiling.


<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
