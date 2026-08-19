"""
Modulo 1 - Exercicio 1: Sistema de Caixa Centralizado de Evento (padrao MVC)

5 caixas (threads) vendem fichas simultaneamente, todos atualizando
o mesmo saldo bancario centralizado do evento.

Cada caixa vende 1.000 fichas de R$ 10,00 -> saldo final esperado: R$ 50.000,00

Avalia: uso de threading.Lock para garantir exclusao mutua sobre o
recurso compartilhado (saldo_central), evitando condicao de corrida.
"""

import threading


# ==================== MODEL ====================
class CaixaCentralModel:
    """Responsavel pelos dados e pela logica de negocio (vendas + sincronizacao)."""

    def __init__(self, num_caixas=5, fichas_por_caixa=1000, preco_ficha=10.00):
        self.saldo_central = 0.0
        self.lock = threading.Lock()  # protege o recurso compartilhado (saldo_central)
        self.num_caixas = num_caixas
        self.fichas_por_caixa = fichas_por_caixa
        self.preco_ficha = preco_ficha

    def _vender_fichas(self, id_caixa):
        """Executado por cada thread (caixa). Atualiza o saldo compartilhado."""
        for _ in range(self.fichas_por_caixa):
            with self.lock:  # exclusao mutua: so uma thread por vez altera o saldo
                self.saldo_central += self.preco_ficha

    def processar_vendas(self):
        """Cria, inicia e aguarda as threads dos caixas."""
        threads = []

        for i in range(1, self.num_caixas + 1):
            t = threading.Thread(target=self._vender_fichas, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        return {
            "saldo_final": self.saldo_central,
            "saldo_esperado": self.num_caixas * self.fichas_por_caixa * self.preco_ficha
        }


# ==================== VIEW ====================
class CaixaView:
    """Responsavel apenas por exibir os dados."""

    def exibir_inicio(self):
        print("Iniciando vendas nos 5 caixas do evento...\n")

    def exibir_resultado(self, dados):
        print(f"\nSaldo final do evento: R$ {dados['saldo_final']:,.2f}")

        if dados["saldo_final"] == dados["saldo_esperado"]:
            print(f"Saldo confere com o esperado (R$ {dados['saldo_esperado']:,.2f})")
        else:
            print(f"Saldo incorreto! Esperado R$ {dados['saldo_esperado']:,.2f}, "
                  f"houve condicao de corrida.")


# ==================== CONTROLLER ====================
class CaixaController:
    """Faz a ponte entre Model e View."""

    def __init__(self):
        self.model = CaixaCentralModel()
        self.view = CaixaView()

    def executar(self):
        self.view.exibir_inicio()
        dados = self.model.processar_vendas()
        self.view.exibir_resultado(dados)


if __name__ == "__main__":
    CaixaController().executar()
