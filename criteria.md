# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
The search uses keyword matching, so some reasonable phrasings may not match the
listing data. Once a listing is found, the remaining tool calls should normally
complete successfully.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
The empty-search branch is deterministic and does not depend on model-generated
text. Every empty result should therefore stop the loop reliably.

---

## 3. Something about state

In 5 of 5 successful runs, `session["selected_item"]` is the same listing
dictionary that was passed as `new_item` to `suggest_outfit`.

**Why this target:**
The selected listing is the main state passed between tools. A 5 of 5 target is
reasonable because the agent should always pass the item stored in the session,
not a newly recreated or different item.

---

## 4. Something about the fit card

In at least 4 of 5 successful runs, the fit card is a non-empty string that
mentions the selected item's title and price.

**Why this target:**
The model may phrase the card differently each time, but it should still include
the two concrete facts needed to identify and describe the item. Four of five
allows for occasional model variation while requiring consistent useful output.

---

## 5. Your choice

For 5 of 5 searches with a `max_price` value, every returned listing has a
price less than or equal to that maximum price.

**Why this target:**
The maximum-price filter is implemented locally and should be deterministic.
Unlike model-generated outfit text, it should never vary between runs.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
