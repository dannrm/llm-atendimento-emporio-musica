#Este script tem como objetivo desenvolver o agente e estabelecer a comunicação com o cliente
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from google import genai
from google.genai import types,errors
from src.agent.prompt import carregar_prompt
from src.data.buscar_db import buscar_produtos, consultar_pedido, listar_promocoes_ativas

#Def. os dias da semana
DIAS = ["segunda-feira",
        "terça-feira",
        "quarta-feira",
        "quinta-feira",
        "sexta-feira",
        "sábado",
        "domingo"]

#Função que retorna a data e hora atual baseado na cidade em que esta a loja
def data_hora_atual() -> str:
    agora = datetime.now(ZoneInfo("America/Campo_Grande"))

    return (f"Agora são {agora:%H:%M} de {DIAS[agora.weekday()]}, {agora:%d/%m/%Y} (horário de Campo Grande).")

#Criando o agente que irá realizar o atendimento: Lady Gaita
class Agente:
    def __init__(self):
        #Carregando o .env e o modelo escolhido
        load_dotenv()
        modelo = os.getenv("GEMINI_MODEL")

        #Cliente guardado no objeto para a conexão não ser fechada
        self.cliente = genai.Client()

        #System Prompt do agente integrando políticas e horário local
        system_prompt = carregar_prompt() + "\n\n" + data_hora_atual()

        #"Memorizando" o histórico de conversas
        self.chat = self.cliente.chats.create(
            model=modelo,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools = [buscar_produtos, consultar_pedido, listar_promocoes_ativas],
            ),
        )

    #Input do cliente"
    def responder(self, mensagem: str) -> str:
        resposta = self.chat.send_message(mensagem)
        return resposta.text

if __name__ == "__main__":
    agente = Agente()
    print("Olá! Sou a Lady Gaita! Sua atendente virtual! 👩‍🦳🪗  \n"
        "Como posso te ajudar hoje? — digite 'sair' para encerrar.")

    #Laco criado para manter a comunicacao usuário <-> agente
    while True:
        mensagem = input("Você: ").strip()

        if mensagem.lower() in ("sair", "exit", "quit"):
            print("Até a próxima! 🎶")
            break

        if not mensagem:
            continue

        try:
            print(f"\nLady Gaita: {agente.responder(mensagem)}\n")
        except errors.APIError as erro:
            if erro.code in (429, 503):
                print("\nLady Gaita: Estou com muitas mensagens agora 😅 "
                      "Tenta de novo em um minutinho!\n")
            else:
                raise