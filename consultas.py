import os
from collections import defaultdict

# ==============================
# CONFIGURAÇÕES
# ==============================
TAM_PRODUCT_ID = 20
TAM_JEWELLERY_TYPE = 20
TAM_PRICE = 10
TAM_ORDER_ID = 20
TAM_DATE = 25
TAM_USER_ID = 20

TAM_REG_JOIAS = TAM_PRODUCT_ID + TAM_JEWELLERY_TYPE + TAM_PRICE + 1
TAM_REG_COMPRAS = TAM_ORDER_ID + TAM_PRODUCT_ID + TAM_DATE + TAM_USER_ID + 1

BLOCO_INDICE = 10  # índice parcial a cada 10 registros


# ==============================
# FUNÇÕES AUXILIARES
# ==============================
def fix_text(text, size):
    return str(text).strip()[:size].ljust(size)


def parse_joia(line):
    return {
        "ProductID": line[0:TAM_PRODUCT_ID].strip(),
        "JewelleryType": line[TAM_PRODUCT_ID:TAM_PRODUCT_ID + TAM_JEWELLERY_TYPE].strip(),
        "Price": line[TAM_PRODUCT_ID + TAM_JEWELLERY_TYPE:TAM_PRODUCT_ID + TAM_JEWELLERY_TYPE + TAM_PRICE].strip()
    }


def parse_compra(line):
    return {
        "OrderID": line[0:TAM_ORDER_ID].strip(),
        "ProductID": line[TAM_ORDER_ID:TAM_ORDER_ID + TAM_PRODUCT_ID].strip(),
        "Date": line[TAM_ORDER_ID + TAM_PRODUCT_ID:TAM_ORDER_ID + TAM_PRODUCT_ID + TAM_DATE].strip(),
        "UserID": line[TAM_ORDER_ID + TAM_PRODUCT_ID + TAM_DATE:TAM_ORDER_ID + TAM_PRODUCT_ID + TAM_DATE + TAM_USER_ID].strip()
    }


# ==============================
# CRIAÇÃO E LEITURA DE ÍNDICE
# ==============================
def criar_indice(nome_dados, nome_indice, tam_chave):
    """Cria índice parcial baseado no campo ProductID."""
    if not os.path.exists(nome_dados):
        print(f"Arquivo {nome_dados} não encontrado.")
        return

    tam_reg = TAM_REG_JOIAS if "joias" in nome_dados else TAM_REG_COMPRAS
    with open(nome_dados, "rb") as f_dados, open(nome_indice, "wb") as f_idx:
        pos = 0
        contador = 0
        while True:
            linha = f_dados.read(tam_reg)
            if not linha:
                break
            if contador % BLOCO_INDICE == 0:
                if "joias" in nome_dados:
                    chave = linha.decode("utf-8")[0:TAM_PRODUCT_ID].strip()
                else:
                    chave = linha.decode("utf-8")[TAM_ORDER_ID:TAM_ORDER_ID + TAM_PRODUCT_ID].strip()
                if chave:
                    f_idx.write(f"{fix_text(chave, tam_chave)}{str(pos).zfill(10)}\n".encode("utf-8"))
            contador += 1
            pos += tam_reg
    print(f"Índice '{nome_indice}' atualizado.")


def carregar_indice(nome_indice):
    """Carrega índice parcial (chave, posição)."""
    indices = []
    if not os.path.exists(nome_indice):
        return indices
    with open(nome_indice, "r", encoding="utf-8") as f:
        for line in f:
            chave = line[:-10].strip()
            pos = int(line[-10:].strip())
            indices.append((chave, pos))
    return indices


