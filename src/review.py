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
        path_internal = path.replace(path_source, "")[1:]

        if 'MEMBER_PRIVATE_HAS_PREFIX_UNDERLINE' in rules and data_obj['access'] == 'private' and \
                not atr_name.startswith("_"):
            comment = f"""O atributo `{atr_name}` deve possuir o prefixo `_`, por se tratar de uma variavel private<br>
Arquivo: {path_internal}<br>
Linha: {atr_line}"""
            comments.append(
                __create_comment(
                    comment_id=__generate_md5(comment),
                    comment=comment,
                    start_line=atr_line,
                    end_line=atr_line,
                    path=path_internal,
                )
            )

        if 'MEMBER_NOT_INITIALIZED_IN_HEADER' in rules and '=' in data_obj['pattern']:
            comment = f"""O atributo `{atr_name}` nao deve ser inicializado no header, e sim no constructor<br>
Arquivo: {path_internal}<br>
Linha: {atr_line}"""

            comments.append(
                __create_comment(
                    comment_id=__generate_md5(comment),
                    comment=comment,
                    start_line=atr_line,
                    end_line=atr_line,
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
            "endInLine": end_line
        }
    }


def __generate_md5(string):
    md5_hash = hashlib.md5()
    md5_hash.update(string.encode('utf-8'))
    return md5_hash.hexdigest()
