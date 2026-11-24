#!/usr/bin/env python3
"""Anagram Finder - a command-line word toolkit (standard library only).

Level 1: check whether two words are anagrams
Level 2: phrases, validation, extra/missing letters, menu, built-in list
Level 3: word file, anagram families, find anagrams, build words from letters
Level 4: Scrabble scoring, two-word anagrams, timing, statistics, add words

Shared data structure (agree on this first when working in a group):
    index: dict mapping sorted-letters string -> list of words
           e.g. {"eilnst": ["enlist", "listen", "silent", "tinsel"]}
"""

import itertools
import os
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
WORD_FILE = os.path.join(HERE, "words.txt")
REPORT_FILE = os.path.join(HERE, "word_report.txt")

# Small built-in list used by the Level 2 "find anagrams" option.
BUILTIN_WORDS = [
    "listen", "silent", "enlist", "tinsel", "inlets",
    "stone", "notes", "onset", "tones", "steno",
    "angel", "angle", "glean", "evil", "vile", "live", "veil",
    "race", "care", "acre", "heart", "earth", "hater",
    "below", "elbow", "bowel", "study", "dusty",
    "spare", "pears", "parse", "reaps", "spear",
]

# Standard Scrabble letter values.
LETTER_VALUES = {
    **dict.fromkeys("aeioulnstr", 1),
    **dict.fromkeys("dg", 2),
    **dict.fromkeys("bcmp", 3),
    **dict.fromkeys("fhvwy", 4),
    "k": 5,
    **dict.fromkeys("jx", 8),
    **dict.fromkeys("qz", 10),
}


# --------------------------------------------------------------------------
# Core letter helpers (Levels 1-2)
# --------------------------------------------------------------------------

def clean(text):
    """Lower-case the text and keep only the letters a-z."""
    return "".join(ch for ch in text.lower() if ch.isascii() and ch.isalpha())


def sorted_letters(text):
    """Return the cleaned letters of the text in sorted order."""
    return "".join(sorted(clean(text)))


def format_counts(counter):
    """Turn a Counter into text like 'a x2, b, c x3'."""
    parts = []
    for letter in sorted(counter):
        n = counter[letter]
        parts.append(letter if n == 1 else f"{letter} x{n}")
    return ", ".join(parts)


def letter_difference(first, second):
    """Return (extra, missing) letter counts of first compared with second.

    extra   = letters first has more of than second
    missing = letters first would need to match second
    """
    count_a = Counter(clean(first))
    count_b = Counter(clean(second))
    return count_a - count_b, count_b - count_a


# --------------------------------------------------------------------------
# Input helpers
# --------------------------------------------------------------------------

def ask_text(prompt):
    """Ask for a word or phrase containing at least one letter."""
    while True:
        value = input(prompt).strip()
        if clean(value):
            return value
        print("  Please enter at least one letter.")


def ask_yes_no(prompt):
    while True:
        answer = input(prompt + " (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  Please answer y or n.")


def ask_number(prompt, default, low=1, high=1000):
    """Ask for a whole number, falling back to a default on empty input."""
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()
        if not raw:
            return default
        if raw.isdigit() and low <= int(raw) <= high:
            return int(raw)
        print(f"  Enter a whole number between {low} and {high}.")


# --------------------------------------------------------------------------
# Levels 1-2: checking two words
# --------------------------------------------------------------------------

def check_pair(first, second):
    """Print whether two words/phrases are anagrams and why."""
    key_a, key_b = sorted_letters(first), sorted_letters(second)

    if clean(first) == clean(second):
        print(f'\n"{first}" and "{second}" are the same word, so they are '
              "NOT anagrams (an anagram needs a different order).")
        return

    if key_a == key_b:
        print(f'\n"{first}" and "{second}" are anagrams.')
        print(f"Sorted letters: {key_a}")
        return

    print(f'\n"{first}" and "{second}" are NOT anagrams.')
    print(f"Sorted letters of first:  {key_a}")
    print(f"Sorted letters of second: {key_b}")
    extra, missing = letter_difference(first, second)
    if extra:
        print(f"Extra in first (not in second): {format_counts(extra)}")
    if missing:
        print(f"Missing from first (needed to match second): "
              f"{format_counts(missing)}")


def check_two_words(state=None):
    """Level 1/2 option: compare pairs until the user stops."""
    while True:
        first = ask_text("First word or phrase: ")
        second = ask_text("Second word or phrase: ")
        check_pair(first, second)
        print()
        if not ask_yes_no("Check another pair?"):
            break


# --------------------------------------------------------------------------
# Level 3: word list, families, searching
# --------------------------------------------------------------------------

def load_words(path):
    """Load a one-word-per-line file. Returns (words, error_message)."""
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except FileNotFoundError:
        return [], f"Word file not found: {path}"
    except (OSError, UnicodeDecodeError) as error:
        return [], f"Could not read word file ({error})"

    words, seen = [], set()
    for line in lines:
        word = line.strip().lower()
        if word and word.isascii() and word.isalpha() and word not in seen:
            seen.add(word)
            words.append(word)

    if not words:
        return [], f"Word file is empty (no valid words found): {path}"
    return words, None


