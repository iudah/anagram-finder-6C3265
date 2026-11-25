#!/usr/bin/env python3
"""Anagram Finder - command-line driver (front end) using anagram.py as backend.

Keeps the front-end menu, state dict and UX, but delegates all letter logic,
indexing, scoring and statistics to anagram.py:

    clean_input / analyse_anagram        -> word comparison
    load_file / sort_dict                -> word-file loading + index
    make_anagram_lookup                  -> anagram lookups
    analyse_anagram_file                 -> word-list statistics
"""

import itertools
import os
import time
from collections import Counter

import anagram as lib


HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WORD_FILE = os.path.join(HERE, "3of6all.txt")
REPORT_FILE = os.path.join(HERE, "word_report.txt")

# Standard Scrabble letter values (front-end concern, not in backend).
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
# Thin wrapper over anagram.clean_input (no letter logic duplicated)
# --------------------------------------------------------------------------
def key_of(text):
    """Backend's sorted-letter key as a string (what index lookups expect)."""
    return "".join(lib.clean_input(text)[1])


# --------------------------------------------------------------------------
# Input helpers
# --------------------------------------------------------------------------
def ask_text(prompt):
    while True:
        value = input(prompt).strip()
        if lib.clean_input(value)[0]:
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
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()
        if not raw:
            return default
        if raw.isdigit() and low <= int(raw) <= high:
            return int(raw)
        print(f"  Enter a whole number between {low} and {high}.")


# --------------------------------------------------------------------------
# Levels 1-2: checking two words (uses anagram.analyse_anagram)
# --------------------------------------------------------------------------
def format_counts(counter):
    """Counter -> 'a x2, b, c x3' (front-end formatting only)."""
    parts = []
    for letter in sorted(counter):
        n = counter[letter]
        parts.append(letter if n == 1 else f"{letter} x{n}")
    return ", ".join(parts)


def check_pair(first, second):
    is_anagram, sort, s1missing, s2missing = lib.analyse_anagram(first, second)
    clean_a, sorted_a = lib.clean_input(first)
    clean_b, sorted_b = lib.clean_input(second)

    if clean_a == clean_b:
        print(f'\n"{first}" and "{second}" are the same word, so they are '
              "NOT anagrams (an anagram needs a different order).")
        return
    if is_anagram:
        print(f'\n"{first}" and "{second}" are anagrams.')
        print(f"Sorted letters: {sort}")
        return

    print(f'\n"{first}" and "{second}" are NOT anagrams.')
    print(f"Sorted letters of first:  {''.join(sorted_a)}")
    print(f"Sorted letters of second: {''.join(sorted_b)}")
    extra = Counter(s2missing or {})
    missing = Counter(s1missing or {})
    if extra:
        print(f"Extra in first (not in second): {format_counts(extra)}")
    if missing:
        print(f"Missing from first (needed to match second): "
              f"{format_counts(missing)}")


def check_two_words(state=None):
    while True:
        first = ask_text("First word or phrase: ")
        second = ask_text("Second word or phrase: ")
        check_pair(first, second)
        print()
        if not ask_yes_no("Check another pair?"):
            break


# --------------------------------------------------------------------------
# Level 3: word list / families / searching (uses anagram.load_file/sort_dict)
# --------------------------------------------------------------------------
def words_from_index(index):
    return [w for fam in index.values() for w in fam]


def load_words(path):
    """Load a word file via anagram.load_file + anagram.sort_dict.

    Returns (words, index, error_message).
    """
    if not os.path.exists(path):
        return [], {}, f"Word file not found: {path}"
    index = lib.load_file(path, lib.sort_dict)
    if not index:
        return [], {}, f"Word file is empty or unreadable: {path}"
    words = sorted(words_from_index(index))
    return words, index, None


def largest_family(index):
    key = max(index, key=lambda k: len(index[k]))
    return key, index[key]


def find_anagrams(word, index):
    target = lib.clean_input(word)[0]
    return sorted(index.get(key_of(word), set()) - {target})


