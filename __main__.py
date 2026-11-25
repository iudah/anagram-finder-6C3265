# main.py
"""Command-line driver for the Anagram Finder.

Menu options cover Levels 1-4 of the project spec:
  * two-word anagram check (with explanation)
  * exact anagram lookup (built-in list, current file, or arbitrary file)
  * build words from a multiset of letters
  * largest anagram family
  * Scrabble-scored highest-value 7-letter words
  * two-word anagram search for a phrase
  * benchmark: brute-force permutations vs sorted-letters index
  * word-list statistics via anagram.analyse_anagram_file, saved to a report
  * choose / change the active word-list file
  * append new words to the active word file

The active word list is controlled by ``CURRENT_WORD_FILE`` and can be changed
from the menu (option 8).  Switching reloads the shared lookup closures so
subsequent menu actions see the new list.
"""

import itertools
import os
import time
from collections import Counter

import anagram as lib


DEFAULT_WORD_FILE = "3of6all.txt"
REPORT_FILE = "anagram_report.txt"
CURRENT_WORD_FILE = DEFAULT_WORD_FILE

SCRABBLE = {**dict.fromkeys("aeioulnrst", 1),
            **dict.fromkeys("dg", 2),
            **dict.fromkeys("bcmp", 3),
            **dict.fromkeys("fhvwy", 4),
            **dict.fromkeys("k", 5),
            **dict.fromkeys("jx", 8),
            **dict.fromkeys("qz", 10)}


# ---------------------------------------------------------------- helpers
def prompt(msg):
    """input() that never raises on EOF / Ctrl-C in a menu."""
    try:
        return input(msg).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return ""


def ask_nonempty(prompt_text, label):
    """Loop until the user enters something with at least one letter."""
    while True:
        raw = prompt(prompt_text)
        cleaned, _ = lib.clean_input(raw)
        if cleaned:
            return raw
        print(f"  ! {label} must contain at least one letter. Try again.")


def scrabble_score(word):
    return sum(SCRABBLE.get(ch, 0) for ch in word.lower())


def can_build(word, letters_counter):
    return all(word.count(c) <= letters_counter[c] for c in set(word))


def get_index(path=None):
    """Load a word list and return the sorted-letters index, or None."""
    path = path or CURRENT_WORD_FILE
    index = lib.load_file(path, lib.sort_dict)
    if not index:
        print(f"  ! Could not read a usable word list from {path!r}.")
        return None
    return index


def get_words(index):
    """All words in the index, flattened."""
    return [w for fam in index.values() for w in fam]


def refresh_lookup():
    """Rebuild the shared lookup closures after the word file changes.

    ``lib.make_anagram_lookup`` raises on a bad file, so we guard it: the
    program stays alive and the user can pick another file.
    """
    try:
        lib.anagram_from_default_file = lib.make_anagram_lookup(CURRENT_WORD_FILE)
    except RuntimeError as exc:
        print(f"  ! Could not rebuild lookup for {CURRENT_WORD_FILE!r}: {exc}")
        # Leave the previous closure in place; menu actions that reload the
        # file themselves (build_words, stats, etc.) still work.
    return None


# ---------------------------------------------------------------- menu items
def menu_check_two():
    print("\n-- Check two words --")
    a = ask_nonempty("First word/phrase: ", "First entry")
    b = ask_nonempty("Second word/phrase: ", "Second entry")

    is_anagram, sort, s1missing, s2missing = lib.analyse_anagram(a, b)
    clean1, sorted1 = lib.clean_input(a)
    clean2, sorted2 = lib.clean_input(b)

    print(f'\n  "{a}" vs "{b}"')
    print(f"  Sorted letters (1): {''.join(sorted1)}")
    print(f"  Sorted letters (2): {''.join(sorted2)}")

    if clean1 == clean2:
        print("  -> They are the SAME word. Not anagrams: "
              "an anagram must reorder different letters.")
    elif is_anagram:
        print("  -> They ARE anagrams.")
    else:
        print("  -> They are NOT anagrams.")
        if s2missing:
            extras = ", ".join(f"{c}x{n}" for c, n in sorted(s2missing.items()))
            print(f"     Extra in first : {extras}")
        if s1missing:
            extras = ", ".join(f"{c}x{n}" for c, n in sorted(s1missing.items()))
            print(f"     Extra in second: {extras}")


def menu_find_anagrams():
    print("\n-- Find anagrams of a word --")
    while True:
        word = ask_nonempty("Word: ", "Word")

        print("  Source:")
        print("   1) built-in list")
        print(f"   2) current file: {CURRENT_WORD_FILE}")
        print("   3) choose a new file")
        choice = prompt("   Choose [1/2/3]: ")

        if choice == "1":
            fam = lib.anagram_from_list(word)
            label = "built-in list"
        elif choice == "2":
            fam = lib.anagram_from_default_file(word)
            label = CURRENT_WORD_FILE
        elif choice == "3":
            path = ask_nonempty("Path to word list: ", "Path")
            index = get_index(path)
            if index is None:
                continue
            fam = index.get("".join(lib.clean_input(word)[1]))
            label = path
        else:
            print("  ! Enter 1, 2, or 3.")
            continue

        fam = (fam or set()) - {word.lower()}
        if fam:
            print(f"  Found {len(fam)} anagram(s) of {word!r} in {label}:")
            for w in sorted(fam):
                print(f"    - {w}")
        else:
            print(f"  No anagrams of {word!r} in {label}.")

        if prompt("  Another? [y/N]: ").lower() != "y":
            return


