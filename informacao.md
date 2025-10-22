# Trabalho de Organização de Arquivos – Loja de Joias Online

## 1. Arquivos Criados

No desenvolvimento do projeto, foram criados **dois arquivos binários principais**, a partir do dataset de compras da loja online:

1. **Arquivo de Joias (`joias.dat`)**  
   - Contém informações sobre os produtos cadastrados na loja.  
   - Campos incluídos:
     - `ProductID` (chave única)
     - `JewelleryType`
     - `Price`
   - Finalidade: servir como referência para consultar tipos e preços das joias.

2. **Arquivo de Compras (`compras.dat`)**  
   - Contém informações sobre as compras realizadas pelos usuários.  
   - Campos incluídos:
     - `OrderID`
     - `ProductID` (chave única)
     - `Date`
     - `UserID`
   - Finalidade: registrar as compras feitas pelos usuários e permitir consultas como tipo de joia mais vendido ou usuário que mais gastou.

---

## 2. Ordenação e Busca Binária

### Ordenação
- Ambos os arquivos foram **ordenados pelo campo `ProductID`**, que é o identificador único do produto.  
- A ordenação foi feita de forma **sequencial**, garantindo que a leitura e a inserção de novos registros pudessem manter o arquivo organizado.  
- Sempre que um novo registro era inserido ou removido, o arquivo era reescrito mantendo a **ordem crescente de `ProductID`**.

### Busca Binária
- Cada arquivo possui um **índice parcial** baseado no `ProductID`.  
- O índice armazena a **posição de registros a cada 10 entradas**, permitindo buscar rapidamente o bloco aproximado do registro desejado.  
- Para consultar um registro:
  1. Realiza-se uma **pesquisa binária no índice** para encontrar o bloco correto.
  2. Em seguida, lê-se **apenas os registros do bloco correspondente** no arquivo de dados (10 registros por vez), evitando carregar o arquivo inteiro na memória.  

---

## 3. Estrutura dos Arquivos

### 3.1 Arquivo de Joias (`joias.dat`)

| Campo | Tipo | Tamanho | Descrição |
|-------|------|---------|-----------|
| `ProductID` | Texto | 20 | Identificador único do produto |
| `JewelleryType` | Texto | 20 | Tipo de joia (ex: Pendant, Ring) |
| `Price` | Texto | 10 | Preço do produto em dólares |

### 3.2 Arquivo de Compras (`compras.dat`)

| Campo | Tipo | Tamanho | Descrição |
|-------|------|---------|-----------|
| `OrderID` | Texto | 20 | Identificador único do pedido |
| `ProductID` | Texto | 20 | Identificador do produto comprado |
| `Date` | Texto | 25 | Data e hora da compra |
| `UserID` | Texto | 20 | Identificador do usuário que realizou a compra |

---

## 4. Estrutura Original do Dataset

O dataset original contém os seguintes campos:

| Campo | Descrição |
|-------|-----------|
| `Date` | Data e hora do pedido |
| `OrderID` | Identificador do pedido |
| `ProductID` | Identificador do produto adquirido |
| `Quantity` | Quantidade de SKU1 no pedido |
| `CategoryID` | Identificador da categoria do produto |
| `AliasCategory` | Nome da categoria |
| `BrandID` | Identificação da marca |
| `Price` | Preço do produto em U$D |
| `UserID` | Identificador do usuário |
| `Gender` | Gênero do produto |
| `BoxColour` | Cor da caixa do produto |
| `Metal` | Material da joia |
| `Gem` | Pedra preciosa da joia |

> Nota: Para a construção dos arquivos binários, selecionamos apenas os campos relevantes para cada arquivo, garantindo eficiência na consulta e operações de ordenação e inserção.

---

## 5. Consultas Realizadas

O programa implementa consultas e operações para responder a três perguntas principais:

1. **Qual é o tipo de joia mais vendido?**  
   - Analisa o arquivo de compras e cruza com o arquivo de joias para contar a quantidade de vendas por tipo (`JewelleryType`).  
   - Retorna o tipo de joia com o maior número de vendas.

2. **Qual é o produto mais caro cadastrado nas joias?**  
   - Percorre o arquivo de joias e identifica o produto (`ProductID`) com o maior preço (`Price`).

3. **Qual é o usuário que mais gastou com joias?**  
   - Cria um mapeamento de preços por `ProductID` a partir do arquivo de joias.  
   - Soma o total gasto por cada usuário a partir do arquivo de compras.  
   - Retorna o `UserID` do usuário que mais gastou.

---