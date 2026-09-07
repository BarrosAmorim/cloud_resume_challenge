import os
import json

import boto3
from moto import mock_aws

# Configurações do ambiente de teste
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['TABLE_NAME'] = 'VisitorsCount'

# Importa a função Lambda
from lambda_function import lambda_handler


@mock_aws
def test_lambda_handler():
    """Testa se a Lambda incrementa o contador corretamente"""

    # Criar a tabela DynamoDB mockada
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

    # Inserir um item inicial
    table.put_item(
        Item={
            'id': 'visitor_count',
            'visit_count': 0
        }
    )

    # Chamar a função Lambda
    response = lambda_handler({}, None)

    print("\nRESPOSTA DA LAMBDA:", response)

    # Verificar se a Lambda respondeu com sucesso
    assert response['statusCode'] == 200, (
        f"Erro da Lambda: {response}"
    )

    body = json.loads(response['body'])

    assert 'count' in body
    assert body['count'] == 1


@mock_aws
def test_lambda_handler_multiple_calls():
    """Testa se a Lambda incrementa corretamente em múltiplas chamadas"""

    # Criar a tabela DynamoDB mockada
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

    # Inserir um item inicial
    table.put_item(
        Item={
            'id': 'visitor_count',
            'visit_count': 0
        }
    )

    # Chamar a Lambda 3 vezes
    for i in range(3):
        response = lambda_handler({}, None)

        print("\nRESPOSTA DA LAMBDA:", response)

        assert response['statusCode'] == 200, (
            f"Erro da Lambda: {response}"
        )

        body = json.loads(response['body'])

        assert body['count'] == i + 1

    # Verificar o valor final no DynamoDB
    db_response = table.get_item(
        Key={'id': 'visitor_count'}
    )

    assert db_response['Item']['visit_count'] == 3