# ==============================
# BUSCA USANDO ÍNDICE PARCIAL
# ==============================
def pesquisa_binaria_indice(chave, nome_indice):
    """Pesquisa binária no índice para achar o intervalo correto (posição do registro ou início da faixa mais próxima)."""
    indices = carregar_indice(nome_indice)
    if not indices:
        return 0

    inicio, fim = 0, len(indices) - 1
    posicao = 0  # posição padrão caso não encontre exata

    while inicio <= fim:
        meio = (inicio + fim) // 2
        chave_meio = str(indices[meio][0]).strip()
        chave_busca = str(chave).strip()

        if chave_meio == chave_busca:
            # Achou a chave exata
            return indices[meio][1]
        elif chave_meio < chave_busca:
            posicao = indices[meio][1]  # salva posição válida mais próxima (intervalo certo)
            inicio = meio + 1
        else:
            fim = meio - 1

    # Retorna posição mais próxima para começar a varredura
    return posicao



def consultar_por_productid(nome_dados, nome_indice, chave, tipo="joia", silent=False):
    """
    Consulta por ProductID usando índice parcial.
    Agora garante:
    - Sincronização de escrita antes da leitura (fsync)
    - Comparação com padding tratado (strip)
    - Busca precisa e sem falha em registros recentes
    """
    tam_reg = TAM_REG_JOIAS if tipo == "joia" else TAM_REG_COMPRAS
    pos_inicial = pesquisa_binaria_indice(chave, nome_indice)

    try:
        with open(nome_dados, "rb+") as f_sync:
            f_sync.flush()
            os.fsync(f_sync.fileno())
    except Exception:
        pass  # se não for possível sincronizar, ignora (arquivo só leitura)

    with open(nome_dados, "rb") as f:
        f.seek(pos_inicial)
        for _ in range(BLOCO_INDICE):
            linha = f.read(tam_reg)
            if not linha:
                break

            # Converte o registro binário
            reg = parse_joia(linha.decode("utf-8")) if tipo == "joia" else parse_compra(linha.decode("utf-8"))

            # Remove espaços extras antes da comparação
            id_prod = reg["ProductID"].strip()
            chave_limpa = chave.strip()

            # Comparação segura
            if id_prod == chave_limpa:
                if not silent:
                    print(f"Registro encontrado: {reg}")
                return reg

            # Como está ordenado, pode parar se passou da chave
            if id_prod > chave_limpa:
                break

    if not silent:
        print("Registro não encontrado.")
    return None


# ==============================
# INSERÇÃO E REMOÇÃO ORDENADAS
# ==============================
def inserir_registro(nome_dados, nome_indice, novo, tipo="joia"):
    """Insere de forma ordenada pelo ProductID."""
    tam_reg = TAM_REG_JOIAS if tipo == "joia" else TAM_REG_COMPRAS
    registros = []

    with open(nome_dados, "rb") as f:
        while True:
            linha = f.read(tam_reg)
            if not linha:
                break
            registros.append(parse_joia(linha.decode("utf-8")) if tipo == "joia" else parse_compra(linha.decode("utf-8")))

    registros.append(novo)
    registros = sorted(registros, key=lambda x: x["ProductID"])

    with open(nome_dados, "wb") as f:
        for r in registros:
            if tipo == "joia":
                linha = fix_text(r["ProductID"], TAM_PRODUCT_ID) + \
                        fix_text(r["JewelleryType"], TAM_JEWELLERY_TYPE) + \
                        fix_text(r["Price"], TAM_PRICE) + "\n"
            else:
                linha = fix_text(r["OrderID"], TAM_ORDER_ID) + \
                        fix_text(r["ProductID"], TAM_PRODUCT_ID) + \
                        fix_text(r["Date"], TAM_DATE) + \
                        fix_text(r["UserID"], TAM_USER_ID) + "\n"
            f.write(linha.encode("utf-8"))

    criar_indice(nome_dados, nome_indice, TAM_PRODUCT_ID)
    print("Registro inserido e arquivo reordenado.")


