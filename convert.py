import os
import sys
import re
import argparse

DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'www')


def split_by_parens(text):
    split_text = re.split(r'(\([^()]+(?:\([^()]+\)[^()]*)*\))', text)
    result = [s for s in split_text if s.strip()]
    return result

def split_by_brackets(text):
    split_text = re.split(r'(\[[^\[\]]+(?:\[[^\[\]]+\][^\[\]]*)*\])', text)
    result = [s for s in split_text if s.strip()]
    return result

def split_by_brackets_and_parens(text):
    result = []
    split_text = split_by_brackets(text)
    for s in split_text:
        if s.strip():
            result.extend(split_by_parens(s))
    return result

def split_text_equals_annotations(text):
    texts = []
    equals = []
    annotations = []
    split_text = split_by_brackets_and_parens(text)
    for s in split_text:
        if re.fullmatch('\[.*\]|\(.*\)', s):
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

        q_text = ', '.join(q_texts)
        a_text = ', '.join(a_texts)
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
    content += '<table>'
    content += '<tr><th>English Phrase</th><th>Japanese Description</th></tr>'
    for component in components:
        if isinstance(component, QAComment):
            content += '<tr class="comment"><td colspan="2">' + str(component) + '</td></tr>'
        elif isinstance(component, QAItem):
            content += '<tr><td>' + component.q_text + '</td><td>' + component.a_text + '</td></tr>'
        elif isinstance(component, QAAnnotation):
            content += '<tr class="note"><td colspan="2">' + str(component) + '</td></tr>'
    content += '</table>'
    return content

def main(args):
    components = _parse_QA_file(args.input_file)
    page_content = construct_content(components)
    with open('template.html') as f:
        html = f.read()

    html = html.replace('%CONTENT%', page_content)

    output_filename = os.path.splitext(os.path.basename(args.input_file).lower())[0] + '.html'
    output_filepath = os.path.join(args.output_dir, output_filename)

    with open(output_filepath, 'w') as f:
        f.write(html)
    print(f'Created {output_filepath}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_dir', '-d', help='Output directory', required=False, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument('input_file', help='Input file')
    args = parser.parse_args()

    main(args)