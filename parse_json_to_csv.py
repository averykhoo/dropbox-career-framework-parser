import csv
import json

import pandas as pd

from parse_html_to_json import OUTPUT_DIR as JSON_DIR

OUTPUT_PATH = JSON_DIR.parent / 'output_csv' / 'collated.csv'
OUTPUT_XLSX = OUTPUT_PATH.parent / f'{OUTPUT_PATH.stem}.xlsx'
HEADERS = [
    'Track',
    'Level',
    'Title',
    'Area',
    'Competency',
    'Definition',
    'Behavior',
]


def convert_json_to_rows(json_path):
    with json_path.open(encoding='utf8') as f:
        json_obj = json.load(f)

    track = json_path.parent.name
    level = json_obj['Level']
    title = json_obj['Title']

    for key, value in json_obj.items():
        # we want the competencies, so skip level and title
        if not isinstance(value, list):
            continue

        # no competencies, skip
        if not any(isinstance(elem, list) for elem in value):
            continue

        # strip the emoji from the "sub-functional area" of the competency
        if key[1] == ' ':
            area = key[2:]
        else:
            area = key

        # parse competency table (skip headers)
        table = [elem for elem in value if isinstance(elem, list)][0]
        for row in table[1:]:
            competency, behaviors = row

            # get definition (available for core competencies only)
            # for the rest, have to parse *-_appendix.html
            if '\n' in competency:
                competency, definition = competency.split('\n', 1)
            else:
                definition = ''

            # behaviors = '\n'.join(f'{i + 1}) {x}' for i, x in enumerate(behaviors.split('\n')))
            for behavior in behaviors.split('\n'):
                behavior = behavior.strip()
                if behavior:
                    yield [
                        track,
                        level,
                        title,
                        area,
                        competency,
                        definition,
                        behavior,
                    ]


if __name__ == '__main__':

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open('w', encoding='utf8', newline='') as f_out:
        c = csv.writer(f_out)
        c.writerow(HEADERS)

        for path in JSON_DIR.glob('**/*.json'):
            c.writerows(convert_json_to_rows(path))

    df = pd.read_csv(OUTPUT_PATH, encoding='utf8')
    df.to_excel(OUTPUT_XLSX, index=False)
