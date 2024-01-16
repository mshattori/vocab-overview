import os
import sys
import re
import argparse
from glob import glob

INDEX_TEMPLATE_FILEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index_template.html')
PAGE_TEMPLATE_FILEPATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'page_template.html')
DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'www')


def split_by_parens(text):
    split_text = re.split(r'(\([^()]*(?:\([^()]+\)[^()]*)*\))', text)
    result = [s.strip() for s in split_text if s.strip()]
    return result

def split_by_brackets(text):
    split_text = re.split(r'(\[[^\[\]]*(?:\[[^\[\]]+\][^\[\]]*)*\])', text)
    result = [s.strip() for s in split_text if s.strip()]
    return result

def split_by_brackets_and_parens(text):
    result = []
    split_text = split_by_brackets(text)
    for s in split_text:
        result.extend(split_by_parens(s))
    return result

WORD_CLASS_PATTERN = r'\((vi|vt|adj|adv|n)\.?\)'

def split_text_equals_annotations(text):
    texts = []
    equals = []
    annotations = []

    split_text = split_by_brackets_and_parens(text)
    for s in split_text:
        if re.fullmatch(WORD_CLASS_PATTERN, s):
            texts.append(s)
        elif re.fullmatch('\[.*\]|\(.*\)', s):
            s = s[1:-1]
            if s.startswith('='):
                equals.append(s[1:])
            else:
                annotations.append(s)
        else:
            texts.append(s)

    return texts, equals, annotations

class QAItem:
    def __init__(self, q_text, a_text):
        self._q_text = q_text
        self._a_text = a_text
        # Split q_text by space, slash and punctuation marks (period, comma, etc.)
        id_components = re.split(r'[\s/.,;:!?]+', q_text)
        # Remove characters that cannot be used for the id of HTML elements.
        id_components = [re.sub(r'[^\w-]', '', c) for c in id_components]
        self._item_id = '-'.join(id_components)

    @property
    def item_id(self):
        return self._item_id

    @property
    def q_text(self):
        return self._q_text

    @property
    def a_text(self):
        return self._a_text

    @staticmethod
    def parse_line(line):
        m = re.search(':=', line)
        if not m:
            raise ValueError(f'Unexpected line: {line}')
        q_text = line[0:m.span()[0]].strip()
        a_text = line[m.span()[1]:].strip()

        q_texts, q_equals, q_annotations = split_text_equals_annotations(q_text)
        a_texts, a_equals, a_annotations = split_text_equals_annotations(a_text)
        equals = q_equals + a_equals
        annotations = q_annotations + a_annotations

        def remove_commas_around_word_class(text):
            # Remove commas before/after word class signes.
            pattern = f'(, )?{WORD_CLASS_PATTERN}(, )?'
            # Preserve the space at left, but remove the right one
            replace = lambda m: m.group().lstrip(',').rstrip(' ,')
            return re.sub(pattern, replace, text)

        q_text = remove_commas_around_word_class(', '.join(q_texts))
        a_text = remove_commas_around_word_class(', '.join(a_texts))
        equals = ', '.join(equals)
        annotations = '; '.join(annotations)

        components = []
        components.append(QAItem(q_text, a_text))
        if len(equals) > 0:
            components.append(QAAnnotation('=' + equals))
        if len(annotations) > 0:
            components.append(QAAnnotation(annotations))

        return components

class QAComment:
    def __init__(self, text):
        self._text = text

    def __str__(self):
        return self._text

    @staticmethod
    def parse_line(line):
        if not line.startswith('#'):
            raise ValueError(f'Unexpected line: {line}')
        m = re.fullmatch('#\s*(.*)', line)
        if not m:
            raise ValueError(f'Unexpected line: {line}')
        text = m.group(1)
        return [QAComment(text)]

class QAAnnotation:
    def __init__(self, text):
        self._text = text

    def __str__(self):
        return self._text

def _parse_QA_line(line):
    line = line.strip()
    if line.startswith('#'):
        return QAComment.parse_line(line)
    else:
        return QAItem.parse_line(line)

def _parse_QA_file(filename):
    components = []
    with open(filename) as f:
        for line in f.readlines():
            line = line.rstrip('\n')
            parsed_components = _parse_QA_line(line)
            components.extend(parsed_components)
    return components

def construct_content(components):
    content = ''
    # content += '<thead>'
    # content += '<tr><th>English Phrase</th><th>Japanese Description</th></tr>'
    # content += '</thead>'
    content += '<tbody>\n'
    for component in components:
        if isinstance(component, QAComment):
            content += '<tr class="comment"><td colspan="3">' + str(component) + '</td></tr>\n'
        elif isinstance(component, QAItem):
            content += '<tr>\n'
            content += f'<td><input class="uk-checkbox" type="checkbox" id="{component.item_id}"/></td>\n'
            content += f'<td>{component.q_text}</td>\n'
            content += f'<td class="answer-text">{component.a_text}</td>\n'
            content += '</tr>\n'
        elif isinstance(component, QAAnnotation):
            content += '<tr class="note"><td colspan="3" class="answer-text">' + str(component) + '</td></tr>\n'
    content += '</tbody>'
    return content

def main(args):
    stem_name = os.path.splitext(os.path.basename(args.input_file))[0]
    components = _parse_QA_file(args.input_file)
    page_content = construct_content(components)
    with open(PAGE_TEMPLATE_FILEPATH) as f:
        html = f.read()

    html = html.replace('%TITLE%', stem_name.replace('-', ' ').title())
    html = html.replace('%CONTENT%', page_content)

    output_filename = stem_name.lower() + '.html'
    output_filepath = os.path.join(args.output_dir, output_filename)

    with open(output_filepath, 'w') as f:
        f.write(html)
    print(f'Created {output_filepath}')

    make_index_page(args.output_dir)

def make_index_page(output_dir):
    sub_pages_list = []
    for html_file in glob(os.path.join(output_dir, '*.html')):
        html_file = os.path.basename(html_file)
        if html_file == 'index.html':
            continue
        title = os.path.splitext(html_file)[0].replace('-', ' ').title()
        sub_pages_list.append((title, html_file))

    content = ''
    content += '<thead>'
    content += '<tr><th>Pages</th></tr>'
    content += '</thead>'
    content += '<tbody class="uk-table-striped">'
    for title, html_file in sorted(sub_pages_list):
        content += f'<tr><td><a href="{html_file}">{title}</a></td></tr>'
    content += '</body>'
    with open(INDEX_TEMPLATE_FILEPATH) as f:
        html = f.read()
    html = html.replace('%TITLE%', 'Vocablary overview')
    html = html.replace('%CONTENT%', content)

    index_filename = os.path.join(output_dir, 'index.html')
    with open(index_filename, 'w') as f:
        f.write(html)

    print(f'Created {index_filename}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_dir', '-d', help='Output directory', required=False, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument('input_file', help='Input file')
    args = parser.parse_args()

    main(args)