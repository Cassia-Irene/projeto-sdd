import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches
import numpy as np
import folium
from folium.plugins import HeatMap
import io
import base64
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
    ax.set_title('Perfil de Vulnerabilidade Alimentar', fontsize=12,
                 fontweight='bold', pad=12)

    total = sum(valores)
    ax.axvline(total, color=PALETTE['muted'], linewidth=0.8,
               linestyle=':', alpha=0.5)
    ax.text(total + 0.2, -0.58, f'Total: {total}',
            color=PALETTE['muted'], fontsize=8)

    fig.tight_layout()
    return _plot_to_base64(fig)


def _grafico_chuva_alerta():
    datas, chuva_mm, alerta_familias = calcular_risco_enchente_vs_chuva()

    step = max(1, len(datas) // 90)
    datas_r  = datas[::step]
    chuva_r  = chuva_mm[::step]
    alerta_r = alerta_familias[::step]
    xs = np.arange(len(datas_r))

    fig, ax1 = plt.subplots(figsize=(8.5, 4))
    _apply_dark_style(fig, [ax1])

    ax1.fill_between(xs, chuva_r, alpha=0.20, color=PALETTE['chuva'])
    ax1.plot(xs, chuva_r, color=PALETTE['chuva'], linewidth=1.4)
    ax1.set_ylabel('Precipitação (mm)', color=PALETTE['chuva'], fontsize=9)
    ax1.tick_params(axis='y', labelcolor=PALETTE['chuva'])

    ax2 = ax1.twinx()
    ax2.set_facecolor(PALETTE['card'])
    ax2.plot(xs, alerta_r, color=PALETTE['alerta'], linewidth=1.6, linestyle='--')
    ax2.set_ylabel('Famílias em Alerta', color=PALETTE['alerta'], fontsize=9)
    ax2.tick_params(axis='y', labelcolor=PALETTE['alerta'], colors=PALETTE['muted'])
    for spine in ax2.spines.values():
        spine.set_edgecolor(PALETTE['border'])

    ax1.axhline(15, color=PALETTE['moderada'], linewidth=0.9, linestyle=':', alpha=0.7)

    tick_positions = np.linspace(0, len(datas_r) - 1, min(10, len(datas_r)), dtype=int)
    ax1.set_xticks(tick_positions)
    ax1.set_xticklabels([datas_r[i][:7] for i in tick_positions],
                        rotation=40, ha='right', fontsize=7.5)

    idx_pico = int(np.argmax(chuva_r))
    ax1.annotate(f"Pico: {chuva_r[idx_pico]:.1f}mm",
                 xy=(xs[idx_pico], chuva_r[idx_pico]),
                 xytext=(xs[idx_pico] - 4, chuva_r[idx_pico] + 8),
                 arrowprops=dict(arrowstyle='->', color=PALETTE['muted'], lw=1),
                 color=PALETTE['text'], fontsize=8)

    ax1.set_title('Monitoramento Sazonal: Chuva × Alerta de Estoque',
                  fontsize=12, fontweight='bold', pad=12)

    handles = [
        mpatches.Patch(color=PALETTE['chuva'],    label='Precipitação (mm)'),
        mpatches.Patch(color=PALETTE['alerta'],   label='Famílias em Alerta'),
        mpatches.Patch(color=PALETTE['moderada'], label='Limiar crítico 15mm'),
    ]
    ax1.legend(handles=handles, loc='upper left', fontsize=8,
               facecolor=PALETTE['bg'], edgecolor=PALETTE['border'],
               labelcolor=PALETTE['text'])

    fig.tight_layout()
    return _plot_to_base64(fig)


def _gerar_mapa_calor():
    lats, lngs, niveis = obter_dados_mapa_calor()
    mapa = folium.Map(location=[-2.5391, -44.2829], zoom_start=12,
                      tiles='CartoDB dark_matter')
    pesos = {'Grave': 1.0, 'Moderada': 0.7, 'Leve': 0.4, 'Seguro': 0.1}
    heat_data = [[lats[i], lngs[i], pesos.get(niveis[i], 0.1)]
                 for i in range(len(lats))]
    HeatMap(heat_data, radius=18, blur=14,
            gradient={0.2: '#3b82f6', 0.5: '#f59e0b', 1.0: '#ef4444'}).add_to(mapa)

    bairros_dados = carregar_bairros_coords()
    for bairro in bairros_dados:
        lat  = bairro.get('latitude') or bairro.get('lat')
        lng  = bairro.get('longitude') or bairro.get('lng') or bairro.get('lon')
        nome = bairro.get('nome')
        if lat and lng and nome:
            folium.CircleMarker(
                location=[lat, lng], radius=3,
                color='#60a5fa', fill=True, fill_opacity=0.5,
                tooltip=f"📍 {nome}"
            ).add_to(mapa)
    return mapa._repr_html_()


def _gerar_linhas_tabela():
    dados = carregar_familias()
    lista_familias = list(dados.values())
    familias_prioritarias = merge_sort_familias(lista_familias)

    cor_risco = {'Grave': '#e84040', 'Moderada': '#f59e0b',
                 'Leve': '#38bdf8',  'Seguro': '#34d399'}
    linhas = ""
    for i, f in enumerate(familias_prioritarias[:10]):
        infra   = "⚠️ Crítica" if f['sem_banheiro'] or f['sem_coleta'] else "✓ Regular"
        cor     = cor_risco.get(f['inseguranca'], '#fff')
        auxilio = "✓ Sim" if f['ja_recebe_auxilio'] else "✗ Não"
        linhas += f"""
        <tr>
            <td class="rank">#{i+1}</td>
            <td>{f['bairro']}</td>
            <td style="color:{cor}; font-weight:700;">{f['inseguranca']}</td>
            <td class="mono">R$ {f['renda_sm']:.2f} SM</td>
            <td>{infra}</td>
            <td>{auxilio}</td>
        </tr>"""
    return linhas


def gerar_dashboard_html():
    print("⏳ Gerando visualizações...")

    perfil_b64 = _grafico_perfil_vulnerabilidade()
    linhas_b64 = _grafico_chuva_alerta()
    mapa_html  = _gerar_mapa_calor()
    linhas_tab = _gerar_linhas_tabela()

    resumo     = contar_por_categoria()
    total      = sum(resumo.values())
    graves     = resumo.get('Grave', 0)
    pct_graves = round(graves / total * 100) if total else 0

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
    body {{ background: var(--bg); color: var(--text); font-family: 'DM Sans', sans-serif; min-height: 100vh; }}
    header {{
      background: linear-gradient(135deg, #0d2235 0%, #0f2d40 60%, #0a1e2c 100%);
      border-bottom: 2px solid var(--border);
      padding: 28px 40px 24px;
      display: flex; align-items: flex-end; justify-content: space-between;
      gap: 20px; flex-wrap: wrap;
    }}
    .header-left h1 {{
      font-family: 'Space Mono', monospace;
      font-size: clamp(16px, 2.2vw, 24px);
      font-weight: 700; color: var(--text); line-height: 1.2;
    }}
    .header-left h1 span {{ color: var(--accent); }}
    .header-left p {{ font-size: 11px; color: var(--muted); margin-top: 6px; font-family: 'Space Mono', monospace; }}
    .header-badges {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    .badge {{ font-family: 'Space Mono', monospace; font-size: 11px; padding: 5px 12px; border-radius: 4px; border: 1px solid; white-space: nowrap; }}
    .badge-grave    {{ border-color: var(--grave);    color: var(--grave);    background: rgba(232,64,64,.1); }}
    .badge-moderada {{ border-color: var(--moderada); color: var(--moderada); background: rgba(245,158,11,.1); }}
    .badge-total    {{ border-color: var(--accent);   color: var(--accent);   background: rgba(56,189,248,.1); }}
    main {{ padding: 32px 40px; max-width: 1400px; margin: 0 auto; }}
    .section-label {{
      font-family: 'Space Mono', monospace; font-size: 10px; text-transform: uppercase;
      letter-spacing: 2px; color: var(--muted); margin-bottom: 14px;
      display: flex; align-items: center; gap: 10px;
    }}
    .section-label::after {{ content: ''; flex: 1; height: 1px; background: var(--border); }}
    .card {{
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 10px; padding: 24px; margin-bottom: 28px;
    }}
    .card-title {{ font-family: 'Space Mono', monospace; font-size: 13px; font-weight: 700; color: var(--text); margin-bottom: 4px; }}
    .card-sub {{ font-size: 12px; color: var(--muted); margin-bottom: 18px; }}
    .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 28px; }}
    @media (max-width: 900px) {{ .grid-2 {{ grid-template-columns: 1fr; }} header {{ flex-direction: column; align-items: flex-start; }} main {{ padding: 20px; }} }}
    .chart-img {{ width: 100%; height: auto; border-radius: 6px; display: block; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    thead th {{
      font-family: 'Space Mono', monospace; font-size: 10px; text-transform: uppercase;
      letter-spacing: 1px; color: var(--muted); padding: 10px 14px;
      text-align: left; border-bottom: 1px solid var(--border); background: rgba(255,255,255,.02);
    }}
    tbody tr {{ border-bottom: 1px solid var(--border); transition: background .15s; }}
    tbody tr:hover {{ background: rgba(56,189,248,.05); }}
    tbody td {{ padding: 11px 14px; color: var(--text); vertical-align: middle; }}
    td.rank {{ font-family: 'Space Mono', monospace; color: var(--muted); font-size: 11px; width: 36px; }}
    td.mono {{ font-family: 'Space Mono', monospace; font-size: 12px; }}
    .mapa-wrap {{ border-radius: 8px; overflow: hidden; height: 480px; }}
    .mapa-wrap > div {{ height: 100% !important; }}
    .legend-strip {{ display: flex; gap: 18px; flex-wrap: wrap; margin-top: 12px; }}
    .legend-item {{ display: flex; align-items: center; gap: 7px; font-size: 12px; color: var(--muted); }}
    .legend-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
    footer {{ text-align: center; padding: 20px; font-family: 'Space Mono', monospace; font-size: 10px; color: var(--muted); border-top: 1px solid var(--border); margin-top: 8px; }}
  </style>
</head>
<body>
<header>
  <div class="header-left">
    <h1>🥗 Inteligência Alimentar<span> // SLZ</span></h1>
    <p>Ecossistema de monitoramento de vulnerabilidade · São Luís, Maranhão</p>
  </div>
  <div class="header-badges">
    <span class="badge badge-total">👥 {total} famílias monitoradas</span>
    <span class="badge badge-grave">🔴 {graves} em situação grave ({pct_graves}%)</span>
    <span class="badge badge-moderada">⚠️ Período crítico: Jan–Jun</span>
  </div>
</header>
<main>
  <div class="section-label">01 — Plano de Ação Prioritário</div>
  <div class="card">
    <div class="card-title">Top 10 Famílias para Intervenção Imediata</div>
    <div class="card-sub">Ordenadas por gravidade e renda via Merge Sort — otimização de alocação de recursos</div>
    <table>
      <thead>
        <tr><th>#</th><th>Bairro / Ocupação</th><th>Nível de Risco</th><th>Renda Per Capita</th><th>Infraestrutura</th><th>Recebe Auxílio</th></tr>
      </thead>
      <tbody>{linhas_tab}</tbody>
    </table>
  </div>
  <div class="section-label">02 — Análise Estatística</div>
  <div class="grid-2">
    <div class="card">
      <div class="card-title">Perfil de Vulnerabilidade Alimentar</div>
      <div class="card-sub">Distribuição das famílias por nível de insegurança</div>
      <img class="chart-img" src="data:image/png;base64,{perfil_b64}" alt="Perfil de Vulnerabilidade">
      <div class="legend-strip">
        <div class="legend-item"><div class="legend-dot" style="background:var(--grave)"></div>Grave</div>
        <div class="legend-item"><div class="legend-dot" style="background:var(--moderada)"></div>Moderada</div>
        <div class="legend-item"><div class="legend-dot" style="background:var(--leve)"></div>Leve</div>
        <div class="legend-item"><div class="legend-dot" style="background:var(--seguro)"></div>Seguro</div>
      </div>
    </div>
    <div class="card">
      <div class="card-title">Monitoramento Sazonal — Chuva × Alerta de Estoque</div>
      <div class="card-sub">Correlação entre precipitação e ativação do protocolo emergencial (limiar: 15mm/dia)</div>
      <img class="chart-img" src="data:image/png;base64,{linhas_b64}" alt="Chuva vs Alerta">
    </div>
  </div>
  <div class="section-label">03 — Mapa de Calor de Vulnerabilidade</div>
  <div class="card">
    <div class="card-title">Distribuição Espacial do Risco Alimentar — São Luís/MA</div>
    <div class="card-sub">Intensidade baseada em nível de insegurança · azul → amarelo → vermelho = leve → moderado → grave</div>
    <div class="mapa-wrap">{mapa_html}</div>
  </div>
</main>
<footer>Ecossistema de Inteligência Alimentar · São Luís/MA · Dados: Portal da Transparência (NovaBF/2024) + sintéticos via Faker</footer>
</body>
</html>"""

    caminho = os.path.abspath("dashboard_slz.html")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Dashboard gerado: {caminho}")