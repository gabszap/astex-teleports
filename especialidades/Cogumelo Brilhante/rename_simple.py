#!/usr/bin/env python3
"""Script simples: renomeia arquivos em uma pasta com números sequenciais.

Uso: py scripts/rename_simple.py [PASTA] PREFIX [EXT]

Exemplo: py scripts/rename_simple.py . Hydroculos .png
O script perguntará o número inicial e pedirá confirmação antes de aplicar.
"""

from pathlib import Path
import re
import sys


def list_files(folder, ext=None):
    p = Path(folder).expanduser().resolve()
    if not p.exists() or not p.is_dir():
        print(f'Pasta inválida: {p}')
        sys.exit(2)

    def natural_sort_key(s):
        """Chave de ordenação para ordem numérica natural."""
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

    if ext:
        if not ext.startswith('.'):
            ext = f'.{ext}'
        files = sorted(
            [f for f in p.iterdir() if f.is_file() and f.suffix.lower() == ext.lower()],
            key=lambda f: natural_sort_key(f.name)
        )
    else:
        files = sorted(
            [f for f in p.iterdir() if f.is_file()],
            key=lambda f: natural_sort_key(f.name)
        )

    # Evitar renomear este próprio script, caso esteja na pasta alvo
    try:
        script_path = Path(__file__).resolve()
        files = [f for f in files if f.resolve() != script_path]
    except Exception:
        # se algo der errado ao resolver, não bloquear a execução
        pass
    return files


def main():
    # Aceita duas formas:
    # 1) py scripts/rename_simple.py PREFIX [EXT]        -> usa pasta atual
    # 2) py scripts/rename_simple.py PASTA PREFIX [EXT] -> usa PASTA
    if len(sys.argv) < 2:
        print('Uso: py scripts/rename_simple.py [PASTA] PREFIX [EXT]')
        return 2

    if len(sys.argv) == 2:
        # só prefix fornecido
        folder = '.'
        prefix = sys.argv[1]
        ext = None
    elif len(sys.argv) == 3:
        # dois argumentos: prefix + possivel ext (interpretamos como prefix + ext, usando pasta atual)
        folder = '.'
        prefix = sys.argv[1]
        ext = sys.argv[2]
    else:
        # três ou mais: pasta, prefix, (opt) ext
        folder = sys.argv[1]
        prefix = sys.argv[2]
        ext = sys.argv[3] if len(sys.argv) > 3 else None

    files = list_files(folder, ext)
    if not files:
        print('Nenhum arquivo encontrado.')
        return 0

    try:
        start = int(input('Número inicial: ').strip())
    except Exception:
        print('Número inválido.')
        return 2

    mappings = []
    n = start
    for f in files:
        new = f.with_name(f"{prefix}{n}{f.suffix}")
        mappings.append((f, new))
        n += 1

    print('\nProposta de renomeação:')
    for old, new in mappings:
        print(f'{old.name} -> {new.name}')

    resp = input('\nAplicar renomeações? [S/N]: ').strip().lower()
    if resp not in ('s', 'sim', 'y', 'yes'):
        print('Cancelado.')
        return 0

    renamed = 0
    failed = 0
    for old, new in mappings:
        try:
            if new.exists() and new != old:
                # evitar sobrescrever
                base = new.stem
                suf = new.suffix
                parent = new.parent
                i = 1
                while True:
                    cand = parent / f"{base}_{i}{suf}"
                    if not cand.exists():
                        new = cand
                        break
                    i += 1
            old.rename(new)
            renamed += 1
        except Exception as e:
            print(f'Falha: {old.name} -> {new.name}: {e}')
            failed += 1

    print(f'Feito. Renomeados: {renamed}. Falharam: {failed}.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
