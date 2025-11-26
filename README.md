# Perceptron Dashboard (Flask)

Dashboard Flask para carregar CSV, ajustar hiperparâmetros e acompanhar o treinamento de um Perceptron puro.

## Requisitos
- Python 3.10+ (testado em 3.11/3.12)
- `pip` disponível no PATH

## Instalação local
```bash
# (opcional) criar e ativar venv
python -m venv .venv
.\.venv\Scripts\activate

# instalar dependências
pip install -r requirements.txt
```

## Executar em localhost
```bash
python app.py
```
- O server sobe em http://127.0.0.1:5000/ (ou na porta definida em `PORT`).
- O app serve `templates/` e `static/` automaticamente.

### Alterar a porta (caso precise alterar localmente)
- PowerShell:
  ```ps1
  $env:PORT = 8000
  python app.py
  ```
- Prompt (cmd):
  ```bat
  set PORT=8000
  python app.py
  ```
- Bash/Zsh:
  ```bash
  PORT=8000 python app.py
  ```

## Uso
1. Acesse a URL no navegador.
2. Envie um CSV (suporta vírgula ou ponto e vírgula; cabeçalho opcional).
3. Ajuste taxa de aprendizado (η) e número de épocas.
4. Use os botões: Próxima Época, Rodar Treinamento Completo, Rodar até Convergir, Reset.
   - Pesos e bias são gerados aleatoriamente na criação do perceptron e em cada Reset (sem semente fixa, portanto valores variam a cada inicialização).
   - Próxima Época: roda uma época por clique.
   - Rodar Treinamento Completo: roda até atingir o limite de épocas configurado.
   - Rodar até Convergir: roda até convergir (0 erros) ou até 5000 épocas.

## Estrutura
- `app.py`: rotas Flask e controle do Perceptron.
- `perceptron_puro.py`: implementação do Perceptron puro.
- `templates/`: HTML principal.
- `static/`: CSS, JS e assets.

## Como o Perceptron calcula
Para cada amostra `x`:
- Faz o somatório (produto interno) `z = sum(w_i * x_i) + b`.
- Ativação degrau: `previsto = 1 se z >= 0, senão 0`.
- Erro: `erro = esperado - previsto` (–1, 0 ou 1).
- Se houve erro, ajusta pesos/bias: `w_i ← w_i + η * erro * x_i` e `b ← b + η * erro`.
- Uma época percorre todas as amostras; convergiu quando uma época termina com 0 erros.
