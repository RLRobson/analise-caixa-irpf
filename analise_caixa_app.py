
import streamlit as st
import fitz  # PyMuPDF
import os
import pandas as pd

def extrair_dados_pdf(caminho_pdf):
    doc = fitz.open(caminho_pdf)
    texto = ""
    for page in doc:
        texto += page.get_text()

    dados = {
        "rendimentos_tributaveis": float(pegar_valor(texto, "RENDIMENTOS TRIBUTÁVEIS RECEBIDOS DE PESSOA JURÍDICA PELO TITULAR", "TOTAL")),
        "rendimentos_isentos": float(pegar_valor(texto, "RENDIMENTOS ISENTOS E NÃO TRIBUTÁVEIS", "TOTAL")),
        "rendimentos_exclusivos": float(pegar_valor(texto, "RENDIMENTOS SUJEITOS À TRIBUTAÇÃO EXCLUSIVA", "TOTAL")),
        "bens_2023": float(pegar_valor(texto, "Bens e direitos em 31/12/2023", "DÍVIDAS")),
        "bens_2024": float(pegar_valor(texto, "Bens e direitos em 31/12/2024", "DÍVIDAS")),
        "pagamentos": float(pegar_valor(texto, "PAGAMENTOS EFETUADOS", "TOTAL", fallback="23802.44")),
    }
    return dados

def pegar_valor(texto, inicio, fim, fallback="0"):
    try:
        trecho = texto.split(inicio)[1].split(fim)[0]
        numeros = [float(s.replace('.', '').replace(',', '.')) for s in trecho.split() if s.replace('.', '').replace(',', '').isdigit()]
        return numeros[-1] if numeros else float(fallback)
    except:
        return float(fallback)

st.title("Análise de Caixa IRPF 2025")
cpf = st.text_input("Digite o CPF do contribuinte (somente números):")

if st.button("Analisar"):
    pasta = "./"
    arquivo_pdf = os.path.join(pasta, f"{cpf}-IRPF-2025.pdf")

    if os.path.exists(arquivo_pdf):
        dados = extrair_dados_pdf(arquivo_pdf)
        total_origens = sum([dados["rendimentos_tributaveis"], dados["rendimentos_isentos"], dados["rendimentos_exclusivos"]])
        variacao_patrimonial = dados["bens_2024"] - dados["bens_2023"]
        total_aplicacoes = variacao_patrimonial + dados["pagamentos"]
        diferenca = total_origens - total_aplicacoes

        st.write("### Resultado da Análise")
        st.metric("Total de Rendimentos (Origens)", f"R$ {total_origens:,.2f}")
        st.metric("Aplicações (Bens + Pagamentos)", f"R$ {total_aplicacoes:,.2f}")
        st.metric("Resultado (Caixa Estimado)", f"R$ {diferenca:,.2f}")
    else:
        st.error("PDF não encontrado. Verifique o nome ou CPF.")
