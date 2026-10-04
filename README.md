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
> The first five sections document the Unit 3 submission; Unit 4 sections
> remain below for the next unit.

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

**Repository for this unit and the next:** https://github.com/xiaogao0616/ai201-project2-fitfindr-starter-v2026

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



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
