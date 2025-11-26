from flask import Flask, render_template, request, jsonify
from perceptron_puro import PerceptronPuro

app = Flask(__name__)

perceptron = None
X = []
y = []
dataset = []
feature_names = []
target_name = "y"
has_label_column = False


def _detect_sep(line: str) -> str:
    """Escolhe separador mais provável entre vírgula ou ponto e vírgula."""
    return ";" if line.count(";") > line.count(",") else ","


def ler_csv_puro(file):
    """
    Lê CSV com cabeçalho. Suporta primeira coluna textual (rótulo) e
    usa vírgula ou ponto e vírgula como separador. Converte vírgulas
    decimais para ponto.
    """
    content = file.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8-sig")
    linhas = [ln.strip() for ln in content.splitlines() if ln.strip()]
    if not linhas:
        return [], [], [], [], "y", False

    sep = _detect_sep(linhas[0])

    # Detecta se a primeira linha é cabeçalho (contém texto não numérico).
    header_try = [h.strip() for h in linhas[0].split(sep)]
    def _is_float(val: str) -> bool:
        try:
            float(val.replace(",", "."))
            return True
        except ValueError:
            return False

    header_is_numeric = all(_is_float(h) for h in header_try)
    header_parts = header_try if not header_is_numeric else []
    data_lines = linhas[1:] if header_parts else linhas

    # Rótulo se a primeira coluna sugere "amostra"/"id".
    has_label_col = False
    if header_parts:
        header_lower = [h.lower() for h in header_parts]
        has_label_col = header_lower[0].startswith(("amostra", "sample", "id"))
    else:
        # Sem cabeçalho: assume primeira coluna rótulo apenas se não for numérica.
        try:
            float(data_lines[0].split(sep)[0].replace(",", "."))
        except (ValueError, IndexError):
            has_label_col = True

    sample_cols = len(data_lines[0].split(sep)) if data_lines else len(header_parts)

    # Se deduzimos que há rótulo, mas as colunas de feature estão faltando,
    # podemos recuar: assume que a primeira coluna é feature (x1) em vez de rótulo.
    if header_parts and has_label_col:
        expected_features = max(sample_cols - 2, 0)
        raw_feature_names = header_parts[1:-1] if len(header_parts) > 1 else []
        if expected_features > len(raw_feature_names):
            has_label_col = False

    feat_start_idx = 1 if has_label_col else 0
    if header_parts:
        raw_feature_names = header_parts[feat_start_idx:-1] if len(header_parts) > 1 else []
        feature_names = raw_feature_names if raw_feature_names else [f"x{i+1}" for i in range(max(len(header_parts) - 1 - feat_start_idx, 1))]
        target_name = header_parts[-1] if header_parts else "y"
    else:
        # Sem cabeçalho: gera nomes padrão
        feature_count = max(sample_cols - 1 - feat_start_idx, 1)
        feature_names = [f"x{i+1}" for i in range(feature_count)]
        target_name = "y"

    dados = []
    for linha in data_lines:
        partes = [p.strip() for p in linha.split(sep) if p.strip() != ""]
        if len(partes) < 2:
            continue
        rotulo = partes[0] if has_label_col else f"Amostra {len(dados) + 1}"
        valores_brutos = partes[feat_start_idx:]

        try:
            valores = [float(v.replace(",", ".")) for v in valores_brutos]
        except ValueError:
            continue

        if len(valores) < 2:
            continue

        features = valores[:-1]
        target = int(round(valores[-1]))
        dados.append(
            {
                "label": rotulo or f"Amostra {len(dados) + 1}",
                "features": features,
                "target": target,
            }
        )

    X = [item["features"] for item in dados]
    y = [item["target"] for item in dados]
    return X, y, dados, feature_names, target_name, has_label_col


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    global X, y, perceptron, dataset, feature_names, target_name, has_label_column
    file = request.files["file"]
    X, y, dataset, feature_names, target_name, has_label_column = ler_csv_puro(file)
    if not X:
        return jsonify({"error": "CSV vazio ou em formato inválido."}), 400

    perceptron = PerceptronPuro(n_features=len(X[0]))
    return jsonify({
        "msg": "CSV carregado com sucesso!",
        "features": len(X[0]),
        "samples": len(X),
        "dataset": dataset,
        "weights": perceptron.weights,
        "bias": perceptron.bias,
        "eta": perceptron.eta,
        "max_epoch": perceptron.max_epoch,
        "feature_names": feature_names,
        "target_name": target_name,
        "has_label": has_label_column
    })


