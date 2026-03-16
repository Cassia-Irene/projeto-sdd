import json
import os
import folium
from src.logic import contar_por_categoria, calcular_risco_enchente_vs_chuva, LIMIAR_CHUVA_EMERGENCIAL_MM, identificar_bairros_desassistidos
from src.structures import carregar_familias, carregar_chuvas, construir_matriz_cestas
from src.sorting import merge_sort_familias


# ── Mapa de calor
def _gerar_mapa_calor():
    familias = carregar_familias()

    cor_risco = {
        'Grave':    '#e84040',
        'Moderada': '#f59e0b',
        'Leve':     '#38bdf8',
        'Seguro':   '#34d399',
    }

    mapa = folium.Map(location=[-2.5391, -44.2829], zoom_start=12, tiles='CartoDB positron')

    for dados in familias.values():
        nivel = dados.get('inseguranca', 'Seguro')
        cor   = cor_risco.get(nivel, '#fff')
        folium.CircleMarker(
            location=[dados['latitude'], dados['longitude']],
            radius=6,
            color=cor,
            fill=True,
            fill_color=cor,
            fill_opacity=0.8,
            tooltip=f"📍 {dados.get('bairro')} — {nivel}"
        ).add_to(mapa)

    return mapa._repr_html_()


# ── Dados para os gráficos Chart.js

def _dados_cestas_vs_chuva():
    """
    Cruza a Matriz de Entregas (Bairro × Mês) com os dados pluviométricos.
    Agrega cestas totais por mês (Jan–Jun) e calcula a média de chuva mensal.
    Demonstra causalidade: picos de chuva → aumento de entregas emergenciais.
    """
    _, matriz, meses = construir_matriz_cestas()
    chuvas = carregar_chuvas()

    # Soma de cestas por coluna (mês) na matriz — operação sobre lista de listas
    # Cada linha é um bairro; somamos verticalmente para obter o total mensal
    n_meses = len(meses)  # 6
    cestas_por_mes = [0] * n_meses
    for linha_bairro in matriz:
        for mes_idx, qtd in enumerate(linha_bairro[:n_meses]):
            cestas_por_mes[mes_idx] += qtd

    # Média de chuva mensal
    acum = {m: [] for m in range(n_meses)}
    for dia in chuvas:
        mes_idx = int(dia['data'][5:7]) - 1 
        if 0 <= mes_idx < n_meses:
            acum[mes_idx].append(dia['chuva_mm'])

    chuva_media = [
        round(sum(v) / len(v), 1) if v else 0.0
        for v in acum.values()
    ]

    return {
        'labels':  meses,            # ['Jan','Fev','Mar','Abr','Mai','Jun']
        'cestas':  cestas_por_mes,   # total de cestas entregues por mês
        'chuva':   chuva_media,      # mm médio por mês
    }


def _dados_chuva_alerta():
    datas, chuva_mm, alerta_familias = calcular_risco_enchente_vs_chuva()
    meses_acum = {}
    for i, data in enumerate(datas):
        mes = data[:7]
        if mes not in meses_acum:
            meses_acum[mes] = {'chuva': [], 'alerta': []}
        meses_acum[mes]['chuva'].append(chuva_mm[i])
        meses_acum[mes]['alerta'].append(alerta_familias[i])

    labels = sorted(meses_acum.keys())
    chuva_media = [round(sum(meses_acum[m]['chuva']) / len(meses_acum[m]['chuva']), 1) for m in labels]
    alerta_max  = [max(meses_acum[m]['alerta']) for m in labels]

    nomes_meses = {
        '2026-01': 'Jan/26', '2026-02': 'Fev/26', '2026-03': 'Mar/26',
        '2025-01': 'Jan/25', '2025-02': 'Fev/25', '2025-03': 'Mar/25',
    }
    labels_br = [nomes_meses.get(l, l) for l in labels]

    return {'labels': labels_br, 'chuva': chuva_media, 'alerta': alerta_max}


def _dados_cobertura_auxilio():
    dados = carregar_familias()
    niveis = ['Grave', 'Moderada', 'Leve', 'Seguro']
    atendidos     = {n: 0 for n in niveis}
    nao_atendidos = {n: 0 for n in niveis}

    for f in dados.values():
        nivel = f.get('inseguranca', 'Seguro')
        if f.get('ja_recebe_auxilio'):
            atendidos[nivel] += 1
        else:
            nao_atendidos[nivel] += 1

    return {
        'labels': niveis,
        'atendidos':     [atendidos[n]     for n in niveis],
        'nao_atendidos': [nao_atendidos[n] for n in niveis],
    }


