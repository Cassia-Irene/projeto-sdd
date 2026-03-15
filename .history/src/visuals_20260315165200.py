import json
import folium
from folium.plugins import HeatMap
import io
import os
from src.logic import contar_por_categoria, calcular_risco_enchente_vs_chuva, obter_dados_mapa_calor
from src.structures import carregar_bairros_coords, carregar_familias
from src.sorting import merge_sort_familias

PALETTE = {
    'bg':        '#0f1923',
    'card':      '#162330',
    'border':    '#1e3a4a',
    'text':      '#e8f4f8',
    'muted':     '#8ab4c2',
    'grave':     '#e84040',
    'moderada':  '#f59e0b',
    'leve':      '#38bdf8',
    'seguro':    '#34d399',
    'chuva':     '#60a5fa',
    'alerta':    '#f87171',
}

def _apply_dark_style(fig, ax_list):
    fig.patch.set_facecolor(PALETTE['bg'])
    for ax in ax_list:
        ax.set_facecolor(PALETTE['card'])
        ax.tick_params(colors=PALETTE['muted'], labelsize=9)
        ax.xaxis.label.set_color(PALETTE['muted'])
        ax.yaxis.label.set_color(PALETTE['muted'])
        ax.title.set_color(PALETTE['text'])
        for spine in ax.spines.values():
            spine.set_edgecolor(PALETTE['border'])

def _plot_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=130,
                facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return base64.b64encode(buf.read()).decode('utf-8')