@app.route("/configurar", methods=["POST"])
def configurar():
    global perceptron, X
    if not X:
        return jsonify({"error": "Carregue um CSV antes de configurar."}), 400

    data = request.json
    eta = float(data["eta"])
    max_epoch = int(data["max_epoch"])
    perceptron = PerceptronPuro(n_features=len(X[0]), eta=eta, max_epoch=max_epoch)
    return jsonify({
        "msg": "Configurações aplicadas.",
        "eta": eta,
        "max_epoch": max_epoch,
        "weights": perceptron.weights,
        "bias": perceptron.bias
    })


@app.route("/rodar_epoca", methods=["POST"])
def rodar_epoca():
    global perceptron, X, y
    if not X:
        return jsonify({"error": "Carregue um CSV antes de treinar."}), 400

    data = request.get_json(silent=True) or {}
    eta = float(data.get("eta", perceptron.eta if perceptron else 0.1))
    max_epoch = int(data.get("max_epoch", perceptron.max_epoch if perceptron else 5000))

    if perceptron is None:
        perceptron = PerceptronPuro(n_features=len(X[0]), eta=eta, max_epoch=max_epoch)
    else:
        perceptron.eta = eta
        perceptron.max_epoch = max_epoch

    erros = perceptron.treinar_epoca(X, y)

    return jsonify({
        "epoch": perceptron.current_epoch,
        "errors": erros,
        "weights": perceptron.weights,
        "bias": perceptron.bias,
        "converged": perceptron.converged_epoch is not None,
        "log": perceptron.logs[-40:],
        "errors_list": perceptron.errors_per_epoch,
        "eta": eta,
        "max_epoch": max_epoch
    })


@app.route("/rodar_completo", methods=["POST"])
def rodar_completo():
    global perceptron, X, y
    if not X:
        return jsonify({"error": "Carregue um CSV antes de treinar."}), 400
    data = request.get_json(silent=True) or {}
    eta = float(data.get("eta", perceptron.eta if perceptron else 0.1))
    max_epoch = int(data.get("max_epoch", perceptron.max_epoch if perceptron else 5000))
    if perceptron is None:
        perceptron = PerceptronPuro(n_features=len(X[0]), eta=eta, max_epoch=max_epoch)
    else:
        perceptron.eta = eta
        perceptron.max_epoch = max_epoch

    while perceptron.current_epoch < perceptron.max_epoch:
        erros = perceptron.treinar_epoca(X, y)

    return jsonify({
        "epoch": perceptron.current_epoch,
        "weights": perceptron.weights,
        "bias": perceptron.bias,
        "converged": perceptron.converged_epoch,
        "errors_list": perceptron.errors_per_epoch,
        "log": perceptron.logs[-80:],
        "eta": eta,
        "max_epoch": max_epoch
    })


@app.route("/rodar_convergencia", methods=["POST"])
def rodar_convergencia():
    """
    Roda o treinamento até convergir (0 erros) ou até 5000 épocas.
    """
    global perceptron, X, y
    if not X:
        return jsonify({"error": "Carregue um CSV antes de treinar."}), 400
    data = request.get_json(silent=True) or {}
    eta = float(data.get("eta", perceptron.eta if perceptron else 0.1))
    limite_epocas = 5000
    if perceptron is None:
        perceptron = PerceptronPuro(n_features=len(X[0]), eta=eta, max_epoch=limite_epocas)
    else:
        perceptron.eta = eta
        perceptron.max_epoch = limite_epocas

    while perceptron.converged_epoch is None and perceptron.current_epoch < limite_epocas:
        erros = perceptron.treinar_epoca(X, y)
        if erros == 0:
            break

    return jsonify({
        "epoch": perceptron.current_epoch,
        "weights": perceptron.weights,
        "bias": perceptron.bias,
        "converged": perceptron.converged_epoch,
        "stopped_by_limit": perceptron.converged_epoch is None and perceptron.current_epoch >= limite_epocas,
        "errors_list": perceptron.errors_per_epoch,
        "log": perceptron.logs[-120:],
        "eta": eta,
        "max_epoch": limite_epocas
    })


@app.route("/reset", methods=["POST"])
def reset():
    global perceptron, X
    if not X:
        return jsonify({"error": "Carregue um CSV antes de resetar."}), 400

    eta = float(request.json.get("eta", 0.1))
    max_epoch = int(request.json.get("max_epoch", 100))
    perceptron = PerceptronPuro(n_features=len(X[0]), eta=eta, max_epoch=max_epoch)
    return jsonify({
        "msg": "Treinamento reiniciado.",
        "weights": perceptron.weights,
        "bias": perceptron.bias,
        "eta": eta,
        "max_epoch": max_epoch,
        "epoch": 0,
        "errors_list": []
    })


if __name__ == "__main__":
    app.run(debug=True)