def can_build(word, available):
    return all(available[ch] >= n for ch, n in Counter(word).items())


def build_from_letters(letters, words):
    available = Counter(lib.clean_input(letters)[0])
    found = [w for w in words if len(w) >= 2 and can_build(w, available)]
    return sorted(found, key=lambda w: (-len(w), w))


# --------------------------------------------------------------------------
# Level 4: scoring, two-word anagrams, timing, statistics, adding words
# --------------------------------------------------------------------------
def score_word(word):
    return sum(LETTER_VALUES.get(ch, 0) for ch in word)


def best_scoring_words(letters, words, limit=10):
    candidates = build_from_letters(letters, words)
    candidates.sort(key=lambda w: (-score_word(w), -len(w), w))
    return candidates[:limit]


def two_word_anagrams(phrase, words, index, limit=20):
    target = Counter(lib.clean_input(phrase)[0])
    total = sum(target.values())
    results, seen = [], set()
    for word in words:
        if len(word) >= total or not can_build(word, target):
            continue
        remainder = target - Counter(word)
        remainder_key = "".join(sorted(remainder.elements()))
        for other in index.get(remainder_key, ()):
            if other == word:
                continue
            pair = tuple(sorted((word, other)))
            if pair in seen:
                continue
            seen.add(pair)
            results.append(pair)
            if len(results) >= limit:
                return results, True
    return results, False


def anagrams_by_permutation(word, word_set):
    found = set()
    for perm in itertools.permutations(word):
        candidate = "".join(perm)
        if candidate != word and candidate in word_set:
            found.add(candidate)
    return found


def timing_comparison(words, index):
    word_set = set(words)
    print("\nLetters | Word        | Found | Permutations | Dictionary")
    print("--------+-------------+-------+--------------+-----------")
    for length in range(5, 10):
        same_length = [w for w in words if len(w) == length]
        if not same_length:
            print(f"{length:>7} | (no words of this length in the list)")
            continue
        word = max(same_length,
                   key=lambda w: len(index.get(key_of(w), ())))
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


def statistics_report(path):
    """Build statistics using anagram.analyse_anagram_file.

    anagram.analyse_anagram_file returns
        (index, largest_family, longest_word, num_families, Counter)
    """
    index, big_family, longest, num_families, letter_counter = \
        lib.analyse_anagram_file(path)
    if index is None:
        return None, f"Could not read a usable word list from {path!r}."

    words = words_from_index(index)
    num_words = len(words)
    num_families_2plus = sum(1 for fam in index.values() if len(fam) > 1)
    top_letters = ", ".join(
        f"{ch} ({n})" for ch, n in letter_counter.most_common(5)
    )

    lines = [
        "WORD LIST STATISTICS",
        "====================",
        f"Word file:              {path}",
        f"Number of words:        {num_words}",
        f"Longest word:           {longest} ({len(longest)} letters)",
        f"Anagram families (2+):  {num_families_2plus}",
        f"Anagram families (all): {num_families}",
        f"Largest family:         {len(big_family)} words "
        f"({', '.join(sorted(big_family))})",
        f"Most common letters:    {top_letters}",
    ]
    return lines, None


def save_report(lines, path=REPORT_FILE):
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
        return None
    except OSError as error:
        return str(error)


def add_word_to_file(raw, state, path):
    """Validate and append a new word, then refresh backend lookups."""
    word = raw.strip().lower()
    if not word:
        return False, "Nothing entered."
    if not (word.isascii() and word.isalpha()):
        return False, "Words may only contain the letters a-z (no spaces, digits or symbols)."
    if len(word) < 2:
        return False, "A word needs at least 2 letters."
    if word in set(state["words"]):
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

    state["words"].append(word)
    state["index"].setdefault(key_of(word), set()).add(word)
    # Keep anagram.py's shared lookup closure in sync with the new file.
    try:
        lib.anagram_from_default_file = lib.make_anagram_lookup(path)
    except RuntimeError:
        pass
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
    if state["words"]:
        return True
    print(f"\nThis option needs the word file. {state['error']}")
    print("Create a word file (one word per line) or use option 10 to add words.")
    return False


