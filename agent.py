"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""
import re
import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    session = new_session(query, wardrobe)

    # TODO: delete these two lines and build the loop.
    # Parse optional size, for example: "size M"
    size_match = re.search(
        r"\b(?:size\s*)?(XXS|XS|S|M|L|XL|XXL)\b",
        query,
        re.IGNORECASE,
    )

    # Parse optional maximum price, for example: "under $30"
    price_match = re.search(
        r"\b(?:under|below|max(?:imum)?(?:\s+price)?)\s*\$?\s*(\d+(?:\.\d+)?)",
        query,
        re.IGNORECASE,
    )

    size = size_match.group(1).upper() if size_match else None
    max_price = float(price_match.group(1)) if price_match else None

    description = query

    if size_match:
        description = description.replace(size_match.group(0), "")
    if price_match:
        description = description.replace(price_match.group(0), "")

    description = re.sub(r"\s+", " ", description).strip(" ,")

    session["parsed"] = {
        "description": description,
        "size": size,
        "max_price": max_price,
    }

    try:
        session["search_results"] = search_listings(
            session["parsed"]["description"],
            session["parsed"]["size"],
            session["parsed"]["max_price"],
        )

        # The branch: stop immediately when no listing was found.
        if not session["search_results"]:
            session["error"] = (
                "No listings matched your search. Try changing the description, "
                "removing the size filter, or increasing the maximum price."
            )
            return session

        session["selected_item"] = session["search_results"][0]

        session["outfit_suggestion"] = suggest_outfit(
            session["selected_item"],
            session["wardrobe"],
        )

        session["fit_card"] = create_fit_card(
            session["outfit_suggestion"],
            session["selected_item"],
        )

    except ModelUnavailable as exc:
        session["error"] = f"The model is unavailable: {exc}"

    return session





# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    print("Search results:", len(session["search_results"]))
    print("Selected item:", session["selected_item"])
    print("Outfit suggestion:", session["outfit_suggestion"])
    print("Fit card:", session["fit_card"])
    print("Error:", session["error"])


if __name__ == "__main__":
    wardrobe = {
        "items": [
            "white sneakers",
            "straight-leg jeans",
            "black crossbody bag",
        ]
    }

    print("HAPPY PATH")
    _show(run_agent("vintage graphic tee under $30", wardrobe))

    print("\nEMPTY PATH")
    _show(run_agent("rare astronaut costume under $1", wardrobe))