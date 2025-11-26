import random


class PerceptronPuro:

    def __init__(self, n_features, eta=0.1, max_epoch=5000):
        self.eta = eta
        self.max_epoch = max_epoch
        self.n_features = n_features
        # Inicia pesos e bias aleatórios no intervalo [-0.5, 0.5].
        self.weights = [random.uniform(-0.5, 0.5) for _ in range(n_features)]
        self.bias = random.uniform(-0.5, 0.5)
        self.logs = []
        self.errors_per_epoch = []
        self.converged_epoch = None
        self.current_epoch = 0

    def ativacao(self, z):
        return 1 if z >= 0 else 0

    def produto_interno(self, x):
        z = 0
        for i in range(self.n_features):
            z += self.weights[i] * x[i]
        z += self.bias
        return z

    def treinar_epoca(self, X, y):
        erros = 0
        self.current_epoch += 1
        epoca = self.current_epoch
        self.logs.append(f"\n=== ÉPOCA {epoca} ===\n")

        for idx, x in enumerate(X):
            esperado = y[idx]
            z = self.produto_interno(x)
            previsto = self.ativacao(z)
            erro = esperado - previsto

            self.logs.append(
                f"Amostra {idx}: esperado={esperado}, previsto={previsto}, z={z:.3f}"
            )

            if erro != 0:
                erros += 1
                self.logs.append("ERRO! Ajustando pesos...")

                for i in range(self.n_features):
                    self.weights[i] += self.eta * erro * x[i]

                self.bias += self.eta * erro

            pesos_fmt = [f"{w:.4f}" for w in self.weights]
            self.logs.append(
                f"Pesos: {pesos_fmt}, Bias: {self.bias:.4f}\n"
            )

        self.errors_per_epoch.append(erros)

        if erros == 0:
            self.converged_epoch = epoca

        return erros
