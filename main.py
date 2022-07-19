import json
from pathlib import Path

import bs4

OUTPUT_DIR = Path('output_json')
DOCS_DIR = Path('./dbx-career-framework/docs')

SUFFIX_FOLDERS = {
    'software_engineer':          'Software Engineer (SWE)',
    'quality_assurance_engineer': 'Quality Assurance Engineer (QAE)',
    'reliability_engineer':       'Reliability Engineer (SRE)',
    'machine_learning_engineer':  'Machine Learning Engineer (MLE)',
    'security_engineer':          'Security Engineer (SE)',
    'technical_program_manager':  'Technical Program Manager (TPM)',
    'engineering_manager':        'Engineering Manager (EM)',
    'engineering_director':       'Engineering Manager (EM)',
}


def get_text(tag):
    # convert emoji images to text
    for emoji_tag in tag.find_all('img', attrs={'data-emoji-ch': lambda x: x and len(x) == 1}):
        emoji_tag.replace_with(emoji_tag['data-emoji-ch'])

    # get text
    text = tag.text

    # clean text
    text = text.replace('\xA0', ' ')
    text = text.strip()

    return text


def parse_html(html):
    # parse doc-content element
    soup = bs4.BeautifulSoup(html, features="lxml")
    doc_content = soup.find(id='doc-content')

    out = dict()

    # the first header is implicitly 'description'
    section_header = 'description'

    # get title and description
    out['title'] = [doc_content.find(id='doc-title').text]
    out[section_header] = [get_text(doc_content.find('section', recursive=False))]

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
            section_header = get_text(header_tag)
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
                        c.append(get_text(ace_line))
                    r.append('\n'.join(c))
                t.append(r)
            out.setdefault(section_header, []).append(t)
            continue

        # bold line or plain text
        out.setdefault(section_header, []).append(get_text(section))

    # transpose the description table and add headers for consistency
    out['description'][1] = [['{...} of Responsibility', 'Key Behaviors']] + \
                            [list(row) for row in zip(*out['description'][1])]

    return out


if __name__ == '__main__':

    # get all role files
    # sort by "ic"/"m", then role type, then level
    # don't worry about the sorting logic, which is greatly oversimplified but works (for now)
    paths = sorted(DOCS_DIR.glob('*[0-9]*.html'), key=lambda p: [p.name[0], p.name[::-1]])

    for path in paths:
        print(path.name)
        parsed_data = parse_html(path.read_text(encoding='utf8'))

        # get folder name
        for suffix, folder_name in SUFFIX_FOLDERS.items():
            if path.stem.endswith(suffix):
                break
        else:
            raise IndexError(path.name)

        # make folder
        (OUTPUT_DIR / folder_name).mkdir(parents=True, exist_ok=True)

        # output here
        with (OUTPUT_DIR / folder_name / f'{path.stem}.json').open('w', encoding='utf8') as f:
            json.dump(parsed_data, f, indent=4, ensure_ascii=False)
