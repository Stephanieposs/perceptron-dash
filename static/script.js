const state = {
    dataset: [],
    lastLogs: [],
    featureNames: [],
    targetName: "y",
    hasLabel: true,
};

const el = (id) => document.getElementById(id);

const elements = {
    etaSlider: el("etaSlider"),
    etaValue: el("etaValue"),
    maxEpoch: el("max_epoch"),
    datasetCount: el("datasetCount"),
    dadosBody: el("dados-body"),
    dadosHead: el("dados-head"),
    uploadStatus: el("uploadStatus"),
    logContent: el("logContent"),
    epochValue: el("epochValue"),
    sampleValue: el("sampleValue"),
    etaCurrent: el("etaCurrent"),
    stopValue: el("stopValue"),
    weightsContainer: el("weightsContainer"),
    errorsList: el("errorsList"),
};

function parametrosAtuais() {
    return {
        eta: elements.etaSlider.value,
        max_epoch: elements.maxEpoch.value,
    };
}

function formatNumber(num) {
    if (num === undefined || num === null || Number.isNaN(num)) return "-";
    return Number(num).toFixed(3);
}

function setStatus(message, tone = "muted") {
    elements.uploadStatus.textContent = message;
    elements.uploadStatus.dataset.tone = tone;
}

function atualizarEtaDisplay() {
    const v = parseFloat(elements.etaSlider.value);
    elements.etaValue.textContent = v.toFixed(2);
}

function renderDataset() {
    elements.dadosBody.innerHTML = "";
    elements.datasetCount.textContent = `${state.dataset.length} amostras`;

    // Cabeçalho dinâmico
    const headRow = document.createElement("tr");
    const cols = [];
    if (state.hasLabel) {
        cols.push("<th>Amostra</th>");
    }
    cols.push(...state.featureNames.map((n) => `<th>${n}</th>`));
    cols.push(`<th>${state.targetName || "y"}</th>`);
    headRow.innerHTML = cols.join("");
    elements.dadosHead.innerHTML = "";
    elements.dadosHead.appendChild(headRow);

    if (!state.dataset.length) {
        const row = document.createElement("tr");
        row.classList.add("placeholder");
        row.innerHTML = `<td colspan="${cols.length}">Envie um CSV para visualizar as amostras.</td>`;
        elements.dadosBody.appendChild(row);
        return;
    }

    state.dataset.forEach((item) => {
        const tr = document.createElement("tr");
        const featCells = item.features
            .map((v) => `<td>${formatNumber(v)}</td>`)
            .join("");
        tr.innerHTML = `
            ${state.hasLabel ? `<td>${item.label || "-"}</td>` : ""}
            ${featCells}
            <td>${item.target}</td>
        `;
        elements.dadosBody.appendChild(tr);
    });
}

function renderErrors(errors) {
    elements.errorsList.innerHTML = "";
    if (!errors || !errors.length) {
        elements.errorsList.innerHTML = `<p class="muted">Nenhum treino executado.</p>`;
        return;
    }

    errors.forEach((err, idx) => {
        const bar = document.createElement("div");
        bar.className = "error-row";
        bar.innerHTML = `
            <span>Época ${idx + 1}</span>
            <div class="bar">
                <div class="bar-fill" style="width:${Math.min(err * 20, 100)}%"></div>
            </div>
            <strong>${err}</strong>
        `;
        elements.errorsList.appendChild(bar);
    });
}

function renderLog(logLines) {
    state.lastLogs = logLines || [];
    if (!state.lastLogs.length) {
        elements.logContent.textContent = "Sem logs ainda.";
        return;
    }
    elements.logContent.textContent = state.lastLogs.join("\n");
}

function inferSampleFromLog() {
    if (!state.lastLogs.length || !state.dataset.length) return "-";
    for (let i = state.lastLogs.length - 1; i >= 0; i--) {
        const line = state.lastLogs[i];
        const match = line.match(/Amostra\s+(\d+)/i);
        if (match) {
            const idx = parseInt(match[1], 10);
            const item = state.dataset[idx];
            if (item) return state.hasLabel ? (item.label || `#${idx}`) : `#${idx + 1}`;
        }
    }
    return "-";
}

function atualizarTela(d) {
    if (d.error) {
        setStatus(d.error, "error");
        return;
    }

    if (d.converged) {
        setStatus(`Convergiu na época ${d.converged}`, "success");
    }

    elements.epochValue.textContent = d.epoch ?? 0;
    elements.sampleValue.textContent = inferSampleFromLog();
    elements.etaCurrent.textContent = (d.eta ?? elements.etaSlider.value).toFixed(2);
    const stopText = d.converged
        ? `${d.converged} Épocas (convergido)`
        : `${d.max_epoch || elements.maxEpoch.value} Épocas`;
    elements.stopValue.textContent = stopText;

    if (Array.isArray(d.weights)) {
        renderWeights(d.weights);
    }
    renderBias(d.bias);

    renderErrors(d.errors_list);
    renderLog(d.log || state.lastLogs);
}

