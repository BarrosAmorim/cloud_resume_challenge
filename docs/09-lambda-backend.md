# Etapa 09: Lambda - Backend em Python

## Objetivo
Criar uma função AWS Lambda em Python que recebe requisições da API Gateway, incrementa o contador de visitas no DynamoDB e retorna o valor atualizado.

## Status
✅ Concluído

## Recursos Utilizados
- AWS Lambda
- Python 3.11
- Boto3 (AWS SDK para Python)
- Amazon DynamoDB
- AWS IAM

---

## 📋 Passo a Passo Completo

### Parte 1: Criar a Função Lambda

#### 1.1 Acessar o Lambda

1. No console AWS, pesquisar por **"Lambda"**
2. Clicar no resultado para abrir o serviço

#### 1.2 Criar a Função

1. Clicar em **"Create function"** (Criar função)
2. Preencher:

| Campo | Valor | Motivo |
|-------|-------|--------|
| **Function name** | `visitor-counter` | Nome descritivo para a função |
| **Runtime** | `Python 3.11` | Versão mais recente e estável |
| **Architecture** | `x86_64` | Compatível com todos os serviços |
| **Permissions** | `Create a new role with basic Lambda permissions` | Criar permissões básicas |

3. Clicar em **"Create function"**

---

### Parte 2: Adicionar o Código Python

#### 2.1 Substituir o Código

1. No editor da Lambda, substituir o código padrão pelo conteúdo abaixo:

```python
import json
import boto3
import os
from decimal import Decimal

# Conectar ao DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'VisitorsCount')
table = dynamodb.Table(table_name)

class DecimalEncoder(json.JSONEncoder):
    """Serializa objetos Decimal para JSON"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    """
    Função principal da Lambda.
    Incrementa o contador de visitas no DynamoDB e retorna o valor.
    """
    try:
        # Incrementar o contador
        response = table.update_item(
            Key={'id': 'visitor_count'},
            UpdateExpression='ADD visit_count :inc',
            ExpressionAttributeValues={':inc': 1},
            ReturnValues='UPDATED_NEW'
        )
        
        # Obter o novo valor
        count = response['Attributes']['visit_count']
        
        # Retornar resposta com CORS
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'count': int(count)
            }, cls=DecimalEncoder)
        }
        
    except Exception as e:
        # Tratar erros
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
```

#### 2.2 Explicação do Código

| Parte do código | O que faz |
|-----------------|-----------|
| `import boto3` | Importa o SDK da AWS para Python |
| `dynamodb = boto3.resource('dynamodb')` | Conecta ao DynamoDB |
| `table.update_item()` | Incrementa o contador na tabela |
| `DecimalEncoder` | Converte números decimais para JSON |
| `Access-Control-Allow-Origin: '*'` | Permite CORS (pode ser restrito depois) |

#### 2.3 Deploy do Código

1. Clicar em **"Deploy"** (Botão laranja no topo)
2. Verificar se apareceu: "Successfully deployed"

---

### Parte 3: Configurar Variáveis de Ambiente

1. Na aba **"Configuration"** (Configuração)
2. Clicar em **"Environment variables"** (Variáveis de ambiente)
3. Clicar em **"Edit"** (Editar)
4. Adicionar:

| Key | Value | Motivo |
|-----|-------|--------|
| `TABLE_NAME` | `VisitorsCount` | Nome da tabela DynamoDB |

5. Clicar em **"Save"**

---

### Parte 4: Configurar Permissões IAM

A Lambda precisa de permissão para acessar o DynamoDB.

#### 4.1 Adicionar Política à Role da Lambda

1. Na Lambda, ir na aba **"Configuration"** → **"Permissions"**
2. Clicar no nome da Role (ex: `visitor-counter-role-xxxxx`)
3. Clicar em **"Add permissions"** → **"Attach policies"**
4. Pesquisar por **`AmazonDynamoDBFullAccess`** (ou criar política customizada)
5. Marcar a política e clicar em **"Attach policy"**

#### 4.2 Política Customizada (Menor Privilégio)

Se preferir uma política mais restrita, criar a seguinte política no IAM:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:UpdateItem"
            ],
            "Resource": "arn:aws:dynamodb:us-east-1:696537703431:table/VisitorsCount"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
```

---

### Parte 5: Testar a Lambda

#### 5.1 Teste no Console

1. Na Lambda, ir na aba **"Code"**
2. Clicar em **"Test"**
3. Criar um novo evento de teste:
   - **Event name:** `test`
   - **Template:** `hello-world`
4. Clicar em **"Save"**
5. Clicar em **"Test"** novamente

**Resultado esperado:**
```json
{
  "statusCode": 200,
  "headers": {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json"
  },
  "body": "{\"count\": 1}"
}
```

#### 5.2 Verificar o DynamoDB

1. Ir no **DynamoDB** → **Explore items**
2. A tabela `VisitorsCount` deve ter o item `visitor_count` com `visit_count` incrementado

---

### Parte 6: Conectar com API Gateway

A Lambda já foi integrada à API Gateway durante a Etapa 08.

**Verificar a integração:**
1. No API Gateway, ir em **"Routes"**
2. Verificar se a rota `GET /count` tem a integração `visitor-counter`

---

## 🔍 Verificação

**Teste via terminal:**
```bash
curl https://qjtn3yvqhe.execute-api.us-east-1.amazonaws.com/count
```

**Resultado esperado:**
```json
{"count": 1}
```

**Teste no console da Lambda:**
- Verificar os logs no **CloudWatch**:
  1. Na Lambda, ir em **"Monitor"**
  2. Clicar em **"View CloudWatch logs"**
  3. Verificar se não há erros

---

## 🐛 Problemas e Soluções

### Problema 1: Erro de permissão no DynamoDB

**Cenário:** A Lambda retornava erro "AccessDenied" ao acessar o DynamoDB.

**Causa:** A Role da Lambda não tinha permissão para a tabela.

**Solução:** Adicionar a política `AmazonDynamoDBFullAccess` à Role da Lambda.

### Problema 2: Erro "Decimal cannot be serialized"

**Cenário:** A Lambda retornava erro ao converter o número do DynamoDB.

**Causa:** O DynamoDB retorna números no formato Decimal, que não é serializável pelo JSON padrão.

**Solução:** Usar o `DecimalEncoder` para converter os valores antes de retornar.

### Problema 3: CORS não funcionando

**Cenário:** O navegador bloqueava a requisição.

**Causa:** A Lambda não retornava os cabeçalhos CORS.

**Solução:** Adicionar `Access-Control-Allow-Origin: '*'` no retorno da Lambda.

---

## 📊 Resumo da Configuração Final

| Recurso | Configuração |
|---------|--------------|
| **Nome da Função** | `visitor-counter` |
| **Runtime** | Python 3.11 |
| **Handler** | `lambda_function.lambda_handler` |
| **Variável de ambiente** | `TABLE_NAME = VisitorsCount` |
| **Permissões** | DynamoDB: GetItem, UpdateItem |
| **Tabela** | `VisitorsCount` |
| **Item** | `id = visitor_count`, `visit_count = 0` |

---

## 🎯 Conclusão

A função Lambda em Python está criada, configurada e integrada com o DynamoDB e API Gateway. O contador de visitas funciona corretamente, incrementando a cada requisição.

**Próximo passo:** Criar testes automatizados para a Lambda (Etapa 10).

---

[🏠 Voltar ao README](../README.md)