def build_index(words):
    """Group words into anagram families keyed by their sorted letters."""
    index = {}
    for word in words:
        index.setdefault("".join(sorted(word)), []).append(word)
    return index


def largest_family(index):
    """Return (key, words) for the biggest anagram family."""
    key = max(sorted(index), key=lambda k: len(index[k]))
    return key, index[key]


def find_anagrams(word, index):
    """Every word in the index that is an anagram of the given word."""
    target = clean(word)
    key = "".join(sorted(target))
    return [w for w in index.get(key, []) if w != target]


def can_build(word, available):
    """True if word fits inside the available Counter of letters."""
    return all(available[ch] >= n for ch, n in Counter(word).items())


def build_from_letters(letters, words):
    """Words that can be made using each letter at most as often as given."""
    available = Counter(clean(letters))
    found = [w for w in words if len(w) >= 2 and can_build(w, available)]
    return sorted(found, key=lambda w: (-len(w), w))


# --------------------------------------------------------------------------
# Level 4: scoring, two-word anagrams, timing, statistics, adding words
# --------------------------------------------------------------------------

def score_word(word):
    return sum(LETTER_VALUES.get(ch, 0) for ch in word)


def best_scoring_words(letters, words, limit=10):
    """Highest-scoring words buildable from the letters."""
    candidates = build_from_letters(letters, words)
    candidates.sort(key=lambda w: (-score_word(w), -len(w), w))
    return candidates[:limit]


def two_word_anagrams(phrase, words, index, limit=20):
    """Pairs of list words whose letters together equal the phrase's letters.

    For each word that fits inside the phrase, the leftover letters are
    looked up in the index, so no pair is ever tried blindly.
    """
    target = Counter(clean(phrase))
    total = sum(target.values())
    results, seen = [], set()

    for word in words:
        if len(word) >= total or not can_build(word, target):
            continue
        remainder = target - Counter(word)
        remainder_key = "".join(sorted(remainder.elements()))
        for other in index.get(remainder_key, []):
            pair = tuple(sorted((word, other)))
            if pair in seen:
                continue
            seen.add(pair)
            results.append(pair)
            if len(results) >= limit:
                return results, True
    return results, False


def anagrams_by_permutation(word, word_set):
    """Slow approach: try every ordering of the letters."""
    found = set()
    for perm in itertools.permutations(word):
        candidate = "".join(perm)
        if candidate != word and candidate in word_set:
            found.add(candidate)
    return found


def timing_comparison(words, index):
    """Time permutations vs. the sorted-letters dictionary (5-9 letters)."""
    word_set = set(words)
    print("\nLetters | Word        | Found | Permutations | Dictionary")
    print("--------+-------------+-------+--------------+-----------")
    for length in range(5, 10):
        same_length = [w for w in words if len(w) == length]
        if not same_length:
            print(f"{length:>7} | (no words of this length in the list)")
            continue
        word = max(same_length, key=lambda w: len(index["".join(sorted(w))]))

        start = time.perf_counter()
        slow = anagrams_by_permutation(word, word_set)
        slow_time = time.perf_counter() - start

        start = time.perf_counter()
        fast = set(find_anagrams(word, index))
        fast_time = time.perf_counter() - start

        match = "" if slow == fast else " (MISMATCH!)"
        print(f"{length:>7} | {word:<11} | {len(fast):>5} | "
              f"{slow_time:>10.6f}s | {fast_time:>8.6f}s{match}")
    print("\nThe dictionary approach does one lookup; permutations try up to "
          "n! orderings.")


def statistics_report(words, index):
    """Build the word-list statistics as a list of text lines."""
    families = {k: v for k, v in index.items() if len(v) > 1}
    longest = max(words, key=len)
    letter_totals = Counter("".join(words))
    top_letters = ", ".join(f"{ch} ({n})" for ch, n in letter_totals.most_common(5))
    big_key, big_family = largest_family(index)

    return [
        "WORD LIST STATISTICS",
        "====================",
        f"Number of words:        {len(words)}",
        f"Longest word:           {longest} ({len(longest)} letters)",
        f"Anagram families (2+):  {len(families)}",
        f"Largest family:         {len(big_family)} words "
        f"({', '.join(big_family)})",
        f"Most common letters:    {top_letters}",
    ]


def save_report(lines, path=REPORT_FILE):
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
        return None
    except OSError as error:
        return str(error)


def add_word_to_file(raw, words, index, path=WORD_FILE):
    """Validate and append a new word. Returns (ok, message)."""
    word = raw.strip().lower()
    if not word:
        return False, "Nothing entered."
    if not (word.isascii() and word.isalpha()):
        return False, "Words may only contain the letters a-z (no spaces, digits or symbols)."
    if len(word) < 2:
        return False, "A word needs at least 2 letters."
    if word in set(words):
        return False, f'"{word}" is already in the word list.'

    try:
        needs_newline = False
        if os.path.exists(path) and os.path.getsize(path) > 0:
            with open(path, "rb") as handle:
                handle.seek(-1, os.SEEK_END)
                needs_newline = handle.read(1) != b"\n"
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(("\n" if needs_newline else "") + word + "\n")
    except OSError as error:
        return False, f"Could not write to the word file ({error})."

    words.append(word)
    index.setdefault("".join(sorted(word)), []).append(word)
    return True, f'Added "{word}" to the word list.'


