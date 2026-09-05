# Etapa 07: Database - Amazon DynamoDB

## Objetivo
Criar uma tabela no Amazon DynamoDB para armazenar a contagem de visitantes do site, aplicando o princípio do menor privilégio nas permissões IAM.

## Status
✅ Concluído

## Recursos Utilizados
- Amazon DynamoDB (NoSQL)
- AWS IAM (Identity and Access Management)
- AWS CLI

---

## 📋 Passos Realizados

### 1. Acessar o DynamoDB

1. No console AWS, pesquisar por **"DynamoDB"**
2. Clicar no resultado para abrir o serviço

---

### 2. Criar a Tabela

**Configurações:**

| Campo | Valor |
|-------|-------|
| **Table name** | `VisitorsCount` |
| **Partition key** | `id` |
| **Partition key type** | `String` |
| **Table settings** | Padrão (on-demand) |

**Motivo das escolhas:**
- **Nome:** `VisitorsCount` → Nome descritivo para a tabela de contagem
- **Partition key:** `id` → Chave primária para identificar o item
- **Tipo:** `String` → O valor será `"visitor_count"`
- **On-demand:** → Pagamento por uso, ideal para projetos de baixo tráfego

---

### 3. Inserir o Item Inicial

Após criar a tabela, inserir o primeiro registro:

| Campo | Valor |
|-------|-------|
| `id` | `visitor_count` |
| `visit_count` | `0` |

**Como fazer:**
1. Clicar no nome da tabela `VisitorsCount`
2. Ir na aba **"Explore items"**
3. Clicar em **"Create item"**
4. Adicionar os campos e valores
5. Clicar em **"Create item"**

---

### 4. Configurar Permissões IAM (Menor Privilégio)

Para garantir a segurança, foi criada uma política IAM com apenas as permissões necessárias.

**Política IAM:** `s3-resume-bucket-access`

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::cloud-resume-challenge-rafael-2026",
                "arn:aws:s3:::cloud-resume-challenge-rafael-2026/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:UpdateItem"
            ],
            "Resource": "arn:aws:dynamodb:us-east-1:696537703431:table/VisitorsCount"
        }
    ]
}
```

**Permissões concedidas:**

| Serviço | Ação | Motivo |
|---------|------|--------|
| S3 | `s3:ListBucket` | Necessário para `aws s3 sync` |
| S3 | `s3:GetObject` | Ler arquivos do bucket |
| S3 | `s3:PutObject` | Enviar arquivos para o bucket |
| S3 | `s3:DeleteObject` | Remover arquivos do bucket |
| DynamoDB | `dynamodb:GetItem` | Ler a contagem de visitantes |
| DynamoDB | `dynamodb:UpdateItem` | Incrementar a contagem de visitantes |

**Permissões NÃO concedidas (por segurança):**
- ❌ `dynamodb:ListTables` → Apenas para testes manuais
- ❌ `dynamodb:PutItem` → Item já foi criado manualmente
- ❌ `dynamodb:DeleteItem` → Não há necessidade de excluir itens
- ❌ `dynamodb:CreateTable` → Tabela já foi criada

---

### 5. Testar a Conexão

**Comando para verificar o item:**

```bash
aws dynamodb get-item \
    --table-name VisitorsCount \
    --key '{"id": {"S": "visitor_count"}}' \
    --region us-east-1
```

**Resultado esperado:**
```json
{
    "Item": {
        "id": {"S": "visitor_count"},
        "visit_count": {"N": "0"}
    }
}
```

**Comando para incrementar o contador (teste):**

```bash
aws dynamodb update-item \
    --table-name VisitorsCount \
    --key '{"id": {"S": "visitor_count"}}' \
    --update-expression "ADD visit_count :inc" \
    --expression-attribute-values '{":inc": {"N": "1"}}' \
    --return-values UPDATED_NEW \
    --region us-east-1
```

**Resultado esperado:**
```json
{
    "Attributes": {
        "visit_count": {"N": "1"},
        "id": {"S": "visitor_count"}
    }
}
```

---

## 📊 Estrutura da Tabela

| Atributo | Tipo | Descrição | Valor inicial |
|----------|------|-----------|---------------|
| `id` | String (Partition Key) | Identificador único | `"visitor_count"` |
| `visit_count` | Number | Contagem de visitantes | `0` |

---

## 💰 Custo

- **Modo:** On-demand (pagamento por requisição)
- **Camada gratuita:** 25 GB de armazenamento + 2,5 milhões de leituras/mês
- **Custo estimado para o projeto:** ~US$ 0,00 (dentro da camada gratuita)

---

## 🔍 Verificação

- [x] Tabela `VisitorsCount` criada
- [x] Item `visitor_count` com `visit_count = 0` inserido
- [x] Tabela configurada no modo on-demand
- [x] Política IAM atualizada com permissões mínimas
- [x] Teste de `GetItem` funcionando
- [x] Teste de `UpdateItem` funcionando

---

## 🐛 Problemas e Soluções

### Problema: AccessDenied ao testar o DynamoDB

**Cenário:** Ao executar `aws dynamodb list-tables`, retornava erro `AccessDeniedException`.

**Causa:** O usuário não tinha permissão para listar tabelas.

**Solução:** 
- A política foi ajustada para incluir apenas as ações necessárias:
  - `dynamodb:GetItem` (ler contador)
  - `dynamodb:UpdateItem` (atualizar contador)
- A ação `dynamodb:ListTables` **não foi adicionada**, pois não é necessária para o funcionamento do projeto.
- Isso mantém o **princípio do menor privilégio**.

---

## 🎯 Conclusão

A tabela DynamoDB está pronta para ser utilizada pela função Lambda. As permissões IAM foram configuradas seguindo a boa prática de conceder apenas as ações estritamente necessárias.

**Próximo passo:** Criar a API Gateway e a função Lambda (Etapa 08 e 09).

---

[🏠 Voltar ao README](../README.md)