# ── Gráfico 1: Perfil de vulnerabilidade (barras horizontais) ─────────────────
def _grafico_perfil_vulnerabilidade():
    resumo = contar_por_categoria()
    categorias = ['Seguro', 'Leve', 'Moderada', 'Grave']
    valores    = [resumo.get(c, 0) for c in categorias]
    cores      = [PALETTE['seguro'], PALETTE['leve'], PALETTE['moderada'], PALETTE['grave']]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    _apply_dark_style(fig, [ax])
    bars = ax.barh(categorias, valores, color=cores, height=0.55, zorder=3)
    for bar, val in zip(bars, valores):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f'{val}', va='center', ha='left',
                color=PALETTE['text'], fontsize=11, fontweight='bold',
                fontfamily='monospace')
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=6))
    ax.grid(axis='x', color=PALETTE['border'], linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.set_xlabel('Nº de Famílias', fontsize=9)
    ax.set_title('Perfil de Vulnerabilidade Alimentar', fontsize=12, fontweight='bold', pad=12)
    total = sum(valores)
    ax.axvline(total, color=PALETTE['muted'], linewidth=0.8, linestyle=':', alpha=0.5)
    ax.text(total + 0.2, -0.58, f'Total: {total}', color=PALETTE['muted'], fontsize=8)
    fig.tight_layout()
    return _plot_to_base64(fig)


# ── Gráfico 2: Chuva vs Alerta ────────────────────────────────────────────────
def _dados_perfil_vulnerabilidade():
    resumo = contar_por_categoria()
    return {
        'labels': ['Grave', 'Moderada', 'Leve', 'Seguro'],
        'values': [resumo.get('Grave', 0), resumo.get('Moderada', 0),
                   resumo.get('Leve', 0), resumo.get('Seguro', 0)],
        'colors': ['#e84040', '#f59e0b', '#38bdf8', '#34d399'],
    }


def _dados_chuva_alerta():
    datas, chuva_mm, alerta_familias = calcular_risco_enchente_vs_chuva()
    # Agrupa por mês para o gráfico ficar mais limpo
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

    # Nomes em pt-BR
    nomes_meses = {
        '2026-01': 'Jan/26', '2026-02': 'Fev/26', '2026-03': 'Mar/26',
        '2025-01': 'Jan/25', '2025-02': 'Fev/25', '2025-03': 'Mar/25',
    }
    labels_br = [nomes_meses.get(l, l) for l in labels]

    return {
        'labels': labels_br,
        'chuva': chuva_media,
        'alerta': alerta_max,
    }

# ── Gráfico 3 (NOVO): Cobertura de auxílio por nível de risco ─────────────────
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


# ── Gráfico 4 (NOVO): Privações acumuladas ────────────────────────────────────
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



# ── Mapa de calor ─────────────────────────────────────────────────────────────
def _gerar_mapa_calor():
    familias       = carregar_familias()
    bairros_coords = carregar_bairros_coords()
    lats, lngs, pesos = obter_dados_mapa_calor()  # lógica toda no logic.py

    coords_dict = {
        b['nome']: (b.get('lat'), b.get('lng'))
        for b in bairros_coords
    }

    mapa = folium.Map(location=[-2.5391, -44.2829], zoom_start=12, tiles='CartoDB positron')

    heat_data = []
    bairros_com_familia = set()

    for (lat, lng, peso), dados in zip(zip(lats, lngs, pesos), familias.values()):
        heat_data.append([lat, lng, peso])
        bairros_com_familia.add((dados.get('bairro'), lat, lng))

    HeatMap(heat_data, radius=18, blur=14,
            gradient={0.2: '#3b82f6', 0.5: '#f59e0b', 1.0: '#ef4444'}).add_to(mapa)

    for nome, lat, lng in bairros_com_familia:
        folium.CircleMarker(
            location=[lat, lng], radius=3,
            color="#17978d", fill=True, fill_opacity=0.8,
            tooltip=f"📍 {nome}"
        ).add_to(mapa)

    return mapa._repr_html_()


# ── Tabela: gera todas as linhas com data-attributes para o filtro JS ─────────
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
    # Moradias precárias recebem destaque visual
    moradias_criticas = {'Palafita', 'Taipa/Barro', 'Casa de Madeira'}
 
    linhas = ""
    for i, f in enumerate(familias_prioritarias):
        moradia  = f.get('tipo_moradia', '—')
        infra    = f"⚠️ {moradia}" if moradia in moradias_criticas else f"✓ {moradia}"
        cor      = cor_risco.get(f['inseguranca'], '#fff')
        auxilio  = "✓ Sim" if f['ja_recebe_auxilio'] else "✗ Não"
 
        linhas += f"""
        <tr data-risco="{f['inseguranca']}" data-auxilio="{'sim' if f['ja_recebe_auxilio'] else 'nao'}" data-bairro="{f['bairro']}">
            <td class="rank">#{i+1}</td>
            <td>{f['bairro']}</td>
            <td style="color:{cor}; font-weight:700;">{f['inseguranca']}</td>
            <td class="mono">R$ {f['renda_sm']:.2f} SM</td>
            <td>{infra}</td>
            <td>{auxilio}</td>
        </tr>"""
    return linhas


# ── Dashboard HTML ─────────────────────────────────────────────────────────────
def gerar_dashboard_html():
    print("⏳ Gerando visualizações...")

    mapa_html    = _gerar_mapa_calor()
    linhas_tab   = _gerar_linhas_tabela()

    d_perfil    = json.dumps(_dados_perfil_vulnerabilidade(),  ensure_ascii=False)
    d_chuva     = json.dumps(_dados_chuva_alerta(),            ensure_ascii=False)
    d_cobertura = json.dumps(_dados_cobertura_auxilio(),       ensure_ascii=False)
    d_privacoes = json.dumps(_dados_privacoes(),               ensure_ascii=False)

    resumo     = contar_por_categoria()
    total      = sum(resumo.values())
    graves     = resumo.get('Grave', 0)
    pct_graves = round(graves / total * 100) if total else 0

    # Lista de bairros únicos para o <select> de filtro
    dados = carregar_familias()
    bairros_unicos = sorted(set(f['bairro'] for f in dados.values()))
    opcoes_bairro  = '\n'.join(f'<option value="{b}">{b}</option>' for b in bairros_unicos)

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard de Inteligência Alimentar — São Luís/MA</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --bg:       #0f1923;
      --surface:  #162330;
      --border:   #1e3a4a;
      --text:     #e8f4f8;
      --muted:    #8ab4c2;
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

    /* ── Header ── */
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
    .header-left p {{ font-size: 10px; color: var(--muted); margin-top: 5px; font-family: 'Space Mono', monospace; line-height: 1.5; }}
    .header-badges {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .badge {{ font-family: 'Space Mono', monospace; font-size: 10px; padding: 4px 10px; border-radius: 4px; border: 1px solid; white-space: nowrap; }}
    .badge-grave    {{ border-color: var(--grave);    color: var(--grave);    background: rgba(232,64,64,.1); }}
    .badge-moderada {{ border-color: var(--moderada); color: var(--moderada); background: rgba(245,158,11,.1); }}
    .badge-total    {{ border-color: var(--accent);   color: var(--accent);   background: rgba(56,189,248,.1); }}

    /* ── Layout ── */
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
    .card-title {{ font-family: 'Space Mono', monospace; font-size: 12px; font-weight: 700; color: var(--text); margin-bottom: 4px; line-height: 1.4; }}
    .card-sub {{ font-size: 11px; color: var(--muted); margin-bottom: 14px; line-height: 1.5; }}
    .grid-2 {{ display: grid; grid-template-columns: 1fr; gap: 20px; margin-bottom: 20px; }}

    /* Canvas Chart.js */
    .chart-container {{
      position: relative;
      width: 100%;
      height: 260px;
    }}
    .chart-container canvas {{
      width: 100% !important;
    }}

    /* ── Filtros ── */
    .filtros {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 16px;
      align-items: flex-end;
    }}
    .filtro-grupo {{
      display: flex;
      flex-direction: column;
      gap: 4px;
      flex: 1;
      min-width: 130px;
    }}
    .filtro-grupo label {{
      font-family: 'Space Mono', monospace;
      font-size: 9px;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: var(--muted);
    }}
    .filtro-grupo select {{
      background: var(--bg);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 7px 10px;
      font-family: 'DM Sans', sans-serif;
      font-size: 12px;
      cursor: pointer;
      width: 100%;
      appearance: none;
      -webkit-appearance: none;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%238ab4c2'/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 10px center;
      padding-right: 28px;
    }}
    .filtro-grupo select:focus {{ outline: none; border-color: var(--accent); }}
    .btn-limpar {{
      background: transparent;
      color: var(--muted);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 7px 14px;
      font-family: 'Space Mono', monospace;
      font-size: 10px;
      cursor: pointer;
      white-space: nowrap;
      align-self: flex-end;
    }}
    .btn-limpar:hover {{ border-color: var(--accent); color: var(--accent); }}
    .contador-resultado {{
      font-family: 'Space Mono', monospace;
      font-size: 10px;
      color: var(--muted);
      margin-bottom: 10px;
    }}
    .contador-resultado span {{ color: var(--accent); font-weight: 700; }}

    /* ── Tabela ── */
    .table-scroll {{
      width: 100%; overflow-x: auto;
      -webkit-overflow-scrolling: touch; border-radius: 6px;
    }}
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
    tbody tr:active {{ background: rgba(56,189,248,.07); }}
    tbody tr.oculto {{ display: none; }}
    tbody td {{ padding: 10px 12px; color: var(--text); vertical-align: middle; white-space: nowrap; }}
    td.rank {{ font-family: 'Space Mono', monospace; color: var(--muted); font-size: 10px; width: 32px; }}
    td.mono {{ font-family: 'Space Mono', monospace; font-size: 11px; }}
    .sem-resultado {{
      display: none;
      padding: 24px;
      text-align: center;
      color: var(--muted);
      font-family: 'Space Mono', monospace;
      font-size: 11px;
    }}

    /* ── Mapa ── */
    .mapa-wrap {{ border-radius: 8px; overflow: hidden; height: 320px; }}
    .mapa-wrap > div {{ height: 100% !important; }}

    .legend-strip {{ display: flex; gap: 14px; flex-wrap: wrap; margin-top: 12px; }}
    .legend-item {{ display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--muted); }}
    .legend-dot {{ width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }}

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
    <span class="badge badge-moderada">⚠️ Jan–Jun crítico</span>
  </div>
