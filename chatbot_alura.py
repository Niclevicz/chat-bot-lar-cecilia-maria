import os
from dotenv import load_dotenv
import google.generativeai as genai 
import unicodedata
from datetime import datetime
import random


apresentacoes_feitas = 0

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel ("gemini-2.0-flash")

# Subagente responsável pela normalização de textos (acentos, maiúsculas etc.)
def normalize(texto):
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII').lower().strip()

# Subagente responsável por carregar e processar as fichas dos animais a partir do arquivo .txt.
def carregar_animais(nome_arquivo):
    animais = []
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
            linhas = arquivo.readlines()
            i = 0
            while i < len(linhas):
                if linhas[i].strip().isdigit():
                    animal = {}
                    animal['id'] = int(linhas[i].strip())
                    i += 1
                    if i < len(linhas):
                        animal['nome'] = linhas[i].strip()
                        i += 1

                    while i < len(linhas) and linhas[i].strip() != "":
                        if ":" in linhas[i]:
                            chave, valor = linhas[i].split(":", 1)
                            animal[chave.strip()] = valor.strip()
                        i += 1

                    idade_str = animal.get("Idade", "")
                    animal["faixa"] = classificar_faixa_etaria(idade_str)

                    animais.append(animal)
                else:
                    i += 1
    except FileNotFoundError:
        print(f"Erro: Arquivo '{nome_arquivo}' não encontrado.")
    except Exception as e:
        print(f"Erro ao carregar animais: {e}")
    return animais

# Subagente responsável por interpretar meses e anos corretamente.
def classificar_faixa_etaria(idade_str):
    idade_str = idade_str.lower().strip()
    try:
        if "mes" in idade_str:
            meses = int(idade_str.split()[0])
            if meses < 12:
                return "filhote"
        elif "ano" in idade_str:
            anos = int(idade_str.split()[0])
            if anos <= 7:
                return "adulto"
            else:
                return "idoso"
    except:
        pass
    return "indefinido"

# Subagente responsável por buscar animais com base nos filtros.
def agente_buscar_animais(animais,especie=None, faixa_etaria=None, porte=None, sexo=None):
    resultados = []
    for animal in animais:
        especie_animal = normalize(animal.get("Espécie", ""))
        faixa_etaria = normalize(animal.get("faixa", ""))
        porte_animal = normalize(animal.get("Porte", ""))
        sexo_animal =  normalize(animal.get("Sexo", ""))
        
        if especie and normalize(especie) != especie_animal:
            continue
        if faixa_etaria and normalize(faixa_etaria)!= faixa_etaria:
            continue
        if porte and normalize(porte) != porte_animal:
            continue
        if sexo and normalize (sexo) != sexo_animal:
            continue
        
        resultados.append(animal)
    return resultados

def agente_apresentar_animal(animal, sugestao=False):
    global apresentacoes_feitas
    texto = "\n".join([f"{k.capitalize()}: {v}" for k, v in animal.items() if k != "id"])

    tem_trauma = animal.get("CORAÇÃO COM BURAQUINHOS", "").strip().lower() == "sim"
    explicacao_trauma = (
        "Ah, e um detalhe importante: este é um animal com coração com buraquinhos 💔. "
        "Isso significa que ele passou por situações difíceis e carrega algumas marcas emocionais. "
        "Mas não se preocupe! O Lar Cecília Maria oferece todo o suporte e acompanhamento necessário para que ele possa confiar e amar novamente, no seu tempo. 🐾\n"
        if tem_trauma else ""
    )

    saudacao = (
        "Você é a Ceci 🐾, mascote da Organização sem fins lucrativos, Lar Cecília Maria. "
        "Apresente o animal com entusiasmo e carinho, usando saudações como 'Preparem os corações!'."
        if apresentacoes_feitas == 0 else
        "Você é a Ceci 🐾, mascote da Organização sem fins lucrativos, Lar Cecília Maria. "
        "Você JÁ se apresentou anteriormente, então agora vá direto ao ponto com empatia e serenidade."
    )

    contexto = (
        "Esse animal é uma sugestão, então apresente-o de forma gentil, explicando que pode não ser exatamente o que o adotante buscava, mas ainda assim pode encantá-lo."
        if sugestao else
        "Esse animal está dentro do perfil buscado, então apresente-o com alegria e carinho, como uma ótima escolha para o adotante."
    )

    prompt = f"""
    {saudacao}
    {contexto}
    {explicacao_trauma}

    Apresente em no máximo 5 parágrafos curtos. Seja objetiva, empática e acolhedora.
    Não repita ideias, não conte longas histórias do passado.
    Evite humanizações como 'filhote da casa' ou 'pessoa'.

    Ficha do animal:
    {texto}
    """

    apresentacoes_feitas += 1

    try:
        resposta = model.generate_content(prompt)
        if resposta.text:
            return resposta.text.strip()
        else:
            return "⚠️ Não consegui gerar uma apresentação da Ceci."

    except Exception as e:
        return f"❌ Erro ao gerar resposta com Gemini: {str(e)}"

def agente_agendar_visita(data, hora):
    endereco = "Lar Cecília Maria: Rua das Patinhas, 123 – Bairro Esperança – São Paulo/SP"
    prompt = f"""
        Você é Ceci 🐾, mascote do Lar Cecília Maria.
        Confirme com carinho o agendamento no dia {data} às {hora}.
        Finalize com o endereço: {endereco}.
    """
    resposta = model.generate_content(prompt)
    if resposta.text:
        return resposta.text.strip()
    else:
        return "⚠️ Ocorreu um problema ao confirmar o agendamento. Tente novamente mais tarde."
    