def _dados_privacoes():
    dados = carregar_familias()
    contagem = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    for f in dados.values():
        total = sum([
            bool(f.get('tem_menor_18')),
            bool(f.get('escolaridade_baixa')),
            bool(f.get('doenca_recente')),
            bool(f.get('saude_mental')),
        ])
        contagem[total] += 1

    return {
        'labels': ['Nenhum', '1 fator', '2 fatores', '3 fatores', '4 fatores'],
        'values': [contagem[i] for i in range(5)],
        'colors': ['#34d399', '#38bdf8', '#f59e0b', '#e84040', '#c0392b'],
    }


# ── Tabela ordenada
def _gerar_linhas_tabela():
    dados = carregar_familias()
    lista_familias = list(dados.values())
    familias_prioritarias = merge_sort_familias(lista_familias)

    cor_risco = {
        'Grave':    '#e84040',
        'Moderada': '#f59e0b',
        'Leve':     '#38bdf8',
        'Seguro':   '#34d399',
    }
    moradias_criticas = {'Palafita', 'Taipa/Barro', 'Casa de Madeira'}

    linhas = ""
    for i, f in enumerate(familias_prioritarias):
        moradia = f.get('tipo_moradia', '—')
        infra   = f"⚠️ {moradia}" if moradia in moradias_criticas else f"✓ {moradia}"
        cor     = cor_risco.get(f['inseguranca'], '#fff')
        auxilio = "✓ Sim" if f['ja_recebe_auxilio'] else "✗ Não"

        def sim_nao(v): return "Sim" if v else "Não"

        vuln_label = {3: "🔴 Alta", 2: "🟡 Média", 1: "🟢 Baixa"}.get(
            f.get('vulnerabilidade_territorial', 2), "—"
        )

        linhas += f"""
        <tr
          class="familia-row"
          data-risco="{f['inseguranca']}"
          data-auxilio="{'sim' if f['ja_recebe_auxilio'] else 'nao'}"
          data-bairro="{f['bairro']}"
          data-responsavel="{f.get('responsavel','—')}"
          data-inseguranca="{f['inseguranca']}"
          data-cor-risco="{cor}"
          data-renda="{f['renda_sm']:.2f}"
          data-membros="{f.get('membros', '—')}"
          data-renda-pc="{f.get('renda_pc_sm', '—')}"
          data-moradia="{moradia}"
          data-tem-menor="{sim_nao(f.get('tem_menor_18'))}"
          data-escolaridade="{sim_nao(f.get('escolaridade_baixa'))}"
          data-raca-preta="{sim_nao(f.get('raca_preta'))}"
          data-doenca="{sim_nao(f.get('doenca_recente'))}"
          data-saude-mental="{sim_nao(f.get('saude_mental'))}"
          data-auxilio-label="{'Sim' if f['ja_recebe_auxilio'] else 'Não'}"
          data-vuln="{vuln_label}"
          style="cursor:pointer;"
        >
            <td class="rank">#{i+1}</td>
            <td>{f['bairro']}</td>
            <td style="color:{cor}; font-weight:700;">{f['inseguranca']}</td>
            <td class="mono">R$ {f['renda_sm']:.2f} SM</td>
            <td>{infra}</td>
            <td>{auxilio}</td>
        </tr>"""
    return linhas