</header>

<main>

  <!-- Seção 1: Tabela com filtros -->
  <div class="section-label">01 — Plano de Ação Prioritário</div>
  <div class="card">
    <div class="card-title">Famílias Cadastradas</div>
    <div class="card-sub">Ordenadas por gravidade e renda via Merge Sort · use os filtros para personalizar a busca</div>

    <!-- Filtros -->
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
      Exibindo <span id="contador-num">{total}</span> famílias
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

  <!-- Seção 2: Gráficos -->
  <div class="section-label">02 — Análise Estatística</div>
  <div class="grid-2">

    <div class="card">
      <div class="card-title">Perfil de Vulnerabilidade Alimentar</div>
      <div class="card-sub">Distribuição por nível de insegurança — passe o mouse para ver detalhes</div>
      <div class="chart-container">
        <canvas id="chartPerfil"></canvas>
      </div>
    </div>

    <div class="card">
      <div class="card-title">Monitoramento Sazonal — Chuva × Alerta</div>
      <div class="card-sub">Precipitação média mensal vs famílias em alerta (limiar: 15 mm/dia)</div>
      <div class="chart-container">
        <canvas id="chartChuva"></canvas>
      </div>
    </div>

    <div class="card">
      <div class="card-title">Cobertura de Auxílio por Nível de Risco</div>
      <div class="card-sub">Quem está em situação grave mas ainda não é atendido — clique nas legendas para filtrar</div>
      <div class="chart-container">
        <canvas id="chartCobertura"></canvas>
      </div>
    </div>

    <div class="card">
      <div class="card-title">Acúmulo de Fatores de Risco por Família</div>
      <div class="card-sub">Menor de 18 · Escolaridade baixa · Doença recente · Saúde mental</div>
      <div class="chart-container">
        <canvas id="chartPrivacoes"></canvas>
      </div>
    </div>

  </div>

