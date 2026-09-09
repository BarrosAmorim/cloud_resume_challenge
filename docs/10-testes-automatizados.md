# Etapa 10: Testes Automatizados

## Objetivo
Criar testes automatizados para a função Lambda utilizando Pytest e Moto, garantindo que o contador de visitas funcione corretamente antes de cada deploy.

## Status
✅ Concluído

## Recursos Utilizados
- Python 3.11
- Pytest (framework de testes)
- Moto (mock dos serviços AWS)
- Boto3 (SDK AWS para Python)

---

## 📋 Passo a Passo Completo

### Parte 1: Criar a Estrutura de Arquivos

#### 1.1 Criar a pasta `backend/` (se não existir)

```bash
cd ~/projects/cloud_resume_challenge
mkdir -p backend
```

#### 1.2 Criar o arquivo `backend/requirements.txt`

```
boto3
pytest
moto

```

#### 1.3 Criar o arquivo `backend/lambda_function.py`

```
import json
import boto3
import os
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)


def lambda_handler(event, context):
    try:
        table_name = os.environ.get('TABLE_NAME', 'VisitorsCount')

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)

        response = table.update_item(
            Key={'id': 'visitor_count'},
            UpdateExpression='ADD visitor_count :inc',
            ExpressionAttributeValues={':inc': 1},
            ReturnValues='UPDATED_NEW'
        )

        count = response['Attributes']['visitor_count']

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
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }

```

#### 1.4 Criar o arquivo `backend/test_lambda_function.py`

```
import os
import json

import boto3
from moto import mock_aws

os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['TABLE_NAME'] = 'VisitorsCount'

from lambda_function import lambda_handler


@mock_aws
def test_lambda_handler():
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.create_table(
        TableName='VisitorsCount',
        KeySchema=[
            {'AttributeName': 'id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'id', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )

    table.put_item(
        Item={
            'id': 'visitor_count',
            'visitor_count': 0
        }
    )

    response = lambda_handler({}, None)

    print("\nRESPOSTA DA LAMBDA:", response)

    assert response['statusCode'] == 200, (
        f"Erro da Lambda: {response}"
    )

    body = json.loads(response['body'])

    assert 'count' in body
    assert body['count'] == 1


@mock_aws
def test_lambda_handler_multiple_calls():
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.create_table(
        TableName='VisitorsCount',
        KeySchema=[
            {'AttributeName': 'id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'id', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )

    table.put_item(
        Item={
            'id': 'visitor_count',
            'visitor_count': 0
        }
    )

    for i in range(3):
        response = lambda_handler({}, None)

        print("\nRESPOSTA DA LAMBDA:", response)

        assert response['statusCode'] == 200, (
            f"Erro da Lambda: {response}"
        )

        body = json.loads(response['body'])

        assert body['count'] == i + 1

    db_response = table.get_item(
        Key={'id': 'visitor_count'}
    )

    assert db_response['Item']['visitor_count'] == 3

```
---

### Parte 2: Criar o Ambiente Virtual

#### 2.1 Instalar o suporte a ambientes virtuais

```bash
sudo apt install python3-venv -y
```

#### 2.2 Criar o ambiente virtual

```bash
cd ~/projects/cloud_resume_challenge
python3 -m venv venv
```

#### 2.3 Ativar o ambiente virtual

```bash
source venv/bin/activate
```

#### 2.4 Instalar as dependências

```bash
pip install -r backend/requirements.txt
```

---

### Parte 3: Executar os Testes

#### 3.1 Rodar os testes

```bash
pytest backend/test_lambda_function.py -v
```

#### 3.2 Resultado esperado

```
============================= test session starts ==============================
platform linux -- Python 3.11.2, pytest-7.4.0, pluggy-1.0.0
rootdir: /home/rafael/projects/cloud_resume_challenge
collected 2 items

backend/test_lambda_function.py::test_lambda_handler PASSED           [ 50%]
backend/test_lambda_function.py::test_lambda_handler_multiple_calls PASSED [100%]

============================== 2 passed in 0.77s ===============================
```

#### 3.3 Desativar o ambiente virtual (quando terminar)

```bash
deactivate
```

---

## 🔍 Explicação dos Testes

### Teste 1: `test_lambda_handler`

| Etapa | O que faz |
|-------|-----------|
| 1 | Cria uma tabela DynamoDB **falsa** (mock) |
| 2 | Insere um item com `visit_count = 0` |
| 3 | Chama a Lambda |
| 4 | Verifica se a resposta é `200` (sucesso) |
| 5 | Verifica se o contador retornado é `1` |
| 6 | Verifica se o DynamoDB foi atualizado para `1` |

### Teste 2: `test_lambda_handler_multiple_calls`

| Etapa | O que faz |
|-------|-----------|
| 1 | Cria uma tabela DynamoDB **falsa** (mock) |
| 2 | Insere um item com `visit_count = 0` |
| 3 | Chama a Lambda **3 vezes seguidas** |
| 4 | Verifica se cada resposta é `200` e o contador incrementa: `1 → 2 → 3` |
| 5 | Verifica se o DynamoDB foi atualizado para `3` |

---

## 📊 Explicação das Bibliotecas

| Biblioteca | Para que serve | Por que está no `requirements.txt` |
|------------|----------------|-----------------------------------|
| **boto3** | SDK da AWS para Python | A Lambda usa `boto3` para acessar o DynamoDB |
| **pytest** | Framework de testes | Executa os testes automatizados |
| **moto** | Mock dos serviços AWS | Simula o DynamoDB nos testes (não usa o real) |

---

## 🐛 Problemas e Soluções

### Problema 1: "externally-managed-environment"

**Cenário:** `pip3 install -r backend/requirements.txt` retorna erro.

**Causa:** O Raspberry Pi (Debian/Ubuntu) bloqueia instalações globais para evitar conflitos.

**Solução:** Criar um ambiente virtual:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### Problema 2: "ImportError: cannot import name 'mock_dynamodb' from 'moto'"

**Cenário:** O teste falha com erro de importação.

**Causa:** Versões mais recentes do `moto` usam `mock_aws` em vez de `mock_dynamodb`.

**Solução:** Usar `from moto import mock_aws` e `@mock_aws`.

---

## 📊 Resumo da Configuração

| Recurso | Configuração |
|---------|--------------|
| **Arquivo de dependências** | `backend/requirements.txt` |
| **Código da Lambda** | `backend/lambda_function.py` |
| **Testes** | `backend/test_lambda_function.py` |
| **Ambiente virtual** | `venv/` |
| **Framework de testes** | Pytest |
| **Mock da AWS** | Moto |

---

## 🎯 Conclusão

Os testes automatizados estão configurados e passando com sucesso. Agora, sempre que o código for alterado, os testes podem ser executados para garantir que a Lambda continue funcionando corretamente.

**Próximo passo:** Infrastructure as Code com AWS SAM (Etapa 11).

---

[🏠 Voltar ao README](../README.md)