# ── Modal HTML + JS do modal
_MODAL_BLOCK = """
  <!-- ── Modal de detalhes da família ── -->
  <div id="modal-overlay" style="
    display:none; position:fixed; inset:0; z-index:9999;
    background:rgba(9,18,28,0.85); backdrop-filter:blur(4px);
    align-items:center; justify-content:center; padding:16px;
  ">
    <div id="modal-box" style="
      background:#162330; border:1px solid #1e3a4a; border-radius:14px;
      width:100%; max-width:480px; padding:28px 24px 24px;
      box-shadow:0 24px 60px rgba(0,0,0,.6);
      position:relative; font-family:'DM Sans',sans-serif;
      animation: modalIn .22s ease;
    ">
      <style>
        @keyframes modalIn {
          from { opacity:0; transform:translateY(14px) scale(.97); }
          to   { opacity:1; transform:translateY(0)    scale(1);   }
        }
        #modal-box h2 {
          font-family:'Space Mono',monospace;
          font-size:14px; color:#e8f4f8; margin-bottom:4px;
          padding-right:28px; line-height:1.4;
        }
        #modal-box .modal-bairro {
          font-size:11px; color:#8ab4c2; margin-bottom:18px;
          font-family:'Space Mono',monospace;
        }
        #modal-close {
          position:absolute; top:16px; right:16px;
          background:transparent; border:none; color:#8ab4c2;
          font-size:20px; cursor:pointer; line-height:1;
          padding:4px 8px; border-radius:4px;
          transition:color .15s, background .15s;
        }
        #modal-close:hover { color:#e8f4f8; background:#1e3a4a; }
        .modal-badge {
          display:inline-block; padding:3px 10px; border-radius:4px;
          font-family:'Space Mono',monospace; font-size:11px;
          font-weight:700; margin-bottom:18px;
          border:1px solid; letter-spacing:.5px;
        }
        .modal-grid {
          display:grid; grid-template-columns:1fr 1fr; gap:10px;
        }
        .modal-item {
          background:#0f1923; border:1px solid #1e3a4a;
          border-radius:8px; padding:10px 12px;
        }
        .modal-item .label {
          font-size:9px; text-transform:uppercase; letter-spacing:1.5px;
          color:#8ab4c2; font-family:'Space Mono',monospace;
          margin-bottom:4px;
        }
        .modal-item .value {
          font-size:13px; color:#e8f4f8; font-weight:600;
        }
        .modal-item .value.warn { color:#f59e0b; }
        .modal-item .value.ok   { color:#34d399; }
        .modal-divider {
          height:1px; background:#1e3a4a; margin:16px 0;
        }
        .modal-section-title {
          font-family:'Space Mono',monospace; font-size:9px;
          text-transform:uppercase; letter-spacing:2px;
          color:#8ab4c2; margin-bottom:10px;
        }
        .modal-flags { display:flex; flex-wrap:wrap; gap:7px; }
        .flag {
          display:flex; align-items:center; gap:5px;
          background:#0f1923; border:1px solid #1e3a4a;
          border-radius:6px; padding:5px 9px;
          font-size:11px; color:#8ab4c2;
        }
        .flag .dot { width:7px; height:7px; border-radius:50%; flex-shrink:0; }
        .dot-yes { background:#e84040; }
        .dot-no  { background:#34d399; }
      </style>

      <button id="modal-close" onclick="fecharModal()">✕</button>
      <h2 id="modal-nome">—</h2>
      <div class="modal-bairro" id="modal-bairro">—</div>
      <span class="modal-badge" id="modal-risco-badge">—</span>

      <div class="modal-grid">
        <div class="modal-item">
          <div class="label">Renda familiar</div>
          <div class="value mono" id="m-renda">—</div>
        </div>
        <div class="modal-item">
          <div class="label">Renda per capita</div>
          <div class="value mono" id="m-renda-pc">—</div>
        </div>
        <div class="modal-item">
          <div class="label">Membros</div>
          <div class="value" id="m-membros">—</div>
        </div>
        <div class="modal-item">
          <div class="label">Moradia</div>
          <div class="value" id="m-moradia">—</div>
        </div>
        <div class="modal-item">
          <div class="label">Recebe auxílio</div>
          <div class="value" id="m-auxilio">—</div>
        </div>
        <div class="modal-item">
          <div class="label">Território</div>
          <div class="value" id="m-vuln">—</div>
        </div>
      </div>

      <div class="modal-divider"></div>
      <div class="modal-section-title">Fatores de risco identificados</div>
      <div class="modal-flags" id="modal-flags"></div>
    </div>
  </div>

  <script>
  // ── Modal ──────────────────────────────────────────────────────────────────
  const overlay = document.getElementById('modal-overlay');

  document.querySelectorAll('.familia-row').forEach(tr => {
    tr.addEventListener('click', () => {
      const d = tr.dataset;

      document.getElementById('modal-nome').textContent   = d.responsavel;
      document.getElementById('modal-bairro').textContent = '📍 ' + d.bairro;

      const badge = document.getElementById('modal-risco-badge');
      badge.textContent        = d.inseguranca;
      badge.style.color        = d.corRisco;
      badge.style.borderColor  = d.corRisco;
      badge.style.background   = d.corRisco + '18';

      document.getElementById('m-renda').textContent    = d.renda + ' SM';
      document.getElementById('m-renda-pc').textContent = d.rendaPc + ' SM';
      document.getElementById('m-membros').textContent  = d.membros + ' pessoa(s)';

      const moradiasCriticas = ['Palafita','Taipa/Barro','Casa de Madeira'];
      const mEl = document.getElementById('m-moradia');
      mEl.textContent = d.moradia;
      mEl.className   = 'value ' + (moradiasCriticas.includes(d.moradia) ? 'warn' : 'ok');

      const auxEl = document.getElementById('m-auxilio');
      auxEl.textContent = d.auxilioLabel;
      auxEl.className   = 'value ' + (d.auxilioLabel === 'Sim' ? 'ok' : 'warn');

      document.getElementById('m-vuln').textContent = d.vuln;

      const flags = [
        { label: 'Menor de 18',        val: d.temMenor     },
        { label: 'Escolaridade baixa',  val: d.escolaridade },
        { label: 'Doença recente',      val: d.doenca       },
        { label: 'Saúde mental',        val: d.saudeMental  },
        { label: 'Raça preta',          val: d.racaPreta    },
      ];
      document.getElementById('modal-flags').innerHTML = flags.map(f =>
        `<div class="flag">
           <div class="dot ${f.val === 'Sim' ? 'dot-yes' : 'dot-no'}"></div>
           ${f.label}: <strong>${f.val}</strong>
         </div>`
      ).join('');

      overlay.style.display = 'flex';
      document.body.style.overflow = 'hidden';
    });
  });

  function fecharModal() {
    overlay.style.display = 'none';
    document.body.style.overflow = '';
  }
  overlay.addEventListener('click', e => { if (e.target === overlay) fecharModal(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') fecharModal(); });

  // ── Filtros ────────────────────────────────────────────────────────────────
  function aplicarFiltros() {
    const risco   = document.getElementById('filtro-risco').value;
    const auxilio = document.getElementById('filtro-auxilio').value;
    const bairro  = document.getElementById('filtro-bairro').value;
    const linhas  = document.querySelectorAll('#corpo-tabela tr');
    let visiveis  = 0;
    linhas.forEach(tr => {
      const ok = (!risco   || tr.dataset.risco   === risco)
              && (!auxilio || tr.dataset.auxilio  === auxilio)
              && (!bairro  || tr.dataset.bairro   === bairro);
      tr.classList.toggle('oculto', !ok);
      if (ok) visiveis++;
    });
    document.getElementById('contador-num').textContent = visiveis;
    document.getElementById('sem-resultado').style.display = visiveis === 0 ? 'block' : 'none';
  }
  function limparFiltros() {
    document.getElementById('filtro-risco').value   = '';
    document.getElementById('filtro-auxilio').value = '';
    document.getElementById('filtro-bairro').value  = '';
    aplicarFiltros();
  }
  </script>
"""


