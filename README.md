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

## Uso
1. Acesse a URL no navegador.
2. Envie um CSV (suporta vírgula ou ponto e vírgula; cabeçalho opcional).
3. Ajuste taxa de aprendizado (η) e número de épocas.
4. Use os botões: Próxima Época, Rodar Treinamento Completo, Rodar até Convergir, Reset.

## Estrutura
- `app.py`: rotas Flask e controle do Perceptron.
- `perceptron_puro.py`: implementação do Perceptron puro.
- `templates/`: HTML principal.
- `static/`: CSS, JS e assets.
