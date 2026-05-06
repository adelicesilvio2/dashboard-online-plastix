from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

API_KEY = "plastix123"

maquinas = {
    "MA1": {"nome": "MA1", "tipo": "Automática", "op": "-", "produto": "-", "equipe": "-", "meta": 0, "total": 0, "velocidade": 0, "status": "SEM DADOS", "ultima": "-"},
    "MA2": {"nome": "MA2", "tipo": "Automática", "op": "-", "produto": "-", "equipe": "-", "meta": 0, "total": 0, "velocidade": 0, "status": "SEM DADOS", "ultima": "-"},
    "MA3": {"nome": "MA3", "tipo": "Automática", "op": "-", "produto": "-", "equipe": "-", "meta": 0, "total": 0, "velocidade": 0, "status": "SEM DADOS", "ultima": "-"},
    "M1": {"nome": "M1", "tipo": "Semiautomática", "op": "-", "produto": "-", "equipe": "-", "meta": 0, "total": 0, "velocidade": 0, "status": "SEM DADOS", "ultima": "-"},
    "M2": {"nome": "M2", "tipo": "Semiautomática", "op": "-", "produto": "-", "equipe": "-", "meta": 0, "total": 0, "velocidade": 0, "status": "SEM DADOS", "ultima": "-"},
    "M3": {"nome": "M3", "tipo": "Semiautomática", "op": "-", "produto": "-", "equipe": "-", "meta": 0, "total": 0, "velocidade": 0, "status": "SEM DADOS", "ultima": "-"},
    "M4": {"nome": "M4", "tipo": "Semiautomática", "op": "-", "produto": "-", "equipe": "-", "meta": 0, "total": 0, "velocidade": 0, "status": "SEM DADOS", "ultima": "-"},
    "M5": {"nome": "M5", "tipo": "Semiautomática", "op": "-", "produto": "-", "equipe": "-", "meta": 0, "total": 0, "velocidade": 0, "status": "SEM DADOS", "ultima": "-"},
}

eventos = []


@app.route("/")
def index():
    return HTML


