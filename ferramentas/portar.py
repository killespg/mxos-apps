"""Traz um app do sistema (src/gui/apps/<nome>.rs do MXOS) para um pacote:
troca `crate::` por `mxos::`, poe o cabecalho no_std e o ponto de entrada.

Uso: python ferramentas/portar.py <arquivo.rs do mxos> <pasta do app> <entrada>

<entrada> e a expressao `fn() -> impl App` do mxos::app!. Serve para a
primeira copia; depois o app evolui aqui.
"""

import pathlib
import sys


def portar(origem: pathlib.Path, destino: pathlib.Path, entrada: str, trocas: list[tuple[str, str]]) -> None:
    s = origem.read_text(encoding="utf-8")
    for a, b in trocas:
        s = s.replace(a, b)
    s = s.replace("crate::", "mxos::")
    linhas = s.split("\n")
    docs = []
    while linhas and linhas[0].startswith("//!"):
        docs.append(linhas.pop(0))
    corpo = "\n".join(linhas).lstrip("\n").rstrip("\n")
    texto = "\n".join(docs) + "\n\n#![no_std]\n#![no_main]\n\nextern crate alloc;\n\n" + corpo + f"\n\nmxos::app!({entrada});\n"
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "main.rs").write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    portar(pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3], [])
