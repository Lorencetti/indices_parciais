import csv

# --- Definir tamanhos fixos dos campos (em caracteres) ---
TAM_JEWELLERY_TYPE = 20
TAM_PRICE = 10
TAM_DATE = 25

# --- Função auxiliar: normaliza texto com espaços para tamanho fixo ---
def fix_text(text, size):
    text = str(text).strip()
    return text[:size].ljust(size)

# --- Função auxiliar: verifica se algum campo está vazio ---
def registro_completo(campos):
    return all(str(c).strip() != '' for c in campos)

# --- Criação dos arquivos binários ---
with open("jewelry.csv", "r", encoding="utf-8") as f_in, \
     open("joias.dat", "wb") as f_joias, \
     open("compras.dat", "wb") as f_compras:

    reader = csv.reader(f_in)
    for linha in reader:
        # Campos conforme ordem indicada
        try:
            Date, OrderID, ProductID, Quantity, CategoryID, JewelleryType, BrandID, Price, UserID, Gender, BoxColour, Metal, Gem = linha
        except ValueError:
            # Linha com campos faltando
            continue

        # Verificar se há dados incompletos
        if not registro_completo([ProductID, JewelleryType, Price, OrderID, Date, UserID]):
            continue

        # --- Criar registro para joias ---
        reg_joia = (
            fix_text(ProductID, 20) +               # ProductID como string de 20 chars
            fix_text(JewelleryType, TAM_JEWELLERY_TYPE) +
            fix_text(Price, TAM_PRICE) +
            "\n"
        )

        # --- Criar registro para compras ---
        reg_compra = (
            fix_text(OrderID, 20) +
            fix_text(ProductID, 20) +
            fix_text(Date, TAM_DATE) +
            fix_text(UserID, 20) +
            "\n"
        )

        # Gravar em modo binário
        f_joias.write(reg_joia.encode("utf-8"))
        f_compras.write(reg_compra.encode("utf-8"))

print("Arquivos 'joias.dat' e 'compras.dat' criados com sucesso!")