# ── Dashboard HTML ─────────────────────────────────────────────────────────────
def gerar_dashboard_html():
    print("⏳ Gerando visualizações...")

    mapa_html  = _gerar_mapa_calor()
    linhas_tab = _gerar_linhas_tabela()

    d_cestas    = json.dumps(_dados_cestas_vs_chuva(),         ensure_ascii=False)
    d_chuva     = json.dumps(_dados_chuva_alerta(),            ensure_ascii=False)
    d_cobertura = json.dumps(_dados_cobertura_auxilio(),       ensure_ascii=False)
    d_privacoes = json.dumps(_dados_privacoes(),               ensure_ascii=False)
    limiar_js   = LIMIAR_CHUVA_EMERGENCIAL_MM

    resumo     = contar_por_categoria()
    total      = sum(resumo.values())
    graves     = resumo.get('Grave', 0)
    pct_graves = round(graves / total * 100) if total else 0
    desassistidos = len(identificar_bairros_desassistidos())

    dados = carregar_familias()
    bairros_unicos = sorted(set(f['bairro'] for f in dados.values()))
    opcoes_bairro  = '\n'.join(f'<option value="{b}">{b}</option>' for b in bairros_unicos)

    # ── Parte 1: tudo que precisa de f-string (variáveis Python)
    html_parte1 = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard de Inteligência Alimentar — São Luís/MA</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --bg:       #0f1923;
    --surface:  #162330;
    --border:   #1e3a4a;
    --text:     #ffffff;
    --muted:    #ffffff;
    --grave:    #e84040;
    --moderada: #f59e0b;
    --leve:     #38bdf8;
    --seguro:   #34d399;
    --accent:   #38bdf8;
  }}
  body {{
    background: var(--bg); color: var(--text);
    font-family: 'DM Sans', sans-serif;
    min-height: 100vh; overflow-x: hidden;
  }}
  header {{
    background: linear-gradient(135deg, #0d2235 0%, #0f2d40 60%, #0a1e2c 100%);
    border-bottom: 2px solid var(--border);
    padding: 20px 16px;
    display: flex; flex-direction: column; gap: 14px;
  }}
  .header-left h1 {{
    font-family: 'Space Mono', monospace;
    font-size: clamp(15px, 4.5vw, 24px);
    font-weight: 700; color: var(--text); line-height: 1.3;
  }}
  .header-left h1 span {{ color: var(--accent); }}
  .header-left p {{ font-size: 12px; color: var(--muted); margin-top: 5px; font-family: 'Space Mono', monospace; line-height: 1.5; }}
  .header-badges {{ display: flex; gap: 8px; flex-wrap: wrap; }}
  .badge {{ font-family: 'Space Mono', monospace; font-size: 12px; padding: 4px 10px; border-radius: 4px; border: 1px solid; white-space: nowrap; }}
  .badge-grave    {{ border-color: var(--grave);    color: var(--grave);    background: rgba(232,64,64,.1); }}
  .badge-moderada {{ border-color: var(--moderada); color: var(--moderada); background: rgba(245,158,11,.1); }}
  .badge-total    {{ border-color: var(--accent);   color: var(--accent);   background: rgba(56,189,248,.1); }}
  main {{ padding: 16px; width: 100%; max-width: 1400px; margin: 0 auto; }}
  .section-label {{
    font-family: 'Space Mono', monospace; font-size: 9px; text-transform: uppercase;
    letter-spacing: 2px; color: var(--muted); margin-bottom: 12px;
    display: flex; align-items: center; gap: 10px;
  }}
  .section-label::after {{ content: ''; flex: 1; height: 1px; background: var(--border); }}
  .card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 16px; margin-bottom: 20px;
  }}
  .card-title {{ font-family: 'Space Mono', monospace; font-size: 14px; font-weight: 700; color: var(--text); margin-bottom: 4px; line-height: 1.4; }}
  .card-sub {{ font-size: 11px; color: var(--muted); margin-bottom: 14px; line-height: 1.5; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr; gap: 20px; margin-bottom: 20px; }}
  .chart-container {{ position: relative; width: 100%; height: 260px; }}
  .chart-container canvas {{ width: 100% !important; }}
  .filtros {{ display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 16px; align-items: flex-end; }}
  .filtro-grupo {{ display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 130px; }}
  .filtro-grupo label {{ font-family: 'Space Mono', monospace; font-size: 9px; text-transform: uppercase; letter-spacing: 1px; color: var(--muted); }}
  .filtro-grupo select {{
    background: var(--bg); color: var(--text); border: 1px solid var(--border);
    border-radius: 6px; padding: 7px 10px; font-family: 'DM Sans', sans-serif;
    font-size: 12px; cursor: pointer; width: 100%; appearance: none; -webkit-appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%238ab4c2'/%3E%3C/svg%3E");
    background-repeat: no-repeat; background-position: right 10px center; padding-right: 28px;
  }}
  .filtro-grupo select:focus {{ outline: none; border-color: var(--accent); }}
  .btn-limpar {{
    background: transparent; color: var(--muted); border: 1px solid var(--border);
    border-radius: 6px; padding: 7px 14px; font-family: 'Space Mono', monospace;
    font-size: 10px; cursor: pointer; white-space: nowrap; align-self: flex-end;
  }}
  .btn-limpar:hover {{ border-color: var(--accent); color: var(--accent); }}
  .contador-resultado {{ font-family: 'Space Mono', monospace; font-size: 10px; color: var(--muted); margin-bottom: 10px; }}
  .contador-resultado span {{ color: var(--accent); font-weight: 700; }}
  .table-scroll {{ width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; border-radius: 6px; }}
  .table-scroll::-webkit-scrollbar {{ height: 4px; }}
  .table-scroll::-webkit-scrollbar-track {{ background: var(--bg); }}
  .table-scroll::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 2px; }}
  table {{ width: 100%; min-width: 520px; border-collapse: collapse; font-size: 12px; }}
  thead th {{
    font-family: 'Space Mono', monospace; font-size: 9px; text-transform: uppercase;
    letter-spacing: 1px; color: var(--muted); padding: 9px 12px;
    text-align: left; border-bottom: 1px solid var(--border);
    background: rgba(255,255,255,.02); white-space: nowrap;
  }}
  tbody tr {{ border-bottom: 1px solid var(--border); transition: background .15s; }}
  tbody tr:hover {{ background: rgba(56,189,248,.05); }}
  tbody tr:active {{ background: rgba(56,189,248,.07); }}
  tbody tr.oculto {{ display: none; }}
  tbody td {{ padding: 10px 12px; color: var(--text); vertical-align: middle; white-space: nowrap; }}
  td.rank {{ font-family: 'Space Mono', monospace; color: var(--muted); font-size: 10px; width: 32px; }}
  td.mono {{ font-family: 'Space Mono', monospace; font-size: 11px; }}
  .sem-resultado {{ display: none; padding: 24px; text-align: center; color: var(--muted); font-family: 'Space Mono', monospace; font-size: 11px; }}
  .mapa-wrap {{ border-radius: 8px; overflow: hidden; height: 320px; }}
  .mapa-wrap > div {{ height: 100% !important; }}
  footer {{
    text-align: center; padding: 16px;
    font-family: 'Space Mono', monospace; font-size: 9px;
    color: var(--muted); border-top: 1px solid var(--border);
    margin-top: 8px; line-height: 1.6;
  }}
  @media (min-width: 640px) {{
    header {{ padding: 24px 32px; flex-direction: row; align-items: flex-end; justify-content: space-between; }}
    main {{ padding: 24px 32px; }}
    .card {{ padding: 20px; }}
    .mapa-wrap {{ height: 420px; }}
    table {{ font-size: 13px; }}
    thead th {{ font-size: 10px; }}
  }}
  @media (min-width: 900px) {{
    header {{ padding: 28px 40px 24px; }}
    main {{ padding: 32px 40px; }}
    .card {{ padding: 24px; }}
    .grid-2 {{ grid-template-columns: 1fr 1fr; }}
    .mapa-wrap {{ height: 480px; }}
  }}