def remover_registro(nome_dados, nome_indice, chave, tipo="joia"):
    """Remove registro com base no ProductID e mantém arquivo ordenado."""
    tam_reg = TAM_REG_JOIAS if tipo == "joia" else TAM_REG_COMPRAS
    registros = []

    with open(nome_dados, "rb") as f:
        while True:
            linha = f.read(tam_reg)
            if not linha:
                break
            reg = parse_joia(linha.decode("utf-8")) if tipo == "joia" else parse_compra(linha.decode("utf-8"))
            if reg["ProductID"] != chave:
                registros.append(reg)

    with open(nome_dados, "wb") as f:
        for r in registros:
            if tipo == "joia":
                linha = fix_text(r["ProductID"], TAM_PRODUCT_ID) + \
                        fix_text(r["JewelleryType"], TAM_JEWELLERY_TYPE) + \
                        fix_text(r["Price"], TAM_PRICE) + "\n"
            else:
                linha = fix_text(r["OrderID"], TAM_ORDER_ID) + \
                        fix_text(r["ProductID"], TAM_PRODUCT_ID) + \
                        fix_text(r["Date"], TAM_DATE) + \
                        fix_text(r["UserID"], TAM_USER_ID) + "\n"
            f.write(linha.encode("utf-8"))

    criar_indice(nome_dados, nome_indice, TAM_PRODUCT_ID)
    print("Registro removido e índice recriado.")


# ==============================
# CONSULTAS (3 PERGUNTAS)
# ==============================
def tipo_mais_vendido():
    """Determina o tipo de joia mais vendido, consultando dados de joias e compras."""
    tipos_por_produto = {}

    if not os.path.exists("joias.dat"):
        print("Arquivo joias.dat não encontrado.")
        return
    if not os.path.exists("compras.dat"):
        print("Arquivo compras.dat não encontrado.")
        return

    # Passo 1: Mapeia tipos das joias (ProductID → JewelleryType)
    tam_joia = TAM_REG_JOIAS
    tamanho_joias = os.path.getsize("joias.dat")
    total_joias = tamanho_joias // tam_joia

    with open("joias.dat", "rb") as f_joias:
        for i in range(total_joias):
            f_joias.seek(i * tam_joia)
            linha = f_joias.read(tam_joia)
            if not linha.strip():
                continue
            reg = parse_joia(linha.decode("utf-8"))
            tipos_por_produto[reg["ProductID"]] = reg["JewelleryType"]

    # Passo 2: Conta as vendas por tipo de joia
    vendas_por_tipo = defaultdict(int)
    tam_compra = TAM_REG_COMPRAS
    tamanho_compras = os.path.getsize("compras.dat")
    total_compras = tamanho_compras // tam_compra

    with open("compras.dat", "rb") as f_compras:
        for i in range(total_compras):
            f_compras.seek(i * tam_compra)
            linha = f_compras.read(tam_compra)
            if not linha.strip():
                continue
            compra = parse_compra(linha.decode("utf-8"))
            produto = compra["ProductID"]
            if produto in tipos_por_produto:
                tipo = tipos_por_produto[produto]
                vendas_por_tipo[tipo] += 1

    # Passo 3: Mostra o resultado
    if vendas_por_tipo:
        tipo_top = max(vendas_por_tipo, key=vendas_por_tipo.get)
        print(f" Tipo de joia mais vendido: {tipo_top} ({vendas_por_tipo[tipo_top]} vendas)")
    else:
        print("Nenhuma venda registrada.")




def produto_mais_caro():
    """Produto mais caro."""
    tam_reg = TAM_REG_JOIAS
    mais_caro = None
    maior_preco = 0

    with open("joias.dat", "rb") as f:
        while True:
            linha = f.read(tam_reg)
            if not linha:
                break
            reg = parse_joia(linha.decode("utf-8"))
            try:
                preco = float(reg["Price"])
                if preco > maior_preco:
                    maior_preco = preco
                    mais_caro = reg
            except:
                pass

    if mais_caro:
        print(f" Produto mais caro: {mais_caro['ProductID']} - {mais_caro['JewelleryType']} (${maior_preco})")
    else:
        print("Nenhum produto encontrado.")


