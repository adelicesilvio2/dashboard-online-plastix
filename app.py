from flask import Flask, request, jsonify, Response
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
    return jsonify({
        "maquinas": maquinas,
        "eventos": eventos[-30:][::-1],
        "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })


@app.route("/api/receber", methods=["POST"])
def receber():
    dados = request.get_json(force=True)

    chave = dados.get("api_key", "")
    if chave != API_KEY:
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
        "descricao": f"{nome} atualizada | OP {m['op']} | {m['total']} de {m['meta']}"
    })

    return jsonify({"ok": True, "maquina": nome})


HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Dashboard Online PLASTIX</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #0f172a;
    color: #e5e7eb;
}
header {
    padding: 18px 24px;
    background: #020617;
    border-bottom: 1px solid rgba(255,255,255,0.12);
}
h1 {
    margin: 0;
    font-size: 26px;
}
.sub {
    color: #94a3b8;
    font-size: 13px;
    margin-top: 4px;
}
main {
    padding: 20px;
}
.cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
}
.card {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 12px 28px rgba(0,0,0,0.3);
}
.card h2 {
    margin: 0 0 8px;
}
.badge {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: bold;
    background: #334155;
}
.produzindo { color: #86efac; background: rgba(34,197,94,0.15); }
.parada { color: #fca5a5; background: rgba(239,68,68,0.15); }
.atencao { color: #fde68a; background: rgba(234,179,8,0.15); }
.sem { color: #cbd5e1; background: rgba(148,163,184,0.15); }

.info {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 12px;
}
.box {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 10px;
}
.box small {
    color: #94a3b8;
}
.box b {
    display: block;
    font-size: 16px;
    margin-top: 4px;
}
.progress {
    height: 8px;
    background: rgba(255,255,255,0.12);
    border-radius: 999px;
    overflow: hidden;
    margin-top: 8px;
}
.bar {
    height: 100%;
    background: #38bdf8;
}
.charts {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    margin-top: 22px;
}
.panel {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 18px;
    padding: 16px;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 22px;
    background: #111827;
    border-radius: 18px;
    overflow: hidden;
}
td, th {
    padding: 10px;
    border-bottom: 1px solid rgba(255,255,255,0.10);
}
th {
    color: #94a3b8;
    text-align: left;
}
@media(max-width: 1100px) {
    .cards { grid-template-columns: 1fr; }
    .charts { grid-template-columns: 1fr; }
}
</style>
</head>
<body>
<header>
    <h1>Dashboard Online - Produção Sopradoras</h1>
    <div class="sub" id="ultima">Aguardando dados...</div>
</header>

<main>
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
        div.className = "card";
        div.innerHTML = `
            <h2>${m.nome}</h2>
            <span class="badge ${cls}">${m.status}</span>

            <div class="info">
                <div class="box"><small>OP</small><b>${m.op}</b></div>
                <div class="box"><small>Produto</small><b>${m.produto}</b></div>
                <div class="box"><small>Equipe</small><b>${m.equipe}</b></div>
                <div class="box"><small>Quantidade OP</small><b>${m.meta > 0 ? fmt(m.meta) : "-"}</b></div>
            </div>

            <div class="box" style="margin-top:10px;">
                <small>Produzidos</small>
                <b>${fmt(m.total)} de ${m.meta > 0 ? fmt(m.meta) : "-"}</b>
                <div class="progress">
                    <div class="bar" style="width:${Math.min(perc, 100)}%;"></div>
                </div>
                <small>${m.meta > 0 ? perc.toFixed(1) + "%" : "Sem quantidade informada"}</small>
            </div>

            <div class="box" style="margin-top:10px;">
                <small>Velocidade</small>
                <b>${fmt(m.velocidade)} un/h</b>
            </div>

            <div style="color:#94a3b8; font-size:12px; margin-top:10px;">
                Última leitura: ${m.ultima}
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
        plugins: { legend: { labels: { color: "#e5e7eb" } } },
        scales: {
            x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.08)" } },
            y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.08)" } }
        }
    };

    if (!graficoTotal) {
        graficoTotal = new Chart(document.getElementById("graficoTotal"), {
            type: "bar",
            data: {
                labels: nomes,
                datasets: [{ label: "Produzidos", data: totais }]
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
                datasets: [{ label: "Avanço da OP (%)", data: percentuais }]
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
