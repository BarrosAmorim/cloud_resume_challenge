import os
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
import json
import pytest
import boto3
from moto import mock_aws

# Importar a função Lambda que vamos testar
from lambda_function import lambda_handler

@mock_aws
def test_lambda_handler():
    """Testa se a Lambda incrementa o contador corretamente"""
    
    # 1. Criar a tabela DynamoDB mockada (falsa)
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
    
    # 2. Inserir um item inicial (contador = 0)
    table.put_item(
        Item={
            'id': 'visitor_count',
            'visit_count': 0
        }
    )
    
    # 3. Configurar a variável de ambiente para o teste
    os.environ['TABLE_NAME'] = 'VisitorsCount'
    
    # 4. Chamar a função Lambda
    response = lambda_handler({}, None)
    
    # 5. Verificar se a resposta é 200 (sucesso)
    assert response['statusCode'] == 200
    
    # 6. Verificar o conteúdo da resposta
    body = json.loads(response['body'])
    assert 'count' in body
    assert body['count'] == 1
    
    # 7. Verificar se o contador foi incrementado no DynamoDB
    db_response = table.get_item(Key={'id': 'visitor_count'})
    assert db_response['Item']['visit_count'] == 1

@mock_aws
def test_lambda_handler_multiple_calls():
    """Testa se a Lambda incrementa corretamente em múltiplas chamadas"""
    
    # 1. Criar a tabela DynamoDB mockada
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
    
    # 2. Inserir item inicial
    table.put_item(
        Item={
            'id': 'visitor_count',
            'visit_count': 0
        }
    )
    
    os.environ['TABLE_NAME'] = 'VisitorsCount'
    
    # 3. Chamar a Lambda 3 vezes
    for i in range(3):
        response = lambda_handler({}, None)
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['count'] == i + 1
    
    # 4. Verificar o valor final
    db_response = table.get_item(Key={'id': 'visitor_count'})
    assert db_response['Item']['visit_count'] == 3