def usuario_que_mais_gastou():
    """Determina o usuário que mais gastou com base nas compras e nos preços das joias."""
    # Passo 1: Mapeia preços das joias (ProductID → Price)
    precos_por_produto = {}

    if not os.path.exists("joias.dat"):
        print(" Arquivo de joias.dat não encontrado.")
        return
    if not os.path.exists("compras.dat"):
        print(" Arquivo de compras.dat não encontrado.")
        return

    tam_joia = TAM_REG_JOIAS
    tamanho_joias = os.path.getsize("joias.dat")
    total_joias = tamanho_joias // tam_joia

    with open("joias.dat", "rb") as f_joias:
        for i in range(total_joias):
            f_joias.seek(i * tam_joia)
            linha = f_joias.read(tam_joia)
            if not linha.strip():
                continue
            reg = parse_joia(linha.decode("utf-8"))
            try:
                precos_por_produto[reg["ProductID"]] = float(reg["Price"])
            except ValueError:
                continue

    # Passo 2: Soma gastos por usuário (usando o índice de compras para buscar blocos)
    gastos_por_usuario = defaultdict(float)
    tam_compra = TAM_REG_COMPRAS
    tamanho_compras = os.path.getsize("compras.dat")
    total_compras = tamanho_compras // tam_compra

    with open("compras.dat", "rb") as f_compras:
        for i in range(total_compras):
            f_compras.seek(i * tam_compra)
            linha = f_compras.read(tam_compra)
            if not linha.strip():
                continue
            compra = parse_compra(linha.decode("utf-8"))
            produto = compra["ProductID"]
            usuario = compra["UserID"]
            if produto in precos_por_produto:
                gastos_por_usuario[usuario] += precos_por_produto[produto]

    # Passo 3: Exibe o resultado
    if gastos_por_usuario:
        usuario_top = max(gastos_por_usuario, key=gastos_por_usuario.get)
        total_gasto = gastos_por_usuario[usuario_top]
        print(f" Usuário que mais gastou: {usuario_top} (${total_gasto:.2f})")
    else:
        print("Nenhuma compra registrada.")




# ==============================
# MENU
# ==============================
def menu():
    criar_indice("joias.dat", "indice_joias.idx", TAM_PRODUCT_ID)
    criar_indice("compras.dat", "indice_compras.idx", TAM_PRODUCT_ID)

    while True:
        print("\n========== MENU ==========")
        print("1 - Consultar joia por ProductID")
        print("2 - Inserir joia (ordenado)")
        print("3 - Remover joia")
        print("4 - Consultar compra por ProductID")
        print("5 - Inserir compra (ordenado)")
        print("6 - Remover compra")
        print("7 - Tipo de joia mais vendido")
        print("8 - Produto mais caro")
        print("9 - Usuário que mais gastou")
        print("0 - Sair")

        op = input("Escolha: ")
        if op == "1":
            chave = input("ProductID: ")
            consultar_por_productid("joias.dat", "indice_joias.idx", chave, "joia")
        elif op == "2":
            novo = {
                "ProductID": input("ProductID: "),
                "JewelleryType": input("JewelleryType: "),
                "Price": input("Price: ")
            }
            inserir_registro("joias.dat", "indice_joias.idx", novo, "joia")
        elif op == "3":
            chave = input("ProductID a remover: ")
            remover_registro("joias.dat", "indice_joias.idx", chave, "joia")
        elif op == "4":
            chave = input("ProductID: ")
            consultar_por_productid("compras.dat", "indice_compras.idx", chave, "compra")
        elif op == "5":
            novo = {
                "OrderID": input("OrderID: "),
                "ProductID": input("ProductID: "),
                "Date": input("Date: "),
                "UserID": input("UserID: ")
            }
            inserir_registro("compras.dat", "indice_compras.idx", novo, "compra")
        elif op == "6":
            chave = input("ProductID a remover: ")
            remover_registro("compras.dat", "indice_compras.idx", chave, "compra")
        elif op == "7":
            tipo_mais_vendido()
        elif op == "8":
            produto_mais_caro()
        elif op == "9":
            usuario_que_mais_gastou()
        elif op == "0":
            print("Encerrando...")
            break
        else:
            print(" Opção inválida.")


if __name__ == "__main__":
    menu()
