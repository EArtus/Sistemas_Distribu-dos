import socket
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from comunicador_udp import ComunicadorUDP


class ClienteUDPApp:

    def __init__(
        self, root: tk.Tk, host_servidor: str = "127.0.0.1", porta_servidor: int = 1234
    ):
        self.root = root
        self.root.title("Cliente UDP - Sistemas Distribuídos")
        self.root.geometry("460x430")
        self.root.resizable(False, False)

        self.host_servidor = host_servidor
        self.porta_servidor = porta_servidor

        # Socket UDP do cliente com timeout
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(3.0)

        # Estado do temporizador
        self.tempo_restante = 0
        self.timer_rodando = False

        self._criar_interface()

    def _criar_interface(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Aba Cadastro
        aba_cadastro = ttk.Frame(notebook)
        notebook.add(aba_cadastro, text="1. Cadastro")
        self._montar_aba_cadastro(aba_cadastro)

        # Aba Token
        aba_token = ttk.Frame(notebook)
        notebook.add(aba_token, text="2. Autenticação (Token)")
        self._montar_aba_token(aba_token)

    def _montar_aba_cadastro(self, frame: ttk.Frame):
        lbl_instrucao = ttk.Label(
            frame,
            text="Informe seus dados para cadastro no servidor:",
            font=("Arial", 10, "bold"),
        )
        lbl_instrucao.pack(anchor="w", padx=15, pady=(15, 5))

        lbl_nome = ttk.Label(frame, text="Nome Completo:")
        lbl_nome.pack(anchor="w", padx=15, pady=(5, 2))
        self.ent_nome = ttk.Entry(frame, width=45)
        self.ent_nome.pack(padx=15, pady=(0, 10))

        lbl_email = ttk.Label(frame, text="E-mail:")
        lbl_email.pack(anchor="w", padx=15, pady=(5, 2))
        self.ent_email = ttk.Entry(frame, width=45)
        self.ent_email.pack(padx=15, pady=(0, 15))

        btn_cadastrar = ttk.Button(
            frame, text="Enviar Cadastro", command=self.enviar_cadastro
        )
        btn_cadastrar.pack(pady=10)

        self.lbl_status_cadastro = ttk.Label(
            frame, text="", font=("Arial", 9, "italic")
        )
        self.lbl_status_cadastro.pack(pady=10)

    def _montar_aba_token(self, frame: ttk.Frame):
        lbl_instrucao = ttk.Label(
            frame,
            text="Solicitação e Validação de Token (60s)",
            font=("Arial", 10, "bold"),
        )
        lbl_instrucao.pack(anchor="w", padx=15, pady=(15, 5))

        lbl_email_token = ttk.Label(
            frame, text="E-mail Cadastrado (identificador):"
        )
        lbl_email_token.pack(anchor="w", padx=15, pady=(5, 2))
        self.ent_email_token = ttk.Entry(frame, width=45)
        self.ent_email_token.pack(padx=15, pady=(0, 15))

        btn_solicitar = ttk.Button(
            frame,
            text="Solicitar / Atualizar Token",
            command=self.solicitar_token,
        )
        btn_solicitar.pack(pady=10)

        frame_token = ttk.LabelFrame(frame, text=" Token Ativo ")
        frame_token.pack(fill="x", padx=15, pady=10)

        self.lbl_token = ttk.Label(
            frame_token,
            text="Nenhum token gerado",
            font=("Courier", 14, "bold"),
            anchor="center",
        )
        self.lbl_token.pack(pady=10)

        self.lbl_timer = ttk.Label(
            frame_token, text="Validade: --", font=("Arial", 9)
        )
        self.lbl_timer.pack(pady=(0, 10))

    def _trocar_mensagem_servidor(self, texto_mensagem: str) -> str:
        """Envia e recebe pacotes utilizando a classe ComunicadorUDP."""
        pacote_envio = ComunicadorUDP.monta_mensagem(
            texto_mensagem, self.host_servidor, self.porta_servidor
        )
        if not pacote_envio:
            return "ERRO;Falha ao montar o pacote."

        ComunicadorUDP.envia_mensagem(self.socket, pacote_envio)

        pacote_resposta = ComunicadorUDP.recebe_mensagem(self.socket)
        if pacote_resposta and pacote_resposta.get("dados"):
            return pacote_resposta["dados"].decode("utf-8").strip()

        return "ERRO;Servidor indisponível (Timeout)."

    def enviar_cadastro(self):
        nome = self.ent_nome.get().strip()
        email = self.ent_email.get().strip()

        if not nome or not email:
            messagebox.showwarning(
                "Aviso", "Por favor, preencha o Nome e o E-mail!"
            )
            return

        mensagem = f"CADASTRO;{nome};{email}"
        threading.Thread(
            target=self._processar_cadastro, args=(mensagem,), daemon=True
        ).start()

    def _processar_cadastro(self, mensagem: str):
        resposta = self._trocar_mensagem_servidor(mensagem)
        partes = resposta.split(";")

        status = partes[0]
        texto = partes[1] if len(partes) > 1 else resposta

        self.lbl_status_cadastro.config(text=texto)

        if status == "ERRO":
            messagebox.showerror("Erro de Cadastro", texto)
        else:
            messagebox.showinfo("Sucesso", texto)

    def solicitar_token(self):
        email = self.ent_email_token.get().strip()

        if not email:
            messagebox.showwarning(
                "Aviso", "Informe o e-mail cadastrado para solicitar o token!"
            )
            return

        mensagem = f"TOKEN;{email}"
        threading.Thread(
            target=self._processar_token, args=(mensagem,), daemon=True
        ).start()

    def _processar_token(self, mensagem: str):
        resposta = self._trocar_mensagem_servidor(mensagem)
        partes = resposta.split(";")

        if partes[0] == "ERRO":
            msg_erro = partes[1] if len(partes) > 1 else resposta
            messagebox.showerror("Erro de Autenticação", msg_erro)
            return

        token_chave = partes[0]
        tempo_validez = int(partes[1]) if len(partes) > 1 else 60

        self.lbl_token.config(text=token_chave)
        self.iniciar_temporizador(tempo_validez)

    def iniciar_temporizador(self, segundos: int):
        self.tempo_restante = segundos
        if not self.timer_rodando:
            self.timer_rodando = True
            self._atualizar_timer()

    def _atualizar_timer(self):
        if self.tempo_restante > 0:
            self.lbl_timer.config(
                text=f"Validade: {self.tempo_restante}s restantes"
            )
            self.tempo_restante -= 1
            self.root.after(1000, self._atualizar_timer)
        else:
            self.lbl_timer.config(text="Validade: Token Expirado!")
            self.timer_rodando = False


if __name__ == "__main__":
    root = tk.Tk()
    app = ClienteUDPApp(root, host_servidor="127.0.0.1", porta_servidor=1234)
    root.mainloop()