def menu_build_words():
    print("\n-- Build words from letters --")
    raw = ask_nonempty("Letters: ", "Letter set")
    letters = lib.clean_input(raw)[0]
    counter = Counter(letters)

    index = get_index()
    if index is None:
        return

    hits = sorted({w for w in get_words(index) if len(w) > 1 and can_build(w, counter)},
                  key=lambda w: (-len(w), w))

    if not hits:
        print(f"  No words can be built from {letters!r}.")
        return
    print(f"  {len(hits)} word(s) can be built from {letters!r} "
          f"(longest first, showing up to 40):")
    for w in hits[:40]:
        print(f"    - {w}")

    print("\n  Top by Scrabble score:")
    for w in sorted(hits, key=lambda w: (-scrabble_score(w), w))[:10]:
        print(f"    - {w:20s} {scrabble_score(w):3d}")


def menu_largest_family():
    print("\n-- Largest anagram family --")
    index = get_index()
    if index is None:
        return
    family = max(index.values(), key=len)
    sample = next(iter(family))
    key = "".join(lib.clean_input(sample)[1])
    print(f"  {len(family)} words share sorted key {key!r}:")
    for w in sorted(family):
        print(f"    - {w}")


def menu_best_7():
    print("\n-- Highest-scoring 7-letter words from your letters --")
    raw = ask_nonempty("7 letters (letters only): ", "Letters")
    letters = lib.clean_input(raw)[0]
    if len(letters) != 7:
        print(f"  ! You entered {len(letters)} letters; want exactly 7.")
        return
    counter = Counter(letters)

    index = get_index()
    if index is None:
        return

    hits = sorted({w for w in get_words(index) if can_build(w, counter)},
                  key=lambda w: (-scrabble_score(w), w))
    if not hits:
        print("  No words can be built from those letters.")
        return
    print(f"  Top {min(10, len(hits))} by score:")
    for w in hits[:10]:
        print(f"    - {w:20s} {scrabble_score(w):3d}")


def menu_two_word_anagrams():
    print("\n-- Two-word anagrams of a phrase --")
    phrase = ask_nonempty("Phrase: ", "Phrase")
    target = "".join(lib.clean_input(phrase)[1])
    target_counter = Counter(target)

    index = get_index()
    if index is None:
        return

    words = sorted({w for w in get_words(index) if len(w) > 1})
    results = set()
    for w1 in words:
        c1 = Counter(w1)
        if not all(c1[c] <= target_counter[c] for c in c1):
            continue
        remaining = target_counter - c1
        rem_key = "".join(sorted(remaining.elements()))
        second_fam = index.get(rem_key)
        if not second_fam:
            continue
        for w2 in second_fam:
            if w2 == w1:
                continue
            results.add(tuple(sorted((w1, w2))))
        if len(results) >= 25:
            break

    if results:
        print(f"  {len(results)} pair(s) (showing up to 25):")
        for a, b in sorted(results)[:25]:
            print(f"    - {a} + {b}")
    else:
        print("  No two-word anagrams found.")


def menu_benchmark():
    print("\n-- Benchmark: permutations vs sorted-letters index --")
    index = get_index()
    if index is None:
        return

    # Pick one sample word per length; do NOT iterate characters of a string.
    by_len = {}
    for w in get_words(index):
        if 5 <= len(w) <= 9 and len(w) not in by_len:
            by_len[len(w)] = w

    if not by_len:
        print("  ! No words of length 5-9 in the current word list.")
        return

    print(f"  {'len':>3} {'perm (s)':>12} {'index (s)':>12} {'speedup':>10}")
    for n in sorted(by_len):
        word = by_len[n]
        key = "".join(sorted(word))

        t0 = time.perf_counter()
        _ = [p for p in itertools.permutations(word) if "".join(p) in index]
        t_perm = time.perf_counter() - t0

        runs = 1000
        t0 = time.perf_counter()
        for _ in range(runs):
            _ = index.get(key)
        t_index = (time.perf_counter() - t0) / runs

        speedup = t_perm / t_index if t_index else float("inf")
        print(f"  {n:>3} {t_perm:>12.6f} {t_index:>12.8f} {speedup:>9.0f}x")