@app.route("/api/status")
def api_status():
    produzindo = sum(1 for m in maquinas.values() if "PRODUZINDO" in m["status"].upper())
    paradas = sum(1 for m in maquinas.values() if "PARADA" in m["status"].upper())
    velocidade_total = sum(float(m["velocidade"] or 0) for m in maquinas.values())

    return jsonify({
        "maquinas": maquinas,
        "eventos": eventos[-40:][::-1],
        "resumo": {
            "produzindo": produzindo,
            "paradas": paradas,
            "velocidade_total": velocidade_total,
        },
        "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })


@app.route("/api/receber", methods=["POST"])
def receber():
    dados = request.get_json(force=True)

    if dados.get("api_key") != API_KEY:
        return jsonify({"ok": False, "erro": "API_KEY inválida"}), 403

    nome = str(dados.get("maquina", "")).upper().strip()

    if nome not in maquinas:
        return jsonify({"ok": False, "erro": "Máquina inválida"}), 400

    m = maquinas[nome]

    m["op"] = str(dados.get("op", m["op"]))
    m["produto"] = str(dados.get("produto", m["produto"]))
    m["equipe"] = str(dados.get("equipe", m["equipe"]))
    m["meta"] = int(float(dados.get("meta", m["meta"] or 0)))
    m["total"] = int(float(dados.get("total", m["total"] or 0)))
    m["velocidade"] = float(dados.get("velocidade", m["velocidade"] or 0))
    m["status"] = str(dados.get("status", m["status"]))
    m["ultima"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    eventos.append({
        "data_hora": m["ultima"],
        "maquina": nome,
        "descricao": f"{nome} | OP {m['op']} | {m['total']} de {m['meta']}"
    })

    return jsonify({"ok": True, "maquina": nome})


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
    border-bottom: 1px solid var(--border);
    background: rgba(2,6,23,0.78);
    position: sticky;
    top: 0;
    z-index: 10;
    backdrop-filter: blur(8px);
}

header h1 {
    margin: 0;
    font-size: 26px;
}

header span {
    display: block;
    margin-top: 5px;
    color: var(--muted);
    font-size: 13px;
}

main {
    padding: 20px;
}

.summary {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 20px;
}

.metric {
    background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

.metric small {
    color: var(--muted);
}

.metric b {
    display: block;
    font-size: 30px;
    margin-top: 8px;
}

.cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
}

.card {
    background: rgba(17,24,39,0.94);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 16px;
    box-shadow: 0 16px 35px rgba(0,0,0,0.30);
    position: relative;
    overflow: hidden;
}

.card:before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 6px;
    background: #64748b;
}

.card.produzindo:before {
    background: var(--green);
}

.card.parada:before {
    background: var(--red);
}

.card.atencao:before {
    background: var(--yellow);
}

.card-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.card h2 {
    margin: 0;
    font-size: 28px;
}

.badge {
    padding: 8px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: bold;
    background: #334155;
}

.badge.produzindo {
    color: #86efac;
    background: rgba(34,197,94,0.16);
}

.badge.parada {
    color: #fca5a5;
    background: rgba(239,68,68,0.16);
}

.badge.atencao {
    color: #fde68a;
    background: rgba(234,179,8,0.16);
}

.badge.sem {
    color: #cbd5e1;
    background: rgba(148,163,184,0.16);
}

.info {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 16px;
}

.box {
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 12px;
}

.box small {
    color: var(--muted);
    display: block;
    margin-bottom: 5px;
}

.box b {
    font-size: 18px;
    word-break: break-word;
}

.big {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 14px;
}

.big .box {
    background: linear-gradient(180deg, rgba(56,189,248,0.13), rgba(255,255,255,0.04));
    border: 1px solid rgba(56,189,248,0.20);
}

.big b {
    display: block;
    font-size: 24px;
}

.progress {
    height: 9px;
    background: rgba(255,255,255,0.12);
    border-radius: 999px;
    overflow: hidden;
    margin-top: 10px;
}

.bar {
    height: 100%;
    background: var(--blue);
}

.last {
    color: var(--muted);
    font-size: 12px;
    margin-top: 12px;
}

.charts {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-top: 22px;
}

.panel {
    background: rgba(17,24,39,0.94);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 16px;
    box-shadow: 0 16px 35px rgba(0,0,0,0.30);
}

.panel h3 {
    margin: 0 0 14px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 22px;
    background: rgba(17,24,39,0.94);
    border-radius: 18px;
    overflow: hidden;
}

td, th {
    padding: 11px;
    border-bottom: 1px solid var(--border);
}

th {
    color: var(--muted);
    text-align: left;
}

@media(max-width: 1200px) {
    .cards {
        grid-template-columns: repeat(2, 1fr);
    }
    .summary {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media(max-width: 700px) {
    .cards, .summary, .charts {
        grid-template-columns: 1fr;
    }
}
</style>
</head>

<body>
<header>
    <h1>Produção Sopradoras - PLASTIX</h1>
    <span id="ultima">Dashboard online aguardando dados...</span>
</header>

<main>
    <section class="summary">
        <div class="metric">
            <small>Velocidade total</small>
            <b id="velTotal">0 un/h</b>
        </div>
        <div class="metric">
            <small>Produzindo</small>
            <b id="produzindo">0 máq.</b>
        </div>
        <div class="metric">
            <small>Paradas</small>
            <b id="paradas">0 máq.</b>
        </div>
        <div class="metric">
            <small>Última atualização</small>
            <b id="horaAtual" style="font-size:18px;">-</b>
        </div>
    </section>

    <section class="cards" id="cards"></section>

    <section class="charts">
        <div class="panel">
            <h3>Produção por máquina</h3>
            <canvas id="graficoTotal"></canvas>
        </div>
        <div class="panel">
            <h3>Avanço da OP (%)</h3>
            <canvas id="graficoPercentual"></canvas>
        </div>
    </section>

    <table>
        <thead>
            <tr>
                <th>Hora</th>
                <th>Máquina</th>
                <th>Evento</th>
            </tr>
        </thead>
        <tbody id="eventos"></tbody>
    </table>
</main>

<script>
let graficoTotal = null;
let graficoPercentual = null;

function fmt(n) {
    return Number(n || 0).toLocaleString("pt-BR", {maximumFractionDigits: 0});
}

function classeStatus(status) {
    const s = String(status || "").toUpperCase();
    if (s.includes("PRODUZINDO")) return "produzindo";
    if (s.includes("PARADA")) return "parada";
    if (s.includes("ATEN")) return "atencao";
    return "sem";
}

async function carregar() {
    const r = await fetch("/api/status");
    const data = await r.json();

    document.getElementById("ultima").innerText = "Última atualização da página: " + data.ultima_atualizacao;
    document.getElementById("horaAtual").innerText = data.ultima_atualizacao;
    document.getElementById("velTotal").innerText = fmt(data.resumo.velocidade_total) + " un/h";
    document.getElementById("produzindo").innerText = fmt(data.resumo.produzindo) + " máq.";
    document.getElementById("paradas").innerText = fmt(data.resumo.paradas) + " máq.";

    const cards = document.getElementById("cards");
    cards.innerHTML = "";

    const nomes = [];
    const totais = [];
    const percentuais = [];

    Object.values(data.maquinas).forEach(m => {
        const perc = m.meta > 0 ? (m.total / m.meta) * 100 : 0;
        nomes.push(m.nome);
        totais.push(m.total);
        percentuais.push(perc);

        const cls = classeStatus(m.status);

        const div = document.createElement("div");
        div.className = "card " + cls;

        div.innerHTML = `
            <div class="card-head">
                <h2>${m.nome}</h2>
                <span class="badge ${cls}">${m.status}</span>
            </div>

            <div class="info">
                <div class="box"><small>OP</small><b>${m.op}</b></div>
                <div class="box"><small>Produto</small><b>${m.produto}</b></div>
                <div class="box"><small>Equipe</small><b>${m.equipe}</b></div>
                <div class="box"><small>Quantidade OP</small><b>${m.meta > 0 ? fmt(m.meta) : "-"}</b></div>
            </div>

            <div class="big">
                <div class="box">
                    <small>Produzidos</small>
                    <b>${fmt(m.total)} de ${m.meta > 0 ? fmt(m.meta) : "-"}</b>
                    <div class="progress">
                        <div class="bar" style="width:${Math.min(perc, 100)}%;"></div>
                    </div>
                    <small>${m.meta > 0 ? perc.toFixed(1) + "%" : "Sem quantidade informada"}</small>
                </div>

                <div class="box">
                    <small>Velocidade</small>
                    <b>${fmt(m.velocidade)} /h</b>
                </div>
            </div>

            <div class="last">
                Tipo: ${m.tipo} | Última leitura: ${m.ultima}
            </div>
        `;

        cards.appendChild(div);
    });

    atualizarGraficos(nomes, totais, percentuais);
    atualizarEventos(data.eventos);
}

function atualizarGraficos(nomes, totais, percentuais) {
    const opt = {
        responsive: true,
        plugins: {
            legend: {
                labels: {
                    color: "#e5e7eb"
                }
            }
        },
        scales: {
            x: {
                ticks: { color: "#94a3b8" },
                grid: { color: "rgba(255,255,255,0.08)" }
            },
            y: {
                ticks: { color: "#94a3b8" },
                grid: { color: "rgba(255,255,255,0.08)" }
            }
        }
    };

    if (!graficoTotal) {
        graficoTotal = new Chart(document.getElementById("graficoTotal"), {
            type: "bar",
            data: {
                labels: nomes,
                datasets: [{
                    label: "Produzidos",
                    data: totais,
                    backgroundColor: "#38bdf8"
                }]
            },
            options: opt
        });
    } else {
        graficoTotal.data.labels = nomes;
        graficoTotal.data.datasets[0].data = totais;
        graficoTotal.update();
    }

    if (!graficoPercentual) {
        graficoPercentual = new Chart(document.getElementById("graficoPercentual"), {
            type: "bar",
            data: {
                labels: nomes,
                datasets: [{
                    label: "Avanço da OP (%)",
                    data: percentuais,
                    backgroundColor: "#22c55e"
                }]
            },
            options: opt
        });
    } else {
        graficoPercentual.data.labels = nomes;
        graficoPercentual.data.datasets[0].data = percentuais;
        graficoPercentual.update();
    }
}

function atualizarEventos(eventos) {
    const tbody = document.getElementById("eventos");
    tbody.innerHTML = "";

    eventos.forEach(e => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${e.data_hora}</td>
            <td>${e.maquina}</td>
            <td>${e.descricao}</td>
        `;
        tbody.appendChild(tr);
    });
}

carregar();
setInterval(carregar, 3000);
</script>

</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
