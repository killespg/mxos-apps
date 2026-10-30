//! Modelo de app do MXOS: uma janela com um contador. Copie esta pasta,
//! troque o nome no Cargo.toml e escreva um mxa.json para virar pacote.

#![no_std]
#![no_main]

extern crate alloc;

use alloc::format;

use mxos::entrada::Botao;
use mxos::gui::grafico::{Retangulo, Superficie};
use mxos::gui::janelas::{App, EventoApp};
use mxos::gui::{tema, widgets};

struct Modelo {
    cliques: u32,
}

const BOTAO: Retangulo = Retangulo { x: 20, y: 64, largura: 140, altura: widgets::ALTURA_BOTAO };

impl App for Modelo {
    fn titulo(&self) -> &str {
        "Modelo"
    }

    fn tamanho(&self) -> (usize, usize) {
        (360, 120)
    }

    fn desenhar(&mut self, s: &mut Superficie) {
        let t = tema::atual();
        s.limpar(t.fundo_janela);
        s.texto(20, 20, &format!("Cliques: {}", self.cliques), t.texto, 2);
        widgets::botao(s, BOTAO, "Clique aqui", true);
    }

    fn evento(&mut self, e: EventoApp) -> bool {
        match e {
            EventoApp::Botao { x, y, botao: Botao::Esquerdo, pressionado: false } if BOTAO.contem(x, y) => {
                self.cliques += 1;
                true
            }
            _ => false,
        }
    }
}

mxos::app!(|| Modelo { cliques: 0 });
