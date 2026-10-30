# mxos-apps

Apps nativos do [MXOS](https://github.com/killespg/mxos) e o catálogo da **Loja** do sistema.

Tudo o que está em `indice.json` aparece na Loja do MXOS: ela baixa o índice deste repositório, mostra os apps
e instala o pacote `.mxa` de cada um em `/apps/<id>/`. Atualizar um app aqui (versão nova no `Cargo.toml`,
pacote refeito) faz a Loja oferecer a atualização; nenhum app depende de atualizar o sistema.

| App | O que faz |
|---|---|
| Calculadora | contas com inteiros, pelo mouse ou pelo teclado |
| Editor de código | texto com realce de sintaxe e o Claude para explicar e refatorar |
| Pintura | desenho livre |
| CHIP-8 | emulador de jogos `.ch8` |

`apps/modelo` é um app mínimo para copiar (não vai para a Loja).

## Fazer ou atualizar um app

1. Rust com os alvos dos apps: `rustup target add armv7a-none-eabihf aarch64-unknown-none`.
2. Uma pasta em `apps/` com `Cargo.toml`, `src/main.rs` (veja `apps/modelo`) e um `mxa.json`:

   ```json
   {
     "id": "meu-app",
     "nome": "Meu app",
     "descricao": "Uma linha sobre o app.",
     "autor": "Seu nome",
     "licenca": "MIT",
     "icone": "Monitor",
     "extensoes": [".xyz"]
   }
   ```

   `icone` é um dos ícones do sistema (Pasta, Arquivo, Texto, Html, Disco, Rede, Terminal, Navegador,
   Engrenagem, Tarefas, Chip, Pincel, Calculadora, Info, Teclado, Monitor, Som). `extensoes` (opcional): arquivos
   que o app abre; o caminho chega em `mxos::argumentos()`. Arquivos em `apps/<pasta>/dados/` vão dentro do
   pacote (o app lê com caminho relativo).
3. `python ferramentas/empacotar.py meu-app` compila para as duas arquiteturas (ARMv7 da TV box, AArch64 do QEMU
   e da MXQ), gera `pacotes/meu-app.mxa` e atualiza o `indice.json`.
4. Commit e push: a Loja mostra o app.

A API dos apps (janelas, desenho, arquivos, HTTP, som, IA) está no [SDK](https://github.com/killespg/mxos/tree/main/sdk).
Um app do próprio sistema vira pacote com `ferramentas/portar.py`.

## O pacote `.mxa`

Um tar (ustar) comprimido com gzip:

```
manifesto.json        o mxa.json + "versao" + "programas": {"armv7": "armv7/<app>", "aarch64": "aarch64/<app>"}
armv7/<app>           ELF estático de 32 bits
aarch64/<app>         ELF estático de 64 bits
...                   o que estava em dados/
```

Também dá para instalar um `.mxa` direto do disco: aberto no gerenciador de arquivos do MXOS, ele vai para a Loja.

## Licença

Os apps deste repositório são GPL-3.0-or-later (`LICENSE`). Apps de terceiros podem ter qualquer licença: o MXOS
tem uma exceção para apps que só usam a ABI e o SDK (`EXCECAO-APPS.md` no repositório do sistema). O campo
`licenca` do `mxa.json` diz a de cada um.
