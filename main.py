import json
from pathlib import Path

import bs4

OUTPUT_DIR = Path('out')
DOCS_DIR = Path('./dbx-career-framework/docs')


def clean_text(text):
    return text.replace('\xA0', ' ').strip()


def parse_html(html):
    # parse doc-content element
    soup = bs4.BeautifulSoup(html, features="lxml")
    doc_content = soup.find(id='doc-content')

    out = dict()

    # the first header is implicitly 'description'
    section_header = 'description'

    # get title and description
    out['title'] = doc_content.find(id='doc-title').text
    out[section_header] = [clean_text(doc_content.find('section', recursive=False).text)]

    # remaining page sections
    page_sections = doc_content.find_all('div',
                                         recursive=False,
                                         attrs={
                                             'class': 'ace-line',
                                             'id':    lambda x: x != 'doc-title',
                                         })

    # each section contains either a h2, bold line, table, or plain text
    for section in page_sections:

        # section header
        header_tag = section.find('h2')
        if header_tag is not None:
            section_header = header_tag.text
            continue

        # table
        table_tag = section.find('table')
        if table_tag is not None:
            t = []
            for row in table_tag.find_all(['th', 'tr']):
                r = []
                for cell in row.find_all('td'):
                    c = []
                    for ace_line in cell.find_all('div', {'class': 'ace-line'}):
                        c.append(clean_text(ace_line.text))
                    r.append('\n'.join(c))
                t.append(r)
            out.setdefault(section_header, []).append(t)
            continue

        # bold line or plain text
        out.setdefault(section_header, []).append(clean_text(section.text))

    return out


if __name__ == '__main__':

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # get all role files
    # sort by "ic"/"m", then role type, then level
    # don't worry about the sorting logic, which is greatly oversimplified but works (for now)
    paths = sorted(DOCS_DIR.glob('*[0-9]*.html'), key=lambda p: [p.name[0], p.name[::-1]])

    for path in paths:
        print(path.name)
        parsed_data = parse_html(path.read_text(encoding='utf8'))

        # output here
        with (OUTPUT_DIR / f'{path.stem}.json').open('w', encoding='utf8') as f:
            json.dump(parsed_data, f, indent=4, ensure_ascii=False)