</style>
</head>
<body>

<header>
  <div class="header-left">
    <h1>🥗 Inteligência Alimentar<span> // SLZ</span></h1>
    <p>Ecossistema de monitoramento de vulnerabilidade · São Luís, Maranhão</p>
  </div>
  <div class="header-badges">
    <span class="badge badge-total">👥 {total} famílias</span>
    <span class="badge badge-grave">🔴 {graves} graves ({pct_graves}%)</span>
    <span class="badge badge-moderada">📍 {desassistidos} bairros sem cobertura</span>
  </div>
</header>

<main>

  <div class="section-label">01 — Plano de Ação Prioritário</div>
  <div class="card">
    <div class="card-title">Famílias Cadastradas</div>
    <div class="card-sub">Ordenadas por gravidade e renda via Merge Sort · clique em uma linha para ver detalhes</div>
    <div class="filtros">
      <div class="filtro-grupo">
        <label>Nível de risco</label>
        <select id="filtro-risco" onchange="aplicarFiltros()">
          <option value="">Todos</option>
          <option value="Grave">Grave</option>
          <option value="Moderada">Moderada</option>
          <option value="Leve">Leve</option>
          <option value="Seguro">Seguro</option>
        </select>
      </div>
      <div class="filtro-grupo">
        <label>Recebe auxílio</label>
        <select id="filtro-auxilio" onchange="aplicarFiltros()">
          <option value="">Todos</option>
          <option value="sim">✓ Sim</option>
          <option value="nao">✗ Não</option>
        </select>
      </div>
      <div class="filtro-grupo">
        <label>Bairro</label>
        <select id="filtro-bairro" onchange="aplicarFiltros()">
          <option value="">Todos</option>
          {opcoes_bairro}
        </select>
      </div>
      <button class="btn-limpar" onclick="limparFiltros()">✕ Limpar</button>
    </div>
    <div class="contador-resultado" id="contador">
      Exibindo <span id="contador-num">{total}</span> família(s)
    </div>
    <div class="table-scroll">
      <table>
        <thead>
          <tr><th>#</th><th>Bairro</th><th>Risco</th><th>Renda</th><th>Infra</th><th>Auxílio</th></tr>
        </thead>
        <tbody id="corpo-tabela">{linhas_tab}</tbody>
      </table>
      <div class="sem-resultado" id="sem-resultado">Nenhuma família encontrada com esses filtros.</div>
    </div>
  </div>

  <div class="section-label">02 — Análise Estatística</div>
  <div class="grid-2">
    <div class="card">
      <div class="card-title">Inteligência Preditiva — Cestas × Precipitação</div>
      <div class="card-sub">Cruzamento da Matriz de Entregas com dados pluviométricos · barras = cestas entregues · linha = chuva média (mm)</div>
      <div class="chart-container"><canvas id="chartCestasVsChuva"></canvas></div>
    </div>
    <div class="card">
      <div class="card-title">Monitoramento Sazonal — Chuva × Alerta</div>
      <div class="card-sub">Precipitação média mensal vs famílias em alerta (limiar: {limiar_js} mm/dia)</div>
      <div class="chart-container"><canvas id="chartChuva"></canvas></div>
    </div>
    <div class="card">
      <div class="card-title">Cobertura de Auxílio por Nível de Risco</div>
      <div class="card-sub">Quem está em situação grave mas ainda não é atendido</div>
      <div class="chart-container"><canvas id="chartCobertura"></canvas></div>
    </div>
    <div class="card">
      <div class="card-title">Acúmulo de Fatores de Risco por Família</div>
      <div class="card-sub">Menor de 18 · Escolaridade baixa · Doença recente · Saúde mental</div>
      <div class="chart-container"><canvas id="chartPrivacoes"></canvas></div>
    </div>
  </div>

  <div class="section-label">03 — Mapa de Calor de Vulnerabilidade</div>
  <div class="card">
    <div class="card-title">Distribuição Espacial do Risco — São Luís/MA</div>
    <div class="card-sub">azul → amarelo → vermelho = leve → moderado → grave</div>
    <div class="mapa-wrap">{mapa_html}</div>
  </div>