function uploadCSV() {
    const fileInput = el("csvfile");
    if (!fileInput.files.length) {
        setStatus("Selecione um arquivo antes de enviar.", "error");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    fetch("/upload_csv", { method: "POST", body: formData })
        .then((r) => r.json())
        .then((data) => {
            if (data.error) {
                setStatus(data.error, "error");
                return;
            }
            state.dataset = data.dataset || [];
            state.featureNames = data.feature_names || [];
            state.targetName = data.target_name || "y";
            state.hasLabel = Boolean(data.has_label);
            renderDataset();
            setStatus("Arquivo enviado", "success");
            atualizaPesosIniciais(data);
            elements.epochValue.textContent = 0;
            elements.sampleValue.textContent = "-";
        })
        .catch(() => setStatus("Falha ao enviar CSV.", "error"));
}

function rodarEpoca() {
    const payload = parametrosAtuais();
    fetch("/rodar_epoca", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    })
        .then((r) => r.json())
        .then((data) => atualizarTela(data))
        .catch(() => setStatus("Erro ao rodar época.", "error"));
}

function rodarCompleto() {
    const payload = parametrosAtuais();
    fetch("/rodar_completo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    })
        .then((r) => r.json())
        .then((data) => atualizarTela(data))
        .catch(() => setStatus("Erro ao rodar completo.", "error"));
}

function rodarConvergencia() {
    const payload = parametrosAtuais();
    fetch("/rodar_convergencia", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    })
        .then((r) => r.json())
        .then((data) => atualizarTela(data))
        .catch(() => setStatus("Erro ao rodar até convergência.", "error"));
}

function resetTreinamento() {
    const payload = {
        eta: elements.etaSlider.value,
        max_epoch: elements.maxEpoch.value,
    };

    fetch("/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    })
        .then((r) => r.json())
        .then((data) => {
            if (data.error) {
                setStatus(data.error, "error");
                return;
            }
            setStatus(data.msg || "Treinamento reiniciado.", "success");
            atualizaPesosIniciais(data);
            renderErrors([]);
            renderLog([]);
            elements.epochValue.textContent = 0;
            elements.sampleValue.textContent = "-";
        })
        .catch(() => setStatus("Erro ao resetar.", "error"));
}

function atualizaPesosIniciais(data) {
    if (Array.isArray(data.weights)) {
        renderWeights(data.weights);
    } else {
        elements.weightsContainer.innerHTML = `<p class="muted">Nenhum peso calculado ainda.</p>`;
    }
    renderBias(data.bias);
    elements.etaCurrent.textContent = parseFloat(data.eta ?? elements.etaSlider.value).toFixed(2);
    elements.stopValue.textContent = `${data.max_epoch ?? elements.maxEpoch.value} Épocas`;
}

function renderWeights(weights) {
    if (!Array.isArray(weights)) {
        elements.weightsContainer.innerHTML = `<p class="muted">Nenhum peso calculado ainda.</p>`;
        return;
    }
    elements.weightsContainer.innerHTML = "";
    const names = state.featureNames.length
        ? state.featureNames
        : weights.map((_, i) => `w${i + 1}`);

    weights.forEach((w, idx) => {
        const row = document.createElement("div");
        row.className = "weight-row";
        row.innerHTML = `
            <span>${names[idx] || "w" + (idx + 1)}</span>
            <strong>${formatNumber(w)}</strong>
        `;
        elements.weightsContainer.appendChild(row);
    });
}

function renderBias(bias) {
    const biasRow = document.createElement("div");
    biasRow.className = "weight-row";
    biasRow.innerHTML = `
        <span>b (Bias)</span>
        <strong>${formatNumber(bias)}</strong>
    `;

    // Remove bias rows and append latest
    [...elements.weightsContainer.querySelectorAll("[data-bias]")].forEach((n) => n.remove());
    biasRow.dataset.bias = "true";
    elements.weightsContainer.appendChild(biasRow);
}

function bindEvents() {
    el("csvfile").addEventListener("change", (e) => {
        const file = e.target.files?.[0];
        if (file) {
            setStatus(`Arquivo carregado: ${file.name}`, "success");
        } else {
            setStatus("Nenhum arquivo", "muted");
        }
    });
    el("uploadBtn").addEventListener("click", uploadCSV);
    el("epochBtn").addEventListener("click", rodarEpoca);
    el("fullBtn").addEventListener("click", rodarCompleto);
    const convergeBtn = el("convergeBtn");
    if (convergeBtn) {
        convergeBtn.addEventListener("click", rodarConvergencia);
    }
    el("resetBtn").addEventListener("click", resetTreinamento);
    el("clearLogBtn").addEventListener("click", () => renderLog([]));
    elements.etaSlider.addEventListener("input", atualizarEtaDisplay);
}

bindEvents();
atualizarEtaDisplay();
renderDataset();
