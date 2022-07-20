import json

import pandas as pd

from nmd_index import ApproxWordList5
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
    lookup_table = ApproxWordList5((2, 3, 4,))
    for b in behaviors:
        lookup_table.add_word(b)

    # find all duplicates within a fraction of each other
    min_similarity = 0.75
    dupes = set()
    for i, b in enumerate(behaviors):
        found = [f[0] for f in lookup_table.lookup(b, 20) if f[-1] >= min_similarity]
        found = tuple(sorted(original for casefolded in found for original in casefold_dedupe[casefolded]))
        if len(found) > 1:
            print(found)
            dupes.add(found)

    # save the data
    with open('dupes.json', 'w', encoding='utf8') as f:
        json.dump(sorted(dupes), f, indent=4, ensure_ascii=False)
