import socket


class ComunicadorUDP:

    @staticmethod
    def monta_mensagem(mensagem: str, ip: str, porta: int) -> dict:
        try:
            buffer = mensagem.encode("utf-8")
            return {"dados": buffer, "ip": ip, "porta": porta}
        except Exception:
            return None

    @staticmethod
    def recebe_mensagem(
        sock: socket.socket, buffer_size: int = 1024
    ) -> dict | None:
        try:
            dados, (ip, porta) = sock.recvfrom(buffer_size)
            return {"dados": dados, "ip": ip, "porta": porta}
        except Exception:
            return None

    @staticmethod
    def envia_mensagem(sock: socket.socket, pacote: dict):
        try:
            sock.sendto(pacote["dados"], (pacote["ip"], pacote["porta"]))
        except Exception as e:
            print(f"[ERRO ComunicadorUDP] Falha ao enviar mensagem: {e}")