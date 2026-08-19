"""
Modulo 2 - Exercicio 2: Processamento de Relatorio de Vendas por Filial

4 filiais (threads) calculam seu proprio faturamento a partir de listas
locais e isoladas (nenhum acesso a variavel global durante a execucao).
A thread principal aguarda todas e soma os resultados finais.

Avalia: conceito de Fork-Join e isolamento, usando threading.Thread
com retorno guardado em atributo do objeto.
"""

import threading
import random


class FilialThread(threading.Thread):
    """Cada instancia guarda seu proprio resultado -- sem variavel global."""

    def __init__(self, vendas_filial, nome_filial):
        super().__init__()
        self.vendas_filial = vendas_filial  # dado local, isolado
        self.nome_filial = nome_filial
        self.resultado = 0  # atributo do proprio objeto guarda o retorno

    def run(self):
        self.resultado = sum(self.vendas_filial)


def gerar_vendas_filial(qtd_registros=10000):
    """Simula os dados de vendas de uma filial (lista local, isolada)."""
    return [random.randint(10, 500) for _ in range(qtd_registros)]


if __name__ == "__main__":
    # 4 listas independentes, uma por filial
    filiais_dados = [gerar_vendas_filial() for _ in range(4)]

    # Fork: dispara as 4 threads, cada uma recebendo apenas sua propria lista
    threads = [FilialThread(dados, f"Filial {i + 1}") for i, dados in enumerate(filiais_dados)]

    for t in threads:
        t.start()

    # Join: aguarda cada thread terminar antes de ler o resultado
    for t in threads:
        t.join()

    for t in threads:
        print(f"Faturamento {t.nome_filial}: R$ {t.resultado:,.2f}")

    faturamento_total = sum(t.resultado for t in threads)
    print(f"\nFaturamento total da franquia: R$ {faturamento_total:,.2f}")
