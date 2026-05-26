import os
import requests

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from google import genai
from google.genai import types

from config import SYSTEM_INSTRUCTION

# ======================================
# CONFIG
# ======================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(
    api_key=GEMINI_API_KEY
)

app = Flask(__name__)

CORS(app)

# ======================================
# GEMINI
# ======================================

def ask_gemini(prompt):

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",

            contents=prompt,

            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=1.2
            )
        )

        return response.text

    except Exception as e:

        print(e)

        return "Erro ao gerar resposta."

# ======================================
# BUSCA DE PRODUTOS
# ======================================

def gerar_links(marca, estilo):

    produtos = [

        {
            "titulo": f"Camiseta {marca}",
            "link": f"https://www.google.com/search?q={marca}+camiseta+{estilo}"
        },

        {
            "titulo": f"Calça {marca}",
            "link": f"https://www.google.com/search?q={marca}+calça+{estilo}"
        },

        {
            "titulo": f"Tênis {marca}",
            "link": f"https://www.google.com/search?q={marca}+tênis+{estilo}"
        }

    ]

    return produtos

# ======================================
# HOME
# ======================================

@app.route("/")
def home():

    return jsonify({
        "status": "online",
        "message": "DripAI funcionando 🔥"
    })

# ======================================
# GERAR OUTFIT
# ======================================

@app.route("/outfit", methods=["POST"])
def outfit():

    try:

        data = request.get_json()

        estilo = data.get("estilo")
        ocasiao = data.get("ocasiao")
        orcamento = data.get("orcamento")
        marca = data.get("marca")
        genero = data.get("genero")

        if not estilo or not ocasiao:

            return jsonify({
                "erro": "Preencha os campos."
            }), 400

        # ==================================
        # PROMPT
        # ==================================

        prompt = f"""
        Monte um outfit moderno.

        Estilo:
        {estilo}

        Ocasião:
        {ocasiao}

        Orçamento:
        R${orcamento}

        Marca:
        {marca}

        Gênero:
        {genero}

        Seja moderno e estiloso.
        """

        resposta_ia = ask_gemini(prompt)

        # ==================================
        # LINKS
        # ==================================

        produtos = gerar_links(
            marca,
            estilo
        )

        return jsonify({

            "status": "success",

            "outfit": resposta_ia,

            "produtos": produtos

        })

    except Exception as e:

        print(e)

        return jsonify({
            "erro": "Erro interno no servidor."
        }), 500

# ======================================
# START
# ======================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )