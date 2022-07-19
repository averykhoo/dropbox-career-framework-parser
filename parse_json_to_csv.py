import csv
import json

from parse_html_to_json import OUTPUT_DIR as JSON_DIR

OUTPUT_PATH = JSON_DIR.parent / 'output_csv' / 'collated.csv'
HEADERS = [
    'Track',
    'Level',
    'Title',
    'Area',
    'Competency',
    'Definition',
    'Behaviors',
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

            yield [
                track,
                level,
                title,
                area,
                competency,
                definition,
                behaviors,
            ]


if __name__ == '__main__':

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open('w', encoding='utf8', newline='') as f_out:
        c = csv.writer(f_out)
        c.writerow(HEADERS)

        for path in JSON_DIR.glob('**/*.json'):
            c.writerows(convert_json_to_rows(path))