def menu_builtin_anagrams(state):
    word = ask_text("Word to find anagrams of: ")
    target = lib.clean_input(word)[0]
    found = (lib.anagram_from_list(word) or set()) - {target}
    show_anagram_list(target, sorted(found), "the built-in list")


def menu_file_anagrams(state):
    if not need_words(state):
        return
    word = ask_text("Word to find anagrams of: ")
    target = lib.clean_input(word)[0]
    found = (lib.anagram_from_default_file(word) or set()) - {target}
    show_anagram_list(target, sorted(found), "the word list")


def menu_largest_family(state):
    if not need_words(state):
        return
    key, family = largest_family(state["index"])
    print(f"\nLargest anagram family ({len(family)} words, letters '{key}'):")
    print("  " + ", ".join(sorted(family)))


def menu_build_words(state):
    if not need_words(state):
        return
    letters = ask_text("Letters to use: ")
    found = build_from_letters(letters, state["words"])
    if not found:
        print("\nNo words in the list can be made from those letters.")
        return
    cleaned = lib.clean_input(letters)[0]
    print(f"\n{len(found)} word(s) can be built from '{cleaned}':")
    print("  " + ", ".join(found))


def menu_scrabble(state):
    if not need_words(state):
        return
    while True:
        letters = lib.clean_input(ask_text("Enter 7 letters: "))[0]
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
    cleaned = lib.clean_input(phrase)[0]
    print(f"\nTwo-word anagrams of '{cleaned}':")
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
    lines, error = statistics_report(state["path"])
    if error:
        print(f"\n{error}")
        return
    print()
    print("\n".join(lines))
    write_error = save_report(lines)
    if write_error:
        print(f"\nCould not save the report: {write_error}")
    else:
        print(f"\nReport saved to {REPORT_FILE}")


def menu_add_word(state):
    raw = input("New word to add: ")
    ok, message = add_word_to_file(raw, state, state["path"])
    print(("\n" if ok else "\nNot added: ") + message)
    if ok:
        state["error"] = None


def menu_change_file(state):
    """Switch the active word-list file."""
    print(f"\nCurrent word file: {state['path']}")
    print("  1) keep current")
    print(f"  2) use default ({os.path.basename(DEFAULT_WORD_FILE)})")
    print("  3) enter a new path")
    choice = input("Choose [1/2/3]: ").strip()

    if choice == "1":
        return
    if choice == "2":
        new_path = DEFAULT_WORD_FILE
    elif choice == "3":
        new_path = input("Path to word list: ").strip()
    else:
        print("  Please choose 1, 2, or 3.")
        return

    if not os.path.isfile(new_path):
        print(f'  Not a regular file: {new_path}')
        return

    words, index, error = load_words(new_path)
    if error:
        print(f"  {error}")
        return

    state.update({
        "path": new_path,
        "words": words,
        "index": index,
        "error": None,
    })
    try:
        lib.anagram_from_default_file = lib.make_anagram_lookup(new_path)
    except RuntimeError as exc:
        print(f"  Note: could not rebuild backend lookup ({exc}); "
              "menu actions that reload will still work.")
    print(f"  Loaded {len(words)} words from {new_path}.")


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
    ("Change the active word-list file", menu_change_file),
]


def main():
    initial_path = DEFAULT_WORD_FILE
    words, index, error = load_words(initial_path)
    state = {
        "path": initial_path,
        "words": words,
        "index": index,
        "error": error,
    }

    print("=== Anagram Finder ===")
    if error:
        print(f"Note: {error}")
        print("Options 1 and 2 still work; the rest need the word file.")
        print("Use option 11 to choose a different word file.")
    else:
        print(f"Loaded {len(words)} words from {os.path.basename(initial_path)}.")

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
