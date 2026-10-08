import random
import string
import time


class Pessoa:

    def __init__(self, nome: str, email: str):
        self.nome = nome
        self.email = email
        self.token = None
        self.token_timestamp = 0

    def gerar_ou_obter_token(self) -> tuple[str, int]:
        tempo_atual = time.time()
        tempo_decorrido = tempo_atual - self.token_timestamp

        if self.token is not None and tempo_decorrido < 60:
            tempo_restante = int(60 - tempo_decorrido)
            return self.token, tempo_restante

        self.token = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=8)
        )
        self.token_timestamp = tempo_atual
        return self.token, 60

    def __eq__(self, other):
        if isinstance(other, Pessoa):
            return self.email.lower() == other.email.lower()
        return False