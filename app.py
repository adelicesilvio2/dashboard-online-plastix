from flask import Flask, request, jsonify
from datetime import datetime
from collections import deque

app = Flask(__name__)

# ==============================
# CONFIGURAÇÕES
# ==============================

API_KEY = "plastix123"

MAQUINAS_CONFIG = {
    "MA1": {"nome": "MA1", "tipo": "Automática"},
    "MA2": {"nome": "MA2", "tipo": "Automática"},
    "MA3": {"nome": "MA3", "tipo": "Automática"},
    "M1": {"nome": "M1", "tipo": "Semiautomática"},
    "M2": {"nome": "M2", "tipo": "Semiautomática"},
    "M3": {"nome": "M3", "tipo": "Semiautomática"},
    "M4": {"nome": "M4", "tipo": "Semiautomática"},
    "M5": {"nome": "M5", "tipo": "Semiautomática"},
}

HORAS_TREND = list(range(5, 24))  # 05:00 até 23:00

maquinas = {}
eventos = deque(maxlen=100)

for codigo, cfg in MAQUINAS_CONFIG.items():
    maquinas[codigo] = {
        "codigo": codigo,
        "nome": cfg["nome"],
        "tipo": cfg["tipo"],
        "op": "-",
        "produto": "-",
        "equipe": "-",
        "meta": 0,
        "total": 0,
        "velocidade": 0,
        "status": "SEM DADOS",
        "ultima": "-",
        "historico_hora": {h: 0 for h in HORAS_TREND},
        "historico_acumulado": {h: 0 for h in HORAS_TREND},
    }


# ==============================
# ROTAS
# ==============================

@app.route("/")
def index():
    return HTML


