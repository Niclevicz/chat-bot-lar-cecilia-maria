from flask import Flask, request, jsonify, render_template, session
from chatbot_alura import (
    carregar_animais,
    agente_buscar_animais,
    agente_apresentar_animal,
    agente_agendar_visita
)
from datetime import datetime
import random

# Inicializa o app Flask e configura a chave secreta da sessão
app = Flask(__name__)
app.secret_key = 'chave-muito-segura-e-secreta'

# Carrega os dados dos animais disponíveis para adoção
animais = carregar_animais("lista_animais.txt")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=['POST'])
def chat():
    # Captura a mensagem enviada pelo frontend
    dados = request.get_json()
    msg_original = dados.get("msg", "").strip()  
    msg = msg_original.lower()  
    
    # ✅ SINALIZADOR: reinício antes de qualquer outro processamento
    if msg == "reiniciar":
        session.pop("estado_conversa", None)
        return "Vamos começar de novo! Qual é o seu nome? 😊"

    # Recupera ou inicializa o estado da conversa
    estado_conversa = session.get("estado_conversa", {
        "nome": None,
        "etapa": "nome",
        "especie": None,
        "faixa_etaria": None,
        "porte": None,
        "sexo": None,
        "data": None
    })

    # ✅ SINALIZADOR: reiniciar se etapa estiver corrompida
    if estado_conversa.get("etapa") not in [
        "nome", "especie", "faixa_etaria", "porte", "sexo", "resultado",
        "gostou", "agendamento_data", "agendamento_hora", "tentar_novamente", "finalizar"
    ]:
        estado_conversa = {
            "nome": None,
            "etapa": "nome",
            "especie": None,
            "faixa_etaria": None,
            "porte": None,
            "sexo": None,
            "data": None
        }
        session["estado_conversa"] = estado_conversa
        return "Algo saiu do esperado. Vamos começar de novo! Qual é o seu nome?"

    # ETAPA: Perguntar nome do adotante
    if estado_conversa["etapa"] == "nome":
        respostas_invalidas = ["gato", "cachorro", "filhote", "adulto", "idoso", "sim", "não", "nao"]
        if msg in respostas_invalidas:
            session["estado_conversa"] = estado_conversa
            return "Sei que você está ansioso para adotar, mas preciso que você insira o seu nome 😊"
        estado_conversa["nome"] = msg_original.title()
        estado_conversa["etapa"] = "especie"
        session["estado_conversa"] = estado_conversa
        return f"Oi {estado_conversa['nome']}! Vamos procurar seu(sua) novo(a) melhor amigo(a)? ❤\n\nVocê quer adotar um gato ou cachorro?"

    # ETAPA: Perguntar espécie
    elif estado_conversa["etapa"] == "especie":
        if msg not in ["gato", "cachorro"]:
            session["estado_conversa"] = estado_conversa
            return "Por favor, responda com 'gato' ou 'cachorro' 🐱🐶"
        estado_conversa["especie"] = msg
        estado_conversa["etapa"] = "faixa_etaria"
        session["estado_conversa"] = estado_conversa
        return "Você procura um animal filhote, adulto ou idoso?"

    # ETAPA: Perguntar faixa etária
    elif estado_conversa["etapa"] == "faixa_etaria":
        if msg not in ["filhote", "adulto", "idoso"]:
            session["estado_conversa"] = estado_conversa
            return "Por favor, responda com 'filhote', 'adulto' ou 'idoso' 🐾"
        estado_conversa["faixa_etaria"] = msg
        estado_conversa["etapa"] = "porte"
        session["estado_conversa"] = estado_conversa
        return "Qual porte? (pequeno, médio, grande)?"

    # ETAPA: Perguntar porte
    elif estado_conversa["etapa"] == "porte":
        if msg not in ["pequeno", "médio", "medio", "grande"]:
            session["estado_conversa"] = estado_conversa
            return "Responda com: pequeno, médio ou grande 🐾"
        estado_conversa["porte"] = msg
        estado_conversa["etapa"] = "sexo"
        session["estado_conversa"] = estado_conversa
        return "Você prefere macho ou fêmea?"

    # ETAPA: Perguntar sexo
    elif estado_conversa["etapa"] == "sexo":
        estado_conversa["sexo"] = msg if msg in ["macho", "fêmea", "femea", ""] else ""
        estado_conversa["etapa"] = "resultado"
        session["estado_conversa"] = estado_conversa

        encontrados = agente_buscar_animais(
            animais,
            especie=estado_conversa["especie"],
            faixa_etaria=estado_conversa["faixa_etaria"],
            porte=estado_conversa["porte"],
            sexo=estado_conversa["sexo"]
        )

        if len(encontrados) >= 2:
            texto = f"🐾 Encontrei dois {estado_conversa['especie']}s para você, {estado_conversa['nome']}!\n\n"
            for animal in encontrados[:2]:
                texto += agente_apresentar_animal(animal) + "\n\n"
            estado_conversa["etapa"] = "gostou"
            session["estado_conversa"] = estado_conversa
            return texto.strip() + "\n\nVocê gostou de algum deles? Responda com 'sim' ou 'não' 💬"

        sugestoes = agente_buscar_animais(animais, especie=estado_conversa["especie"]) or []
        if sugestoes:
            sugerido = random.choice(sugestoes)
            estado_conversa["etapa"] = "gostou"
            session["estado_conversa"] = estado_conversa
            return (
                "🐾 Ainda não encontrei exatamente o que você pediu, mas talvez esse amiguinho te encante:\n\n"
                + agente_apresentar_animal(sugerido, sugestao=True)
                + "\n\nVocê gostou de algum deles? Responda com 'sim' ou 'não' 💬"
            )

        estado_conversa["etapa"] = "finalizar"
        session["estado_conversa"] = estado_conversa
        return "😔 Ainda não temos esse perfil, mas novos amiguinhos chegam em breve!"

    # ETAPA: Verificar se gostou dos animais
    elif estado_conversa["etapa"] == "gostou":
        if "sim" in msg:
            estado_conversa["etapa"] = "agendamento_data"
            session["estado_conversa"] = estado_conversa
            return "Que alegria! 🐾 Me diga o dia que deseja visitar (formato: 25/05):"
        elif "não" in msg or "nao" in msg:
            estado_conversa["etapa"] = "tentar_novamente"
            session["estado_conversa"] = estado_conversa
            return "Ah, que pena que nenhum te encantou hoje... Mas não desanime!\nDeseja procurar outro perfil? (sim/não)"
        else:
            session["estado_conversa"] = estado_conversa
            return "Você gostou de algum deles? Responda com 'sim' ou 'não' 💬"

    # ETAPA: Perguntar data para visita
    elif estado_conversa["etapa"] == "agendamento_data":
        try:
            data_informada = datetime.strptime(msg, "%d/%m").replace(year=datetime.now().year)
            if data_informada.date() < datetime.now().date():
                session["estado_conversa"] = estado_conversa
                return "⚠️ Essa data já passou! Escolha uma data futura."
            estado_conversa["data"] = data_informada.strftime("%d/%m/%Y")
            estado_conversa["etapa"] = "agendamento_hora"
            session["estado_conversa"] = estado_conversa
            return "E qual horário? (ex: 15:00)"
        except:
            session["estado_conversa"] = estado_conversa
            return "⚠️ Formato inválido de data. Exemplo: 25/05"

    # ETAPA: Confirmar hora e finalizar
    elif estado_conversa["etapa"] == "agendamento_hora":
        hora = msg
        texto_confirmacao = agente_agendar_visita(estado_conversa["data"], hora)
        estado_conversa["etapa"] = "finalizar"
        session["estado_conversa"] = estado_conversa
        return texto_confirmacao

    # ETAPA: Repetir, busca ou encerrar
    elif estado_conversa["etapa"] == "tentar_novamente":
        if "sim" in msg:
            estado_conversa.update({
                "etapa": "especie",
                "especie": None,
                "faixa_etaria": None,
                "porte": None,
                "sexo": None
            })
            session["estado_conversa"] = estado_conversa
            return "Vamos tentar de novo! 🐾 Você quer adotar um gato ou cachorro?"
        elif "não" in msg or "nao" in msg:
            estado_conversa["etapa"] = "finalizar"
            session["estado_conversa"] = estado_conversa
            return "Que pena, mas eu 🐾 estarei sempre aqui, torcendo para você encontrar seu(a) melhor amigo(a) em breve 💖🐶🐱"
        else:
            session["estado_conversa"] = estado_conversa
            return "Você deseja tentar novamente? Responda com 'sim' ou 'não' 💬"

    # ETAPA: Finalização da conversa
    elif estado_conversa["etapa"] == "finalizar":
        return "Se quiser começar novamente, envie 'reiniciar' 💬"

    # recuo genérico
    session["estado_conversa"] = estado_conversa
    return "Desculpe, não entendi. Vamos tentar de novo? 😊"

# Inicia o servidor Flask
if __name__ == "__main__":
    app.run(debug=True)
