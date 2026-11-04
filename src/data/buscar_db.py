#Este script tem como objetivo fazer a busca de produtos e fornecer informações aos clientes sobre eles.
import difflib
import json
import re
import pandas as pd
from unidecode import unidecode
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
DATA_DIR = RAIZ_PROJETO / "data"
PREFIXO = "desafio_tecnico_ai_eng - "

MAX_RESULTADOS = 10

#Tradução dos status dos pedidos para evitar ambiguidade quando verificado pelo agente.
STATUS_PEDIDO = {
    "pending": "aguardando pagamento",
    "confirmed": "pagamento confirmado, em preparação",
    "shipped": "enviado",
    "delivered": "entregue",
    "cancelled": "cancelado",
}

#Lê o arquivo CSV e retorna um erro caso o arquivo não exista.
def ler_csv(nome: str) -> pd.DataFrame:
    caminho = DATA_DIR / f"{PREFIXO}{nome}.csv"
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    return pd.read_csv(caminho)

def forma_pagamento(codigo: str) -> str:
    if codigo.startswith("credit_"):
        return f"cartão de crédito em {codigo.removeprefix('credit_')}"
    return {"pix": "PIX", "debit": "cartão de débito", "boleto": "boleto bancário"}.get(codigo, codigo)

def valor(dado):
    """Converte NaN em None"""
    return None if pd.isna(dado) else dado

#Carrega os dados
categorias = ler_csv("categories")
clientes = ler_csv("customers")
pedidos = ler_csv("orders")
itens = ler_csv("order_items")
promocoes = ler_csv("promotions")
produtos = ler_csv("products").merge(
    categorias[["category_id", "name"]].rename(columns={"name": "categoria"}),
    on="category_id",
    how="left",
)

#Ignora a diferença entre minúsculas e maiúsculas e também os acentos
produtos["nome_busca"] = produtos["name"].map(lambda t: unidecode(t).lower())
produtos["categoria_busca"] = produtos["categoria"].map(lambda t: unidecode(t).lower())

#Considera as promoções de acordo com a política e os dados da loja
promo_ativa = (
    promocoes[promocoes["is_active"] == 1]
    .sort_values("discount_percent", ascending=False)
    .drop_duplicates("product_id")
    .set_index("product_id")
)

#Apresenta as informações do produto referentes à disponibilidade
def informacao_produto(linha: pd.Series) -> dict:
    if linha["status"] == "discontinued":
        disponibilidade = "descontinuado (não faz mais parte do catálogo)"
    elif linha["status"] == "coming_soon":
        disponibilidade = "em breve (ainda não disponível para venda)"
    elif linha["stock_quantity"] > 0:
        disponibilidade = "disponível"
    else:
        disponibilidade = "esgotado no momento"

    produto = {
        "nome": linha["name"],
        "categoria": linha["categoria"],
        "preco_original": float(linha["price_brl"]),
        "disponibilidade": disponibilidade,
        # O nome e as especificações são a fonte confiável: algumas descrições
        # do cadastro contradizem o próprio produto.
        "especificacoes": json.loads(linha["specs"]),
    }

    if linha["product_id"] in promo_ativa.index:
        promo = promo_ativa.loc[linha["product_id"]]
        desconto = int(promo["discount_percent"])
        produto["promocao"] = {
            "nome": promo["description"],
            "desconto_percentual": desconto,
            "preco_promocional": round(float(linha["price_brl"]) * (1 - desconto / 100), 2),
        }
    return produto

#Busca o produto no banco de dados da loja (args: nome, categoria e preço)
def buscar_produtos(termo: str = "", categoria: str = "", preco_maximo: float = 0) -> list[dict]:
    if termo:
        resultado = produtos
    else:
        resultado = produtos[produtos["status"] != "discontinued"]

    if categoria:
        cat = unidecode(categoria).lower().strip()
        # Encontra produtos no singular e no plural
        singular_plural = {cat, cat.rstrip("s")}
        if cat.endswith("ao"):
            singular_plural.add(cat[:-2] + "oes")
        padrao = "|".join(re.escape(v) for v in singular_plural)
        resultado = resultado[resultado["categoria_busca"].str.contains(padrao)]

    if preco_maximo and preco_maximo > 0:
        resultado = resultado[resultado["price_brl"] <= preco_maximo]

    if termo:
        busca = unidecode(termo).lower().strip()
        nomes = resultado["nome_busca"]

        # Ignora o espaço entre duas palavras que pertencem a um produto
        contem_termo = nomes.str.replace(" ", "").str.contains(busca.replace(" ", ""), regex=False)

        # Verifica se todas as palavras digitadas pertencem a um mesmo produto
        contem_palavras = pd.Series(True, index=nomes.index)
        for palavra in busca.split():
            nomes_com_a_palavra = nomes.str.contains(palavra, regex=False)
            contem_palavras = contem_palavras & nomes_com_a_palavra

        encontrados = resultado[contem_termo | contem_palavras]

        # Busca por produtos que possuam nomes semelhantes ao termo de busca. Útil contra erros de digitação do usuário
        if encontrados.empty:
            parecidos = difflib.get_close_matches(
                busca, resultado["nome_busca"].tolist(), n=3, cutoff=0.5
            )
            encontrados = resultado[resultado["nome_busca"].isin(parecidos)]
        resultado = encontrados

    resultado = resultado.sort_values("price_brl").head(MAX_RESULTADOS)

    lista_produtos = []
    for _, linha in resultado.iterrows():
        lista_produtos.append(informacao_produto(linha))
    return lista_produtos

#Consulta o status de um pedido (args: número e e-mail).
#Para a segurança dos clientes, o pedido só deve ser consultado a partir de
#um endereço de e-mail
def consultar_pedido(numero_pedido: int, email: str) -> dict:

    pedido = pedidos[pedidos["order_id"] == int(numero_pedido)]
    cliente = clientes[clientes["customer_id"].isin(pedido["customer_id"])]

    # Configura a mensagem para o caso de o pedido e o e-mail estarem incoerentes.
    if pedido.empty or cliente["email"].iloc[0].lower() != email.lower().strip():
        return {
            "erro": "Não foi possível localizar um pedido com esse número e e-mail. "
            "Peça ao cliente para conferir os dados."
        }

    pedido = pedido.iloc[0]
    itens_pedido = itens[itens["order_id"] == pedido["order_id"]].merge(produtos, on="product_id")

    return {
        "numero_pedido": int(pedido["order_id"]),
        "data_pedido": pedido["order_date"],
        "status": STATUS_PEDIDO.get(pedido["status"], pedido["status"]),
        "total": float(pedido["total_brl"]),
        "forma_pagamento": forma_pagamento(pedido["payment_method"]),
        "codigo_rastreio": valor(pedido["tracking_code"]),
        "previsao_entrega": valor(pedido["estimated_delivery"]),
        "observacao": valor(pedido["notes"]),
        "itens": [
            {"produto": item["name"], "quantidade": int(item["quantity"])}
            for _, item in itens_pedido.iterrows()
        ],
    }

#Lista de produtos com promoções ativas e descontos
def listar_promocoes_ativas() -> list[dict]:

    #Lista os produtos em promoção
    em_promocao = produtos[
        produtos["product_id"].isin(promo_ativa.index)
        & (produtos["status"] != "discontinued")
    ]
    return [informacao_produto(linha) for _, linha in em_promocao.iterrows()]