@app.route("/api/status")
def api_status():
    produzindo = 0
    paradas = 0
    velocidade_total = 0

    for m in maquinas.values():
        status = str(m["status"]).upper()

        if "PRODUZINDO" in status:
            produzindo += 1

        if "PARADA" in status:
            paradas += 1

        velocidade_total += float(m["velocidade"] or 0)

    trend = gerar_trend()

    return jsonify({
        "maquinas": maquinas,
        "eventos": list(eventos),
        "resumo": {
            "produzindo": produzindo,
            "paradas": paradas,
            "velocidade_total": velocidade_total,
            "total_maquinas": len(maquinas),
        },
        "trend": trend,
        "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })


@app.route("/api/receber", methods=["POST"])
def receber():
    dados = request.get_json(force=True)

    if dados.get("api_key") != API_KEY:
        return jsonify({"ok": False, "erro": "API_KEY inválida"}), 403

    codigo = str(dados.get("maquina", "")).upper().strip()

    if codigo not in maquinas:
        return jsonify({"ok": False, "erro": f"Máquina inválida: {codigo}"}), 400

    m = maquinas[codigo]

    m["op"] = str(dados.get("op", m["op"]))
    m["produto"] = str(dados.get("produto", m["produto"]))
    m["equipe"] = str(dados.get("equipe", m["equipe"]))
    m["meta"] = int_safe(dados.get("meta", m["meta"]))
    m["total"] = int_safe(dados.get("total", m["total"]))
    m["velocidade"] = float_safe(dados.get("velocidade", m["velocidade"]))
    m["status"] = str(dados.get("status", m["status"]))
    m["ultima"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    hora_atual = datetime.now().hour

    if hora_atual in HORAS_TREND:
        producao_hora = int_safe(dados.get("producao_hora", 0))

        # Se o coletor local não mandar producao_hora, usamos velocidade aproximada como referência visual.
        if producao_hora <= 0:
            producao_hora = int(m["velocidade"])

        m["historico_hora"][hora_atual] = producao_hora

        acumulado = 0
        for h in HORAS_TREND:
            acumulado += int_safe(m["historico_hora"].get(h, 0))
            m["historico_acumulado"][h] = acumulado

    eventos.appendleft({
        "data_hora": m["ultima"],
        "maquina": codigo,
        "tipo": "ATUALIZAÇÃO",
        "descricao": f"{codigo} | OP {m['op']} | {m['total']} de {m['meta']} | {m['status']}"
    })

    return jsonify({"ok": True, "maquina": codigo})


@app.route("/api/teste")
def api_teste():
    """
    Rota para simular dados sem coletor local.
    Abra no navegador:
    /api/teste
    """
    exemplos = [
        ("MA1", "4587", "FR500ML", "A", 10000, 2466, 1175, "PRODUZINDO"),
        ("MA2", "4588", "FR2L", "A", 8000, 1200, 980, "PRODUZINDO"),
        ("MA3", "4589", "FR1L", "B", 12000, 5000, 1400, "PRODUZINDO"),
        ("M1", "4590", "TAMPA38", "B", 5000, 850, 350, "ATENÇÃO"),
        ("M2", "4591", "FR250ML", "C", 6000, 0, 0, "PARADA"),
        ("M3", "4592", "FR750ML", "A", 7000, 2300, 500, "PRODUZINDO"),
        ("M4", "4593", "FR300ML", "C", 4000, 900, 220, "PRODUZINDO"),
        ("M5", "4594", "FR100ML", "B", 3000, 300, 150, "PRODUZINDO"),
    ]

    for codigo, op, produto, equipe, meta, total, velocidade, status in exemplos:
        m = maquinas[codigo]
        m["op"] = op
        m["produto"] = produto
        m["equipe"] = equipe
        m["meta"] = meta
        m["total"] = total
        m["velocidade"] = velocidade
        m["status"] = status
        m["ultima"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        for h in HORAS_TREND:
            if 5 <= h <= datetime.now().hour:
                valor = int(velocidade * 0.75)
            else:
                valor = 0

            m["historico_hora"][h] = valor

        acumulado = 0
        for h in HORAS_TREND:
            acumulado += int_safe(m["historico_hora"].get(h, 0))
            m["historico_acumulado"][h] = acumulado

    eventos.appendleft({
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "maquina": "-",
        "tipo": "TESTE",
        "descricao": "Dados simulados carregados"
    })

    return jsonify({"ok": True, "mensagem": "Dados simulados carregados"})


# ==============================
# FUNÇÕES AUXILIARES
# ==============================

def int_safe(valor, padrao=0):
    try:
        if valor is None or valor == "":
            return padrao
        return int(float(str(valor).replace(",", ".")))
    except Exception:
        return padrao


def float_safe(valor, padrao=0):
    try:
        if valor is None or valor == "":
            return padrao
        return float(str(valor).replace(",", "."))
    except Exception:
        return padrao


def gerar_trend():
    labels = [f"{h:02d}:00" for h in HORAS_TREND]
    producao_hora = {}
    acumulado_dia = {}

    for codigo, m in maquinas.items():
        producao_hora[codigo] = [int_safe(m["historico_hora"].get(h, 0)) for h in HORAS_TREND]
        acumulado_dia[codigo] = [int_safe(m["historico_acumulado"].get(h, 0)) for h in HORAS_TREND]

    return {
        "labels": labels,
        "producao_hora": producao_hora,
        "acumulado_dia": acumulado_dia,
        "periodo": "05:00 às 23:00"
    }


# ==============================
# HTML
# ==============================

HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Dashboard Online PLASTIX</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
:root {
    --bg: #0f172a;
    --panel: #111827;
    --panel2: #1f2937;
    --text: #e5e7eb;
    --muted: #9ca3af;
    --green: #22c55e;
    --yellow: #eab308;
    --red: #ef4444;
    --blue: #38bdf8;
    --purple: #a78bfa;
    --border: rgba(255,255,255,0.10);
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: radial-gradient(circle at top left, #1e3a8a 0, #0f172a 35%, #020617 100%);
    color: var(--text);
}

header {
    padding: 18px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--border);
    background: rgba(2, 6, 23, 0.72);
    position: sticky;
    top: 0;
    z-index: 10;
    backdrop-filter: blur(8px);
}

.title h1 {
    margin: 0;
    font-size: 24px;
    letter-spacing: 0.5px;
}

.title span {
    color: var(--muted);
    font-size: 13px;
}

.online-pill {
    padding: 10px 14px;
    border-radius: 999px;
    font-weight: bold;
    font-size: 14px;
    background: rgba(34,197,94,0.15);
    color: #86efac;
    border: 1px solid rgba(34,197,94,0.45);
}

main {
    padding: 18px 24px 32px;
}

.summary {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 18px;
}

.metric {
    background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

.metric .label {
    color: var(--muted);
    font-size: 13px;
}

.metric .value {
    font-size: 28px;
    font-weight: bold;
    margin-top: 8px;
}

.metric .unit {
    color: var(--muted);
    font-size: 12px;
    margin-left: 4px;
}

.cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 18px;
}

.machine-card {
    background: rgba(17, 24, 39, 0.92);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 16px;
    box-shadow: 0 16px 35px rgba(0,0,0,0.30);
    overflow: hidden;
    position: relative;
}

.machine-card:before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 5px;
    background: #64748b;
}

.machine-card.produzindo:before {
    background: var(--green);
}

.machine-card.atencao:before {
    background: var(--yellow);
}

.machine-card.parada:before {
    background: var(--red);
}

.machine-card.offline:before {
    background: #64748b;
}

.machine-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.machine-head h2 {
    margin: 0;
    font-size: 26px;
}

.badge {
    padding: 7px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: bold;
    background: #334155;
}

.badge.produzindo {
    background: rgba(34,197,94,0.16);
    color: #86efac;
}

.badge.atencao {
    background: rgba(234,179,8,0.16);
    color: #fde68a;
}

.badge.parada {
    background: rgba(239,68,68,0.16);
    color: #fca5a5;
}

.badge.offline {
    background: rgba(148,163,184,0.16);
    color: #cbd5e1;
}

.grid-info {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 12px;
}

.info-box {
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 10px;
}

.info-box label {
    color: var(--muted);
    font-size: 12px;
    display: block;
    margin-bottom: 4px;
}

.info-box strong {
    font-size: 18px;
    word-break: break-word;
}

.big-number {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.big-number .box {
    background: linear-gradient(180deg, rgba(56,189,248,0.12), rgba(255,255,255,0.04));
    border: 1px solid rgba(56,189,248,0.20);
    border-radius: 16px;
    padding: 12px;
}

.big-number span {
    color: var(--muted);
    font-size: 12px;
}

.big-number b {
    display: block;
    font-size: 20px;
    margin-top: 4px;
}

.progress {
    margin-top: 8px;
    height: 8px;
    background: rgba(255,255,255,0.10);
    border-radius: 999px;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    background: #38bdf8;
}

.percent {
    color: #9ca3af;
    display: block;
    margin-top: 5px;
    font-size: 12px;
}

.last-line {
    color: var(--muted);
    font-size: 12px;
    margin-top: 12px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.charts {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 18px;
}

.machine-charts {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    margin-bottom: 18px;
}

.chart-panel,
.machine-chart-panel,
.events-panel {
    background: rgba(17, 24, 39, 0.92);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 16px;
    box-shadow: 0 16px 35px rgba(0,0,0,0.30);
}

.chart-panel h3,
.machine-chart-panel h3,
.events-panel h3 {
    margin: 0 0 12px;
    font-size: 18px;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}

th,
td {
    border-bottom: 1px solid var(--border);
    padding: 9px 7px;
    text-align: left;
}

th {
    color: var(--muted);
    font-weight: normal;
}

.actions {
    display: flex;
    gap: 10px;
    margin-top: 12px;
}

.actions a {
    color: white;
    text-decoration: none;
    padding: 10px 12px;
    background: #334155;
    border: 1px solid var(--border);
    border-radius: 12px;
    font-weight: bold;
    font-size: 13px;
}

@media (max-width: 1200px) {
    .summary {
        grid-template-columns: repeat(2, 1fr);
    }

    .cards {
        grid-template-columns: repeat(2, 1fr);
    }

    .charts {
        grid-template-columns: 1fr;
    }

    .machine-charts {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 700px) {
    .summary,
    .cards,
    .charts,
    .machine-charts {
        grid-template-columns: 1fr;
    }

    header {
        display: block;
    }

    .online-pill {
        display: inline-block;
        margin-top: 12px;
    }
}
</style>
</head>

<body>
<header>
    <div class="title">
        <h1>Produção Sopradoras - PLASTIX</h1>
        <span id="subtitulo">Dashboard online aguardando dados...</span>
    </div>

    <div class="online-pill">ONLINE</div>
</header>

<main>
    <section class="summary">
        <div class="metric">
            <div class="label">Velocidade total atual</div>
            <div class="value" id="velTotal">0<span class="unit">un/h</span></div>
        </div>

        <div class="metric">
            <div class="label">Máquinas produzindo</div>
            <div class="value" id="maqProd">0<span class="unit">máq.</span></div>
        </div>

        <div class="metric">
            <div class="label">Máquinas paradas</div>
            <div class="value" id="maqParada">0<span class="unit">máq.</span></div>
        </div>

        <div class="metric">
            <div class="label">Última atualização</div>
            <div class="value" id="ultimaColeta" style="font-size:18px;">-</div>
        </div>
    </section>

    <section class="cards" id="cards"></section>

    <section class="charts">
        <div class="chart-panel">
            <h3>Trend geral de produção por hora - 05:00 às 23:00</h3>
            <canvas id="chartVelocidade"></canvas>
        </div>

        <div class="chart-panel">
            <h3>Trend geral acumulado do dia - 05:00 às 23:00</h3>
            <canvas id="chartAcumulado"></canvas>
        </div>
    </section>

    <section class="machine-charts" id="machineCharts"></section>

    <section class="events-panel">
        <h3>Últimos eventos</h3>

        <table>
            <thead>
                <tr>
                    <th>Hora</th>
                    <th>Máq.</th>
                    <th>Tipo</th>
                    <th>Descrição</th>
                </tr>
            </thead>

            <tbody id="eventosBody"></tbody>
        </table>

        <div class="actions">
            <a href="/api/teste">Carregar dados simulados</a>
        </div>
    </section>
</main>

<script>
let chartVelocidade;
let chartAcumulado;
let chartsPorMaquina = {};

const cores = {
    'MA1': '#38bdf8',
    'MA2': '#a78bfa',
    'MA3': '#22c55e',
    'M1': '#f97316',
    'M2': '#eab308',
    'M3': '#ef4444',
    'M4': '#14b8a6',
    'M5': '#f472b6'
};

function fmt(n) {
    return Number(n || 0).toLocaleString('pt-BR', {maximumFractionDigits: 0});
}

function classeStatus(status) {
    const s = String(status || '').toUpperCase();

    if (s.includes('PRODUZINDO')) return 'produzindo';
    if (s.includes('ATEN')) return 'atencao';
    if (s.includes('PARADA')) return 'parada';

    return 'offline';
}

function criarCards(maquinas) {
    const cards = document.getElementById('cards');
    cards.innerHTML = '';

    Object.values(maquinas).forEach(m => {
        const cls = classeStatus(m.status);
        const meta = Number(m.meta || 0);
        const total = Number(m.total || 0);
        const perc = meta > 0 ? (total / meta) * 100 : 0;

        const div = document.createElement('div');
        div.className = `machine-card ${cls}`;

        div.innerHTML = `
            <div class="machine-head">
                <h2>${m.nome}</h2>
                <div class="badge ${cls}">${m.status}</div>
            </div>

            <div class="grid-info">
                <div class="info-box">
                    <label>OP</label>
                    <strong>${m.op || '-'}</strong>
                </div>

                <div class="info-box">
                    <label>Produto</label>
                    <strong>${m.produto || '-'}</strong>
                </div>

                <div class="info-box">
                    <label>Equipe</label>
                    <strong>${m.equipe || '-'}</strong>
                </div>

                <div class="info-box">
                    <label>Quantidade OP</label>
                    <strong>${meta > 0 ? fmt(meta) : '-'}</strong>
                </div>
            </div>

            <div class="big-number">
                <div class="box">
                    <span>Produzidos</span>
                    <b>${fmt(total)} de ${meta > 0 ? fmt(meta) : '-'}</b>

                    <div class="progress">
                        <div class="progress-bar" style="width:${Math.min(perc, 100)}%;"></div>
                    </div>

                    <small class="percent">${meta > 0 ? perc.toFixed(1) + '%' : 'Sem quantidade informada'}</small>
                </div>

                <div class="box">
                    <span>Velocidade</span>
                    <b>${fmt(m.velocidade)} /h</b>
                </div>
            </div>

            <div class="last-line">
                Tipo: ${m.tipo} | Última leitura: ${m.ultima}
            </div>
        `;

        cards.appendChild(div);
    });
}

function criarOuAtualizarGraficos(data) {
    const trend = data.trend || {};
    const labels = trend.labels || [];
    const producaoHora = trend.producao_hora || {};
    const acumuladoDia = trend.acumulado_dia || {};
    const nomes = Object.keys(producaoHora);

    const datasetsVel = nomes.map(nome => ({
        label: nome,
        data: producaoHora[nome] || [],
        borderColor: cores[nome] || '#fff',
        backgroundColor: cores[nome] || '#fff',
        tension: 0.25
    }));

    const datasetsAcum = nomes.map(nome => ({
        label: nome,
        data: acumuladoDia[nome] || [],
        borderColor: cores[nome] || '#fff',
        backgroundColor: cores[nome] || '#fff',
        tension: 0.25
    }));

    const opcoes = {
        responsive: true,
        plugins: {
            legend: {
                labels: {
                    color: '#e5e7eb'
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    color: '#9ca3af'
                },
                grid: {
                    color: 'rgba(255,255,255,0.08)'
                }
            },
            y: {
                ticks: {
                    color: '#9ca3af'
                },
                grid: {
                    color: 'rgba(255,255,255,0.08)'
                }
            }
        }
    };

    if (!chartVelocidade) {
        chartVelocidade = new Chart(document.getElementById('chartVelocidade'), {
            type: 'line',
            data: {
                labels,
                datasets: datasetsVel
            },
            options: opcoes
        });
    } else {
        chartVelocidade.data.labels = labels;
        chartVelocidade.data.datasets = datasetsVel;
        chartVelocidade.update();
    }

    if (!chartAcumulado) {
        chartAcumulado = new Chart(document.getElementById('chartAcumulado'), {
            type: 'line',
            data: {
                labels,
                datasets: datasetsAcum
            },
            options: opcoes
        });
    } else {
        chartAcumulado.data.labels = labels;
        chartAcumulado.data.datasets = datasetsAcum;
        chartAcumulado.update();
    }
}

function criarGraficosIndividuais(data) {
    const trend = data.trend || {};
    const labels = trend.labels || [];
    const producaoHora = trend.producao_hora || {};
    const acumuladoDia = trend.acumulado_dia || {};
    const container = document.getElementById('machineCharts');
    const nomes = Object.keys(producaoHora);

    nomes.forEach(nome => {
        const canvasId = `chart_${nome}`;

        if (!document.getElementById(canvasId)) {
            const panel = document.createElement('div');
            panel.className = 'machine-chart-panel';

            panel.innerHTML = `
                <h3>${nome} - produção horária e acumulado</h3>
                <canvas id="${canvasId}"></canvas>
            `;

            container.appendChild(panel);
        }

        const datasets = [
            {
                label: 'Produção por hora',
                data: producaoHora[nome] || [],
                borderColor: cores[nome] || '#38bdf8',
                backgroundColor: cores[nome] || '#38bdf8',
                tension: 0.25,
                yAxisID: 'y'
            },
            {
                label: 'Acumulado do dia',
                data: acumuladoDia[nome] || [],
                borderColor: '#e5e7eb',
                backgroundColor: '#e5e7eb',
                tension: 0.25,
                yAxisID: 'y1'
            }
        ];

        const opcoes = {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#e5e7eb'
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#9ca3af'
                    },
                    grid: {
                        color: 'rgba(255,255,255,0.08)'
                    }
                },
                y: {
                    type: 'linear',
                    position: 'left',
                    ticks: {
                        color: '#9ca3af'
                    },
                    grid: {
                        color: 'rgba(255,255,255,0.08)'
                    },
                    title: {
                        display: true,
                        text: 'Un/hora',
                        color: '#9ca3af'
                    }
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    ticks: {
                        color: '#9ca3af'
                    },
                    grid: {
                        drawOnChartArea: false
                    },
                    title: {
                        display: true,
                        text: 'Acumulado',
                        color: '#9ca3af'
                    }
                }
            }
        };

        if (!chartsPorMaquina[nome]) {
            chartsPorMaquina[nome] = new Chart(document.getElementById(canvasId), {
                type: 'line',
                data: {
                    labels,
                    datasets
                },
                options: opcoes
            });
        } else {
            chartsPorMaquina[nome].data.labels = labels;
            chartsPorMaquina[nome].data.datasets = datasets;
            chartsPorMaquina[nome].update();
        }
    });
}

function atualizarEventos(eventos) {
    const body = document.getElementById('eventosBody');
    body.innerHTML = '';

    (eventos || []).slice(0, 20).forEach(e => {
        const tr = document.createElement('tr');

        tr.innerHTML = `
            <td>${e.data_hora}</td>
            <td>${e.maquina || '-'}</td>
            <td>${e.tipo || '-'}</td>
            <td>${e.descricao}</td>
        `;

        body.appendChild(tr);
    });
}

async function carregar() {
    try {
        const r = await fetch('/api/status');
        const data = await r.json();

        document.getElementById('subtitulo').innerText =
            `Dashboard online | Última atualização: ${data.ultima_atualizacao}`;

        document.getElementById('velTotal').innerHTML =
            `${fmt(data.resumo.velocidade_total)}<span class="unit">un/h</span>`;

        document.getElementById('maqProd').innerHTML =
            `${fmt(data.resumo.produzindo)}<span class="unit">máq.</span>`;

        document.getElementById('maqParada').innerHTML =
            `${fmt(data.resumo.paradas)}<span class="unit">máq.</span>`;

        document.getElementById('ultimaColeta').innerText =
            data.ultima_atualizacao || '-';

        criarCards(data.maquinas);
        criarOuAtualizarGraficos(data);
        criarGraficosIndividuais(data);
        atualizarEventos(data.eventos);

    } catch (e) {
        console.error(e);
    }
}

carregar();
setInterval(carregar, 3000);
</script>

</body>
</html>
"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
