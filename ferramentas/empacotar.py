"""Compila os apps e gera os pacotes .mxa e o indice.json da Loja do MXOS.

Uso:  python ferramentas/empacotar.py            (todos os apps)
      python ferramentas/empacotar.py calculadora

Cada app em apps/<pasta>/ tem um mxa.json com id, nome, descricao, autor,
licenca e icone; a versao vem do Cargo.toml. O pacote leva o programa
das duas arquiteturas (armv7 = TV box RK322x, aarch64 = QEMU e MXQ) e o
que estiver em apps/<pasta>/dados/ (o app le com caminhos relativos).

Um .mxa e um tar (ustar) comprimido com gzip, com manifesto.json na raiz.
"""

import gzip
import io
import json
import pathlib
import re
import subprocess
import sys
import tarfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ALVOS = {"armv7": "armv7a-none-eabihf", "aarch64": "aarch64-unknown-none"}


def versao(cargo: pathlib.Path) -> str:
    achado = re.search(r'^version\s*=\s*"([^"]+)"', cargo.read_text(encoding="utf-8"), re.M)
    if not achado:
        raise SystemExit(f"{cargo}: sem version")
    return achado.group(1)


def nome_do_pacote(cargo: pathlib.Path) -> str:
    achado = re.search(r'^name\s*=\s*"([^"]+)"', cargo.read_text(encoding="utf-8"), re.M)
    return achado.group(1)


def sdk_local() -> list[str]:
    """Com o repositorio do MXOS ao lado (../mxos), usa o SDK de la em vez
    do GitHub (para testar mudancas no SDK antes de publicar)."""
    local = RAIZ.parent / "mxos" / "sdk"
    if not (local / "Cargo.toml").exists():
        return []
    caminho = local.as_posix()
    return ["--config", f'patch."https://github.com/killespg/mxos".mxos-sdk.path="{caminho}"']


def compilar(pacote: str) -> dict:
    programas = {}
    for arquitetura, alvo in ALVOS.items():
        subprocess.run(["cargo", "build", "--release", *sdk_local(), "-p", pacote, "--target", alvo], cwd=RAIZ, check=True)
        programas[arquitetura] = RAIZ / "target" / alvo / "release" / pacote
    return programas


def acrescentar(tar: tarfile.TarFile, nome: str, dados: bytes, executavel: bool = False) -> None:
    info = tarfile.TarInfo(nome)
    info.size = len(dados)
    info.mode = 0o755 if executavel else 0o644
    info.mtime = 0
    tar.addfile(info, io.BytesIO(dados))


def empacotar(pasta: pathlib.Path) -> dict:
    meta = json.loads((pasta / "mxa.json").read_text(encoding="utf-8"))
    cargo = pasta / "Cargo.toml"
    pacote = nome_do_pacote(cargo)
    meta["versao"] = versao(cargo)
    programas = compilar(pacote)
    meta["programas"] = {a: f"{a}/{pacote}" for a in programas}
    bruto = io.BytesIO()
    with tarfile.open(fileobj=bruto, mode="w", format=tarfile.USTAR_FORMAT) as tar:
        acrescentar(tar, "manifesto.json", json.dumps(meta, ensure_ascii=False, indent=2).encode("utf-8"))
        for arquitetura, caminho in programas.items():
            acrescentar(tar, meta["programas"][arquitetura], caminho.read_bytes(), True)
        dados = pasta / "dados"
        if dados.is_dir():
            for arquivo in sorted(dados.rglob("*")):
                if arquivo.is_file():
                    acrescentar(tar, arquivo.relative_to(dados).as_posix(), arquivo.read_bytes())
    saida = RAIZ / "pacotes" / f"{meta['id']}.mxa"
    saida.parent.mkdir(exist_ok=True)
    saida.write_bytes(gzip.compress(bruto.getvalue(), compresslevel=9, mtime=0))
    print(f"{saida.relative_to(RAIZ)}: {meta['nome']} {meta['versao']} ({saida.stat().st_size // 1024} KB)")
    entrada = {k: meta.get(k, "") for k in ("id", "nome", "versao", "descricao", "autor", "licenca", "icone")}
    entrada["tamanho"] = saida.stat().st_size
    entrada["pacote"] = f"pacotes/{meta['id']}.mxa"
    entrada["arquiteturas"] = sorted(programas)
    return entrada


def main() -> None:
    escolhidos = set(sys.argv[1:])
    indice_arquivo = RAIZ / "indice.json"
    indice = json.loads(indice_arquivo.read_text(encoding="utf-8")) if indice_arquivo.exists() else {"apps": []}
    por_id = {a["id"]: a for a in indice.get("apps", [])}
    for pasta in sorted((RAIZ / "apps").iterdir()):
        if not (pasta / "mxa.json").exists():
            continue
        if escolhidos and pasta.name not in escolhidos:
            continue
        entrada = empacotar(pasta)
        por_id[entrada["id"]] = entrada
    indice = {"versao": 1, "apps": sorted(por_id.values(), key=lambda a: a["nome"].lower())}
    indice_arquivo.write_text(json.dumps(indice, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"indice.json: {len(indice['apps'])} apps")


if __name__ == "__main__":
    main()
