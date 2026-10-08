import socket
from comunicador_udp import ComunicadorUDP
from pessoa import Pessoa


class ServidorUDP:

    def __init__(self, host: str = "127.0.0.1", porta: int = 1234):
        self.host = host
        self.porta = porta
        self.usuarios: list[Pessoa] = []

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((self.host, self.porta))
        except Exception as e:
            print(f"[ERRO BIND] Não foi possível abrir a porta {self.porta}: {e}")
            raise e

    def buscar_usuario(self, email: str) -> Pessoa | None:
        for p in self.usuarios:
            if p.email.lower() == email.lower():
                return p
        return None

    def processar_requisicao(self, mensagem: str) -> str:
        partes = mensagem.split(";")
        comando = partes[0].upper()

        if comando == "CADASTRO":
            if len(partes) < 3:
                return "ERRO;Dados de cadastro incompletos."

            nome = partes[1].strip()
            email = partes[2].strip()

            if self.buscar_usuario(email):
                return f"ERRO;O e-mail '{email}' já está cadastrado!"

            novo_usuario = Pessoa(nome, email)
            self.usuarios.append(novo_usuario)
            print(f"[CADASTRO SUCESSO] Usuário '{nome}' ({email}) registrado.")
            return f"SUCESSO;Usuário '{nome}' cadastrado com sucesso!"

        elif comando == "TOKEN":
            if len(partes) < 2:
                return "ERRO;E-mail não informado."

            email = partes[1].strip()
            usuario = self.buscar_usuario(email)

            if not usuario:
                return "ERRO;Usuário não encontrado. Cadastre-se primeiro!"

            token, tempo_restante = usuario.gerar_ou_obter_token()
            print(
                f"[TOKEN SOLICITADO] {email} -> Token: {token} (Validade: {tempo_restante}s)"
            )
            return f"{token};{tempo_restante}"

        else:
            return "ERRO;Comando não reconhecido pelo servidor."

    def iniciar(self):
        print(f"=== SERVIDOR UDP ATIVO ===")
        print(f"Escutando em {self.host}:{self.porta}...")

        while True:
            try:
                pacote_recebido = ComunicadorUDP.recebe_mensagem(
                    self.socket, buffer_size=1024
                )

                if pacote_recebido and pacote_recebido.get("dados"):
                    mensagem = (
                        pacote_recebido["dados"].decode("utf-8").strip()
                    )
                    ip_origem = pacote_recebido["ip"]
                    porta_origem = pacote_recebido["porta"]

                    print(
                        f"\n[RECEBIDO DE {ip_origem}:{porta_origem}] {mensagem}"
                    )

                    resposta_texto = self.processar_requisicao(mensagem)

                    pacote_resposta = ComunicadorUDP.monta_mensagem(
                        resposta_texto, ip_origem, porta_origem
                    )

                    if pacote_resposta:
                        ComunicadorUDP.envia_mensagem(
                            self.socket, pacote_resposta
                        )

            except Exception as e:
                print(f"[ERRO NO LOOP DO SERVIDOR]: {e}")


if __name__ == "__main__":
    servidor = ServidorUDP(host="127.0.0.1", porta=1234)
    servidor.iniciar()