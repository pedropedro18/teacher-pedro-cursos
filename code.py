"""
Gerador de catálogo de cursos de inglês com inscrição por WhatsApp.

Uso:
    python code.py                # usa cursos.csv (cria exemplo se não existir)
    python code.py meus.csv       # usa outro CSV

CSV (colunas): curso,nivel,preco,duracao,descricao,imagem

Resultado: catalogo.html + catalogo.css (mantenha os dois na mesma pasta).
"""
import csv
import html
import sys
from pathlib import Path
from urllib.parse import quote

# ====== CONFIGURAÇÃO ======
WHATSAPP = "244923030010"   # código do país + número, sem + nem espaços
LOJA = "Teacher Pedro"
SUBTITULO = "Cursos de inglês do A1 ao C2 — inscreva-se pelo WhatsApp"
MOEDA = "Kz"
PERIODO = "/mês"            # deixe "" se o preço não for mensal
SAIDA_HTML = "catalogo.html"
SAIDA_CSS = "catalogo.css"
# ==========================

EXEMPLO = [
    ["curso", "nivel", "preco", "duracao", "descricao", "imagem"],
    ["Inglês A1 - Iniciante", "A1", "15000", "3 meses · 3x por semana",
     "Primeiros passos: cumprimentos, apresentações e vocabulário do dia a dia.", ""],
    ["Inglês A2 - Elementar", "A2", "15000", "3 meses · 3x por semana",
     "Conversas simples sobre rotina, compras, família e viagens.", ""],
    ["Inglês B1 - Intermédio", "B1", "18000", "4 meses · 3x por semana",
     "Fale com mais confiança e compreenda textos e conversas do quotidiano.", ""],
    ["Inglês B2 - Intermédio Superior", "B2", "18000", "4 meses · 3x por semana",
     "Fluência para trabalho, estudos e apresentações.", ""],
    ["Inglês C1 - Avançado", "C1", "20000", "4 meses · 2x por semana",
     "Expressão precisa e natural em contextos académicos e profissionais.", ""],
    ["Inglês C2 - Proficiência", "C2", "20000", "4 meses · 2x por semana",
     "Domínio quase nativo da língua.", ""],
]

# CSS normal (NÃO é f-string), por isso as chaves { } não dão conflito.
CSS = """
* { box-sizing: border-box; }
body { margin: 0; font-family: system-ui, sans-serif; background: #f4f4f5; color: #18181b; }
header { background: #1d4ed8; color: #fff; padding: 20px; text-align: center; }
header h1 { margin: 0; font-size: 1.5rem; }
header p { margin: 6px 0 0; opacity: 0.9; }
.filtros {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  padding: 16px 16px 0;
}
.filtro {
  border: 1px solid #1d4ed8;
  background: #fff;
  color: #1d4ed8;
  padding: 6px 14px;
  border-radius: 999px;
  font-weight: 600;
  cursor: pointer;
}
.filtro.ativo { background: #1d4ed8; color: #fff; }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
  padding: 16px;
  max-width: 1100px;
  margin: auto;
}
.card {
  background: #fff;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.13);
}
.card img, .sem-img {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: 8px;
  background: #dbeafe;
  color: #1d4ed8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.6rem;
  font-weight: 800;
}
.card h3 { margin: 10px 0 4px; font-size: 1.05rem; }
.duracao { margin: 0 0 6px; color: #1d4ed8; font-size: 0.85rem; font-weight: 600; }
.desc { margin: 0; color: #52525b; font-size: 0.9rem; flex: 1; }
.preco { font-weight: 700; font-size: 1.15rem; margin: 10px 0; }
.btn {
  background: #25d366;
  color: #fff;
  text-align: center;
  padding: 10px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
}
"""

# JavaScript normal (NÃO é f-string): filtra os cursos por nível.
JS = """
document.querySelectorAll('.filtro').forEach(function (b) {
  b.addEventListener('click', function () {
    document.querySelectorAll('.filtro').forEach(function (x) { x.classList.remove('ativo'); });
    b.classList.add('ativo');
    var n = b.dataset.nivel;
    document.querySelectorAll('.card').forEach(function (c) {
      c.style.display = (n === 'todos' || c.dataset.nivel === n) ? '' : 'none';
    });
  });
});
"""


def criar_exemplo(caminho: Path) -> None:
    with caminho.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(EXEMPLO)
    print(f"Criado ficheiro de exemplo: {caminho}")


def ler_cursos(caminho: Path) -> list[dict]:
    with caminho.open(newline="", encoding="utf-8") as f:
        return [
            {k.strip(): (v or "").strip() for k, v in linha.items()}
            for linha in csv.DictReader(f)
            if (linha.get("curso") or "").strip()
        ]


def formatar_preco(valor: str) -> str:
    try:
        n = float(valor.replace(",", "."))
        return f"{n:,.0f}".replace(",", ".") + f" {MOEDA}{PERIODO}"
    except ValueError:
        return valor


def link_whatsapp(c: dict) -> str:
    msg = (
        f"Olá! Tenho interesse no curso:\n"
        f"{c['curso']} - {formatar_preco(c.get('preco', ''))}\n"
        f"Pode dar-me informações sobre horários e inscrição?"
    )
    return f"https://wa.me/{WHATSAPP}?text={quote(msg)}"


def cartao(c: dict) -> str:
    esc = html.escape
    nivel = c.get("nivel", "")
    if c.get("imagem"):
        img = f'<img src="{esc(c["imagem"])}" alt="{esc(c["curso"])}">'
    else:
        img = f'<div class="sem-img">{esc(nivel or "EN")}</div>'
    duracao = f'<p class="duracao">{esc(c["duracao"])}</p>' if c.get("duracao") else ""

    return f"""
    <article class="card" data-nivel="{esc(nivel)}">
      {img}
      <h3>{esc(c['curso'])}</h3>
      {duracao}
      <p class="desc">{esc(c.get('descricao', ''))}</p>
      <p class="preco">{esc(formatar_preco(c.get('preco', '')))}</p>
      <a class="btn" href="{link_whatsapp(c)}" target="_blank" rel="noopener">
        Inscrever-me no WhatsApp
      </a>
    </article>"""


def gerar_html(cursos: list[dict]) -> str:
    cartoes = "\n".join(cartao(c) for c in cursos)
    niveis = sorted({c["nivel"] for c in cursos if c.get("nivel")})
    botoes = '<button class="filtro ativo" data-nivel="todos">Todos</button>' + "".join(
        f'<button class="filtro" data-nivel="{html.escape(n)}">{html.escape(n)}</button>'
        for n in niveis
    )
    return f"""<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(LOJA)} - Cursos de Inglês</title>
<link rel="stylesheet" href="{SAIDA_CSS}">
</head>
<body>
<header>
  <h1>{html.escape(LOJA)}</h1>
  <p>{html.escape(SUBTITULO)}</p>
</header>
<nav class="filtros">{botoes}</nav>
<main class="grid">{cartoes}
</main>
<script>{JS}</script>
</body>
</html>"""


def main() -> None:
    csv_path = Path(sys.argv[1] if len(sys.argv) > 1 else "cursos.csv")
    if not csv_path.exists():
        criar_exemplo(csv_path)

    cursos = ler_cursos(csv_path)
    Path(SAIDA_CSS).write_text(CSS.strip() + "\n", encoding="utf-8")
    Path(SAIDA_HTML).write_text(gerar_html(cursos), encoding="utf-8")
    print(f"Catálogo gerado com {len(cursos)} cursos: {SAIDA_HTML} + {SAIDA_CSS}")


if __name__ == "__main__":
    main()