</main>

<footer>
  Ecossistema de Inteligência Alimentar · São Luís/MA<br>
  Dados: Portal da Transparência (NovaBF/2024)
</footer>

<script>
  // Guarda o total original para o contador
const dadosPerfil    = {d_perfil};
const dadosChuva     = {d_chuva};
const dadosCobertura = {d_cobertura};
const dadosPrivacoes = {d_privacoes};

// ── Defaults de estilo compartilhados ────────────────────────────────────────
Chart.defaults.color = '#8ab4c2';
Chart.defaults.font.family = "'DM Sans', sans-serif";
Chart.defaults.font.size   = 11;

const tooltipDefaults = {{
  backgroundColor: '#0f1923',
  borderColor: '#1e3a4a',
  borderWidth: 1,
  titleColor: '#e8f4f8',
  bodyColor: '#8ab4c2',
  padding: 10,
  cornerRadius: 6,
}};

// ── 1. Gráfico de barras horizontais — Perfil de Vulnerabilidade ──────────────
new Chart(document.getElementById('chartPerfil'), {{
  type: 'bar',
  data: {{
    labels: dadosPerfil.labels,
    datasets: [{{
      label: 'Famílias',
      data: dadosPerfil.values,
      backgroundColor: dadosPerfil.colors.map(c => c + 'cc'),
      borderColor:     dadosPerfil.colors,
      borderWidth: 1,
      borderRadius: 4,
      borderSkipped: false,
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    animation: {{ duration: 900, easing: 'easeOutQuart' }},
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        ...tooltipDefaults,
        callbacks: {{
          label: ctx => ` ${{ctx.parsed.x}} famílias`,
        }}
      }}
    }},
    scales: {{
      x: {{
        grid: {{ color: '#1e3a4a' }},
        ticks: {{ color: '#8ab4c2' }},
      }},
      y: {{
        grid: {{ display: false }},
        ticks: {{ color: '#e8f4f8', font: {{ weight: '600' }} }},
      }}
    }}
  }}
}});

// ── 2. Gráfico de linhas — Chuva × Alerta ────────────────────────────────────
new Chart(document.getElementById('chartChuva'), {{
  type: 'line',
  data: {{
    labels: dadosChuva.labels,
    datasets: [
      {{
        label: 'Precipitação média (mm)',
        data: dadosChuva.chuva,
        borderColor: '#60a5fa',
        backgroundColor: 'rgba(96,165,250,0.15)',
        fill: true,
        tension: 0.4,
        pointRadius: 5,
        pointHoverRadius: 7,
        pointBackgroundColor: '#60a5fa',
        yAxisID: 'y',
      }},
      {{
        label: 'Famílias em alerta',
        data: dadosChuva.alerta,
        borderColor: '#f87171',
        backgroundColor: 'transparent',
        borderDash: [5, 4],
        tension: 0.3,
        pointRadius: 5,
        pointHoverRadius: 7,
        pointBackgroundColor: '#f87171',
        yAxisID: 'y2',
      }}
    ]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    animation: {{ duration: 1000, easing: 'easeOutCubic' }},
    interaction: {{ mode: 'index', intersect: false }},
    plugins: {{
      legend: {{
        display: true,
        labels: {{ color: '#8ab4c2', boxWidth: 12, padding: 16 }}
      }},
      tooltip: {{
        ...tooltipDefaults,
        callbacks: {{
          label: ctx => ctx.datasetIndex === 0
            ? ` ${{ctx.parsed.y}} mm`
            : ` ${{ctx.parsed.y}} famílias`,
        }}
      }},
      annotation: undefined,
    }},
    scales: {{
      x: {{
        grid: {{ color: '#1e3a4a' }},
        ticks: {{ color: '#8ab4c2' }},
      }},
      y: {{
        grid: {{ color: '#1e3a4a' }},
        ticks: {{ color: '#60a5fa' }},
        title: {{ display: true, text: 'mm/mês', color: '#60a5fa', font: {{ size: 10 }} }},
      }},
      y2: {{
        position: 'right',
        grid: {{ display: false }},
        ticks: {{ color: '#f87171' }},
        title: {{ display: true, text: 'Famílias', color: '#f87171', font: {{ size: 10 }} }},
      }}
    }}
  }}
}});