</main>

<footer>
  Ecossistema de Inteligência Alimentar · São Luís/MA<br>
  Dados: Portal da Transparência (NovaBF/2024)
</footer>
"""

    # ── Parte 2: script dos gráficos
    html_parte2 = f"""
<script>
  const dadosCestas    = {d_cestas};
  const dadosChuva     = {d_chuva};
  const dadosCobertura = {d_cobertura};
  const dadosPrivacoes = {d_privacoes};

  Chart.defaults.color = '#8ab4c2';
  Chart.defaults.font.family = "'DM Sans', sans-serif";
  Chart.defaults.font.size   = 11;
  const tooltipDefaults = {{
    backgroundColor: '#0f1923', borderColor: '#1e3a4a', borderWidth: 1,
    titleColor: '#e8f4f8', bodyColor: '#8ab4c2', padding: 10, cornerRadius: 6,
  }};

  new Chart(document.getElementById('chartCestasVsChuva'), {{
    type: 'bar',
    data: {{
      labels: dadosCestas.labels,
      datasets: [
        {{
          label: 'Cestas entregues (total)',
          data: dadosCestas.cestas,
          backgroundColor: 'rgba(56,189,248,0.75)',
          borderColor: '#38bdf8',
          borderWidth: 1,
          borderRadius: 4,
          yAxisID: 'y',
          order: 2,
        }},
        {{
          label: 'Chuva média (mm)',
          data: dadosCestas.chuva,
          type: 'line',
          borderColor: '#f59e0b',
          backgroundColor: 'rgba(245,158,11,0.12)',
          fill: true,
          tension: 0.4,
          pointRadius: 5,
          pointHoverRadius: 7,
          pointBackgroundColor: '#f59e0b',
          borderWidth: 2,
          yAxisID: 'y2',
          order: 1,
        }}
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      animation: {{ duration: 1000, easing: 'easeOutQuart' }},
      interaction: {{ mode: 'index', intersect: false }},
      plugins: {{
        legend: {{ display: true, labels: {{ color: '#8ab4c2', boxWidth: 12, padding: 16 }} }},
        tooltip: {{
          ...tooltipDefaults,
          callbacks: {{
            label: ctx => ctx.datasetIndex === 0
              ? ` ${{ctx.parsed.y}} cestas`
              : ` ${{ctx.parsed.y}} mm`,
          }}
        }}
      }},
      scales: {{
        x: {{ grid: {{ color: '#1e3a4a' }}, ticks: {{ color: '#e8f4f8' }} }},
        y: {{
          grid: {{ color: '#1e3a4a' }},
          ticks: {{ color: '#38bdf8' }},
          title: {{ display: true, text: 'Cestas', color: '#38bdf8', font: {{ size: 10 }} }},
        }},
        y2: {{
          position: 'right',
          grid: {{ display: false }},
          ticks: {{ color: '#f59e0b' }},
          title: {{ display: true, text: 'mm/mês', color: '#f59e0b', font: {{ size: 10 }} }},
        }}
      }}
    }}
  }});

  new Chart(document.getElementById('chartChuva'), {{
    type: 'line',
    data: {{
      labels: dadosChuva.labels,
      datasets: [
        {{
          label: 'Precipitação média (mm)', data: dadosChuva.chuva,
          borderColor: '#60a5fa', backgroundColor: 'rgba(96,165,250,0.15)',
          fill: true, tension: 0.4, pointRadius: 5, pointHoverRadius: 7,
          pointBackgroundColor: '#60a5fa', yAxisID: 'y',
        }},
        {{
          label: 'Famílias em alerta', data: dadosChuva.alerta,
          borderColor: '#f87171', backgroundColor: 'rgba(248,113,113,0.15)',
          fill: true, tension: 0.4, pointRadius: 5, pointHoverRadius: 7,
          pointBackgroundColor: '#f87171', yAxisID: 'y2',
        }}
      ]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      animation: {{ duration: 1000, easing: 'easeOutCubic' }},
      interaction: {{ mode: 'index', intersect: false }},
      plugins: {{
        legend: {{ display: true, labels: {{ color: '#8ab4c2', boxWidth: 12, padding: 16 }} }},
        tooltip: {{
          ...tooltipDefaults,
          callbacks: {{ label: ctx => ctx.datasetIndex === 0 ? ` ${{ctx.parsed.y}} mm` : ` ${{ctx.parsed.y}} famílias` }}
        }},
      }},
      scales: {{
        x: {{ grid: {{ color: '#1e3a4a' }}, ticks: {{ color: '#8ab4c2' }} }},
        y: {{ grid: {{ color: '#1e3a4a' }}, ticks: {{ color: '#60a5fa' }}, title: {{ display: true, text: 'mm/mês', color: '#60a5fa', font: {{ size: 10 }} }} }},
        y2: {{ position: 'right', grid: {{ display: false }}, ticks: {{ color: '#f87171' }}, title: {{ display: true, text: 'Famílias', color: '#f87171', font: {{ size: 10 }} }} }}
      }}
    }}
  }});

  new Chart(document.getElementById('chartCobertura'), {{
    type: 'bar',
    data: {{
      labels: dadosCobertura.labels,
      datasets: [
        {{ label: 'Recebe auxílio', data: dadosCobertura.atendidos, backgroundColor: 'rgba(52,211,153,0.8)', borderColor: '#34d399', borderWidth: 1, borderRadius: 4 }},
        {{ label: 'Sem auxílio',    data: dadosCobertura.nao_atendidos, backgroundColor: 'rgba(232,64,64,0.75)', borderColor: '#e84040', borderWidth: 1, borderRadius: 4 }}
      ]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      animation: {{ duration: 900, easing: 'easeOutQuart' }},
      interaction: {{ mode: 'index', intersect: false }},
      plugins: {{
        legend: {{ display: true, labels: {{ color: '#8ab4c2', boxWidth: 12, padding: 16 }} }},
        tooltip: {{ ...tooltipDefaults, callbacks: {{ label: ctx => ` ${{ctx.parsed.y}} famílias — ${{ctx.dataset.label}}` }} }}
      }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ color: '#e8f4f8' }} }},
        y: {{ grid: {{ color: '#1e3a4a' }}, ticks: {{ color: '#8ab4c2' }} }}
      }}
    }}
  }});

  new Chart(document.getElementById('chartPrivacoes'), {{
    type: 'bar',
    data: {{
      labels: dadosPrivacoes.labels,
      datasets: [{{
        label: 'Famílias', data: dadosPrivacoes.values,
        backgroundColor: dadosPrivacoes.colors.map(c => c + 'cc'),
        borderColor: dadosPrivacoes.colors, borderWidth: 1, borderRadius: 4, borderSkipped: false,
      }}]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      animation: {{ duration: 900, easing: 'easeOutBounce', delay: ctx => ctx.dataIndex * 80 }},
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{ ...tooltipDefaults, callbacks: {{ label: ctx => ` ${{ctx.parsed.y}} famílias` }} }}
      }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ color: '#e8f4f8' }} }},
        y: {{ grid: {{ color: '#1e3a4a' }}, ticks: {{ color: '#8ab4c2' }} }}
      }}
    }}
  }});
</script>
"""

    # ── Concatenação final: f-string parte1 + f-string parte2 + string pura do modal
    html_content = html_parte1 + html_parte2 + _MODAL_BLOCK + "\n</body>\n</html>"

    caminho = os.path.abspath("dashboard_slz.html")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Dashboard gerado: {caminho}")