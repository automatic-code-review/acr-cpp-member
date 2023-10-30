import hashlib
import json
import os
import subprocess


def review(config):
    rules = config['rules']
    path_source = config['path_source']

    comments = []

    for root, dirs, files in os.walk(path_source):
        for file in files:
            if not file.endswith(".h"):
                continue

            path = os.path.join(root, file)
            comments.extend(__review_by_path(path, path_source, rules))

    return comments


def __review_by_path(path, path_source, rules):
    data = subprocess.run(
        'ctags --output-format=json --languages=c++ --fields=+an ' + path,
        shell=True,
        capture_output=True,
        text=True,
    ).stdout

    comments = []
    comments_by_type = {
        "MEMBER_NOT_INITIALIZED_IN_HEADER": [],
        "MEMBER_PRIVATE_HAS_PREFIX_UNDERLINE": [],
    }
    path_internal = path.replace(path_source, "")[1:]

    for data_obj in data.split('\n'):
        if data_obj == '':
            continue

        data_obj = json.loads(data_obj)

        if data_obj['kind'] != 'member':
            continue

        if 'constexpr' in data_obj['pattern']:
            continue

        atr_name = data_obj['name']
        atr_line = data_obj['line']

        if 'MEMBER_PRIVATE_HAS_PREFIX_UNDERLINE' in rules and data_obj['access'] == 'private' and \
                not atr_name.startswith("_"):
            member_private_has_prefix_underline = comments_by_type['MEMBER_PRIVATE_HAS_PREFIX_UNDERLINE']
            member_private_has_prefix_underline.append(f'{atr_name} (Line {atr_line})')
            comments_by_type['MEMBER_PRIVATE_HAS_PREFIX_UNDERLINE'] = member_private_has_prefix_underline

        if 'MEMBER_NOT_INITIALIZED_IN_HEADER' in rules and '=' in data_obj['pattern']:
            member_not_initialized_in_header = comments_by_type['MEMBER_NOT_INITIALIZED_IN_HEADER']
            member_not_initialized_in_header.append(f'{atr_name} (Line {atr_line})')
            comments_by_type['MEMBER_NOT_INITIALIZED_IN_HEADER'] = member_not_initialized_in_header

    member_private_has_prefix_underline = comments_by_type['MEMBER_PRIVATE_HAS_PREFIX_UNDERLINE']
    if len(member_private_has_prefix_underline) > 0:
        attrs_append = ', '.join(member_private_has_prefix_underline)
        comment = f"""Atributos private devem possuir o prefixo `_`<br>
Atributos: {attrs_append}<br>
Arquivo: {path_internal}"""

        comments.append(
            __create_comment(
                comment_id=__generate_md5(comment),
                comment=comment,
                start_line=1,
                end_line=1,
                path=path_internal,
            )
        )

    member_not_initialized_in_header = comments_by_type['MEMBER_NOT_INITIALIZED_IN_HEADER']
    if len(member_not_initialized_in_header) > 0:
        attrs_append = ', '.join(member_not_initialized_in_header)
        comment = f"""Atributos nao devem ser inicializado no header, e sim no constructor<br>
Atributos: {attrs_append}<br>
Arquivo: {path_internal}"""

        comments.append(
            __create_comment(
                comment_id=__generate_md5(comment),
                comment=comment,
                start_line=1,
                end_line=1,
                path=path_internal,
            )
        )

    return comments


def __create_comment(comment_id, comment, path, start_line, end_line):
    return {
        "id": comment_id,
        "comment": comment,
        "position": {
            "language": 'c++',
            "path": path,
            "startInLine": start_line,
            "endInLine": end_line,
            "snipset": False
        }
    }


def __generate_md5(string):
    md5_hash = hashlib.md5()
    md5_hash.update(string.encode('utf-8'))
    return md5_hash.hexdigest()