// ── 3. Barras agrupadas — Cobertura de Auxílio ────────────────────────────────
new Chart(document.getElementById('chartCobertura'), {{
  type: 'bar',
  data: {{
    labels: dadosCobertura.labels,
    datasets: [
      {{
        label: 'Recebe auxílio',
        data: dadosCobertura.atendidos,
        backgroundColor: 'rgba(52,211,153,0.8)',
        borderColor: '#34d399',
        borderWidth: 1,
        borderRadius: 4,
      }},
      {{
        label: 'Sem auxílio',
        data: dadosCobertura.nao_atendidos,
        backgroundColor: 'rgba(232,64,64,0.75)',
        borderColor: '#e84040',
        borderWidth: 1,
        borderRadius: 4,
      }}
    ]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    animation: {{ duration: 900, easing: 'easeOutQuart' }},
    interaction: {{ mode: 'index', intersect: false }},
    plugins: {{
      legend: {{
        display: true,
        labels: {{ color: '#8ab4c2', boxWidth: 12, padding: 16 }}
      }},
      tooltip: {{
        ...tooltipDefaults,
        callbacks: {{
          label: ctx => ` ${{ctx.parsed.y}} famílias — ${{ctx.dataset.label}}`,
        }}
      }}
    }},
    scales: {{
      x: {{
        grid: {{ display: false }},
        ticks: {{ color: '#e8f4f8' }},
      }},
      y: {{
        grid: {{ color: '#1e3a4a' }},
        ticks: {{ color: '#8ab4c2' }},
      }}
    }}
  }}
}});

// ── 4. Barras — Privações Acumuladas ─────────────────────────────────────────
new Chart(document.getElementById('chartPrivacoes'), {{
  type: 'bar',
  data: {{
    labels: dadosPrivacoes.labels,
    datasets: [{{
      label: 'Famílias',
      data: dadosPrivacoes.values,
      backgroundColor: dadosPrivacoes.colors.map(c => c + 'cc'),
      borderColor:     dadosPrivacoes.colors,
      borderWidth: 1,
      borderRadius: 4,
      borderSkipped: false,
    }}]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    animation: {{
      duration: 900,
      easing: 'easeOutBounce',
      delay: ctx => ctx.dataIndex * 80,
    }},
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        ...tooltipDefaults,
        callbacks: {{
          label: ctx => ` ${{ctx.parsed.y}} famílias`,
        }}
      }}
    }},
    scales: {{
      x: {{
        grid: {{ display: false }},
        ticks: {{ color: '#e8f4f8' }},
      }},
      y: {{
        grid: {{ color: '#1e3a4a' }},
        ticks: {{ color: '#8ab4c2' }},
      }}
    }}
  }}
}});

// ── Filtros da tabela ─────────────────────────────────────────────────────────
function aplicarFiltros() {{
  const risco   = document.getElementById('filtro-risco').value;
  const auxilio = document.getElementById('filtro-auxilio').value;
  const bairro  = document.getElementById('filtro-bairro').value;
  const linhas  = document.querySelectorAll('#corpo-tabela tr');
  let visiveis  = 0;

  linhas.forEach(tr => {{
    const okRisco   = !risco   || tr.dataset.risco   === risco;
    const okAuxilio = !auxilio || tr.dataset.auxilio  === auxilio;
    const okBairro  = !bairro  || tr.dataset.bairro   === bairro;
    if (okRisco && okAuxilio && okBairro) {{
      tr.classList.remove('oculto');
      visiveis++;
    }} else {{
      tr.classList.add('oculto');
    }}
  }});

  document.getElementById('contador-num').textContent = visiveis;
  document.getElementById('sem-resultado').style.display = visiveis === 0 ? 'block' : 'none';
}}

function limparFiltros() {{
  document.getElementById('filtro-risco').value   = '';
  document.getElementById('filtro-auxilio').value = '';
  document.getElementById('filtro-bairro').value  = '';
  aplicarFiltros();
}}
</script>

</body>
</html>"""

    caminho = os.path.abspath("dashboard_slz.html")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Dashboard gerado: {caminho}")