def menu_stats():
    """Word-list statistics via anagram.analyse_anagram_file."""
    print("\n-- Word-list statistics --")
    stats = lib.analyse_anagram_file(CURRENT_WORD_FILE)
    index, num_words, largest_family, longest, num_families, letter_counter = stats

    if index is None:
        print(f"  ! Could not read a usable word list from {CURRENT_WORD_FILE!r}.")
        return

    words = get_words(index)            # driver recomputes word count

    print(f"  File              : {CURRENT_WORD_FILE}")
    print(f"  Words             : {num_words}")
    print(f"  Anagram families  : {num_families}")
    print(f"  Largest family    : {len(largest_family)} words "
          f"(e.g. {sorted(largest_family)[:5]})")
    print(f"  Longest word      : {longest!r} ({len(longest)} letters)")
    print("  Most common letters (top 5):")
    for ch, n in letter_counter.most_common(5):
        print(f"    {ch!r}: {n}")

    if prompt("  Save report to file? [y/N]: ").lower() == "y":
        try:
            with open(REPORT_FILE, "w", encoding="utf-8") as fh:
                fh.write(f"Anagram report for {CURRENT_WORD_FILE}\n")
                fh.write("=" * 40 + "\n")
                fh.write(f"Words: {num_words}\n")
                fh.write(f"Anagram families: {num_families}\n")
                fh.write(f"Largest family: {sorted(largest_family)}\n")
                fh.write(f"Longest word: {longest} ({len(longest)})\n")
                fh.write("Letter frequency:\n")
                for ch, n in letter_counter.most_common():
                    fh.write(f"  {ch}: {n}\n")
            print(f"  Report written to {REPORT_FILE}.")
        except OSError as exc:
            print(f"  ! Could not write report: {exc}")


def menu_change_file():
    """Switch the active word-list file.  Adds the 'new file' option."""
    global CURRENT_WORD_FILE
    print("\n-- Choose the word-list file --")
    print(f"  Current: {CURRENT_WORD_FILE}")
    print(f"   1) keep current")
    print(f"   2) use default ({DEFAULT_WORD_FILE})")
    print(f"   3) enter a new path")
    choice = prompt("   Choose [1/2/3]: ")

    if choice == "1":
        return
    if choice == "2":
        new_path = DEFAULT_WORD_FILE
    elif choice == "3":
        new_path = ask_nonempty("Path to word list: ", "Path")
    else:
        print("  ! Enter 1, 2, or 3.")
        return

    if not os.path.exists(new_path):
        print(f"  ! {new_path!r} does not exist.")
        return
    if not os.path.isfile(new_path):
        print(f"  ! {new_path!r} is not a regular file.")
        return

    probe = lib.load_file(new_path, lib.sort_dict)
    if not probe:
        print(f"  ! {new_path!r} is empty or unreadable; keeping {CURRENT_WORD_FILE!r}.")
        return

    CURRENT_WORD_FILE = new_path
    refresh_lookup()
    print(f"  Active word list is now {CURRENT_WORD_FILE!r} "
          f"({sum(len(f) for f in probe.values())} words, "
          f"{len(probe)} families).")


def menu_add_word():
    print(f"\n-- Add a word to {CURRENT_WORD_FILE} --")
    if not os.path.exists(CURRENT_WORD_FILE):
        print(f"  ! {CURRENT_WORD_FILE} does not exist; choose another file first.")
        return

    raw = ask_nonempty("New word: ", "Word").lower()
    cleaned, _ = lib.clean_input(raw)
    if not cleaned:
        print("  ! Word has no letters after cleaning.")
        return
    if cleaned != raw:
        print(f"  ! Only letters are allowed (got {raw!r}, would store {cleaned!r}).")
        return

    existing = set()
    with open(CURRENT_WORD_FILE, encoding="utf-8") as fh:
        existing = {line.strip().lower() for line in fh if line.strip()}

    if cleaned in existing:
        print(f"  ! {cleaned!r} is already in the list.")
        return

    with open(CURRENT_WORD_FILE, "a", encoding="utf-8") as fh:
        fh.write(cleaned + "\n")
    print(f"  Added {cleaned!r} to {CURRENT_WORD_FILE}.")

    refresh_lookup()


# ---------------------------------------------------------------- driver
def build_menu():
    """Menu is rebuilt each loop so labels reflect CURRENT_WORD_FILE."""
    return {
        "1": ("Check two words", menu_check_two),
        "2": ("Find anagrams of a word", menu_find_anagrams),
        "3": ("Build words from letters", menu_build_words),
        "4": ("Largest anagram family", menu_largest_family),
        "5": ("Highest-scoring 7-letter Scrabble words", menu_best_7),
        "6": ("Two-word anagrams of a phrase", menu_two_word_anagrams),
        "7": ("Benchmark: permutations vs index", menu_benchmark),
        "8": (f"Word-list statistics and report", menu_stats),
        "9": (f"Change word-list file (current: {CURRENT_WORD_FILE})", menu_change_file),
        "10": (f"Add a word to {CURRENT_WORD_FILE}", menu_add_word),
        "0": ("Quit", None),
    }


def main():
    while True:
        menu = build_menu()
        print("\n===== ANAGRAM FINDER =====")
        for key, (label, _) in menu.items():
            print(f"  {key:>2}) {label}")
        choice = prompt("Choose an option: ")
        if choice == "0":
            print("Bye.")
            return
        entry = menu.get(choice)
        if entry is None:
            print("  ! Unknown option.")
            continue
        _, func = entry
        try:
            func()
        except Exception as exc:
            print(f"  ! Error: {exc}")


if __name__ == "__main__":
    main()