# --------------------------------------------------------------------------
# Menu actions
# --------------------------------------------------------------------------

def show_anagram_list(word, found, source):
    if found:
        print(f'\nFound {len(found)} anagram(s) of "{word}" in {source}:')
        print("  " + ", ".join(sorted(found)))
    else:
        print(f'\nNo anagrams of "{word}" found in {source}.')


def need_words(state):
    """Return True if a word list is loaded; otherwise explain why not."""
    if state["words"]:
        return True
    print(f"\nThis option needs the word file. {state['error']}")
    print("Create a words.txt file (one word per line) next to this program, "
          "or use option 9 to add words.")
    return False


def menu_builtin_anagrams(state):
    word = ask_text("Word to find anagrams of: ")
    index = build_index(BUILTIN_WORDS)
    show_anagram_list(clean(word), find_anagrams(word, index), "the built-in list")


def menu_file_anagrams(state):
    if not need_words(state):
        return
    word = ask_text("Word to find anagrams of: ")
    show_anagram_list(clean(word), find_anagrams(word, state["index"]),
                      "the word list")


def menu_largest_family(state):
    if not need_words(state):
        return
    key, family = largest_family(state["index"])
    print(f"\nLargest anagram family ({len(family)} words, letters '{key}'):")
    print("  " + ", ".join(family))


def menu_build_words(state):
    if not need_words(state):
        return
    letters = ask_text("Letters to use: ")
    found = build_from_letters(letters, state["words"])
    if not found:
        print("\nNo words in the list can be made from those letters.")
        return
    print(f"\n{len(found)} word(s) can be built from '{clean(letters)}':")
    print("  " + ", ".join(found))


def menu_scrabble(state):
    if not need_words(state):
        return
    while True:
        letters = clean(ask_text("Enter 7 letters: "))
        if len(letters) == 7:
            break
        print(f"  You entered {len(letters)} letter(s); please enter exactly 7.")
    top = best_scoring_words(letters, state["words"], limit=10)
    if not top:
        print("\nNo words in the list can be made from those letters.")
        return
    print(f"\nBest-scoring words from '{letters}':")
    for rank, word in enumerate(top, start=1):
        print(f"  {rank:>2}. {word:<10} {score_word(word)} points")


def menu_two_word(state):
    if not need_words(state):
        return
    phrase = ask_text("Phrase to rearrange: ")
    limit = ask_number("Maximum results to show", default=20)
    pairs, truncated = two_word_anagrams(phrase, state["words"],
                                         state["index"], limit)
    if not pairs:
        print("\nNo two-word anagrams found in the word list.")
        return
    print(f"\nTwo-word anagrams of '{clean(phrase)}':")
    for first, second in pairs:
        print(f"  {first} {second}")
    if truncated:
        print(f"(stopped at the limit of {limit} results)")


def menu_timing(state):
    if need_words(state):
        timing_comparison(state["words"], state["index"])


def menu_statistics(state):
    if not need_words(state):
        return
    lines = statistics_report(state["words"], state["index"])
    print()
    print("\n".join(lines))
    error = save_report(lines)
    if error:
        print(f"\nCould not save the report: {error}")
    else:
        print(f"\nReport saved to {REPORT_FILE}")


def menu_add_word(state):
    raw = input("New word to add: ")
    ok, message = add_word_to_file(raw, state["words"], state["index"])
    print(("\n" if ok else "\nNot added: ") + message)
    if ok:
        state["error"] = None


# --------------------------------------------------------------------------
# Main program
# --------------------------------------------------------------------------

MENU = [
    ("Check two words or phrases", check_two_words),
    ("Find anagrams of a word (small built-in list)", menu_builtin_anagrams),
    ("Find anagrams of a word (word file)", menu_file_anagrams),
    ("Show the largest anagram family", menu_largest_family),
    ("Build words from a set of letters", menu_build_words),
    ("Best Scrabble words from 7 letters", menu_scrabble),
    ("Find two-word anagrams of a phrase", menu_two_word),
    ("Timing: permutations vs dictionary", menu_timing),
    ("Word-list statistics (saves a report)", menu_statistics),
    ("Add a word to the word file", menu_add_word),
]


def main():
    words, error = load_words(WORD_FILE)
    state = {"words": words, "index": build_index(words), "error": error}

    print("=== Anagram Finder ===")
    if error:
        print(f"Note: {error}")
        print("Options 1 and 2 still work; the rest need the word file.")
    else:
        print(f"Loaded {len(words)} words from {os.path.basename(WORD_FILE)}.")

    while True:
        print("\nMenu")
        for number, (label, _) in enumerate(MENU, start=1):
            print(f"  {number:>2}. {label}")
        print("   0. Quit")

        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye!")
            return
        if choice.isdigit() and 1 <= int(choice) <= len(MENU):
            MENU[int(choice) - 1][1](state)
        else:
            print("Please choose a number from the menu.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")