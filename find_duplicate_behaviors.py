import json

import pandas as pd

from find_replace_trie import Trie
from parse_json_to_csv import OUTPUT_PATH as CSV_PATH

if __name__ == '__main__':

    df = pd.read_csv(CSV_PATH, encoding='utf8')

    behaviors = sorted(df['Behavior'].unique())

    # casefold the text
    casefold_dedupe = dict()
    for b in behaviors:
        casefold_dedupe.setdefault(b.casefold(), []).append(b)

    # note: zero matches for this
    for b_list in casefold_dedupe.values():
        if len(b_list) > 1:
            print(b_list)

    # build a lookup data structure
    behaviors = sorted(casefold_dedupe.keys())
    t = Trie.fromkeys(behaviors, case_sensitive=False)

    # find all duplicates within a fraction of each other
    dupes = set()
    for i, b in enumerate(behaviors):
        found = list(t.levenshtein_lookup(b, max(4, len(b) // 8)))
        if len(found) > 1:
            print(found)
            dupes.add(tuple(sorted(original for casefolded in found for original in casefold_dedupe[casefolded])))

    # save the data
    with open('dupes.json', 'w') as f:
        json.dump(sorted(dupes), f, indent=4, ensure_ascii=False)
