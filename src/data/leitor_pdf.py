#Este script tem como objetivo ler o PDF que descreve as políticas da loja.

import re
from pathlib import Path
from pypdf import PdfReader

#Def. de caminhos e constantes
RAIZ_PROJETO = Path(__file__).resolve().parents[2]
CAMINHO_PDF = RAIZ_PROJETO/"data"/"politicas_da_loja.pdf"

#Header presente em todas as paginas
CABECALHO = "Empório da Música Manual de Políticas e Procedimentos"

def carregar_arquivo():
    arquivo = PdfReader(CAMINHO_PDF)

    if not CAMINHO_PDF.exists():
        raise FileNotFoundError(f"O arquivo nao foi encontrado. Verifique se o PDF encontra-se em: {CAMINHO_PDF}")

    textos = []
    for texto in arquivo.pages:
        textos.append(texto.extract_text(extraction_mode="layout"))
    texto_completo = "\n".join(textos)

    #Remove rodapés e cabeçalhos, e formatar o texto
    texto_formatado = []
    for frase in texto_completo.splitlines():
        frase = frase.strip()

        #Reduz espaços repetidos e descarta o header
        frase = re.sub(r"\s+", " ", frase)
        if frase.startswith("Página ") or frase == CABECALHO:
            continue

        #Evita várias linhas vazias seguidas
        if not frase and texto_formatado and not texto_formatado[-1]:
            continue

        texto_formatado.append(frase)

    return "\n".join(texto_formatado)

if __name__=="__main__":
    print(carregar_arquivo())