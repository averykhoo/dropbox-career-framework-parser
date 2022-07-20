import json

import pandas as pd

from nmd_index import ApproxWordList5
from parse_json_to_csv import OUTPUT_PATH as CSV_PATH


class DisjointSet:
    def __init__(self):
        self.parents = dict()

    def find(self, item):
        parent = self.parents[item]
        if parent is item:
            return item
        return self.find(parent)

    def union(self, *items):
        # add new items
        for item in items:
            if item not in self.parents:
                self.parents[item] = item
        # union
        roots = [self.find(item) for item in items]
        for root in roots[1:]:
            self.parents[root] = roots[0]

    def disjoint_sets(self):
        known_roots = dict()
        current = set()
        unknown = set(self.parents.keys())
        if not unknown:
            return []

        item = unknown.pop()
        while True:
            current.add(item)
            parent = self.parents[item]
            if parent == item:
                for _item in current:
                    known_roots[_item] = item
                current.clear()
                if not unknown:
                    break
                item = unknown.pop()
            elif parent in known_roots:
                for _item in current:
                    known_roots[_item] = known_roots[parent]
                current.clear()
                if not unknown:
                    break
                item = unknown.pop()

            else:
                item = parent
                unknown.remove(item)

        tmp = dict()
        for k, v in known_roots.items():
            tmp.setdefault(v, set()).add(k)
        return list(tmp.values())


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
    dupes = DisjointSet()
    for i, b in enumerate(behaviors):
        found = [f[0] for f in lookup_table.lookup(b, 20) if f[-1] >= min_similarity]
        found = tuple(sorted(original for casefolded in found for original in casefold_dedupe[casefolded]))
        if len(found) > 1:
            print(found)
            dupes.union(*found)

    merged_dupes = [sorted(dupe_set) for dupe_set in dupes.disjoint_sets()]
    print(f'found {len(merged_dupes)} sets of duplicates')

    # save the data
    with open('dupes.json', 'w', encoding='utf8') as f:
        json.dump(sorted(merged_dupes), f, indent=4, ensure_ascii=False)
