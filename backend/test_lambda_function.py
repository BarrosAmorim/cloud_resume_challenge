import json
from unittest.mock import MagicMock

import lambda_function


def test_lambda_handler():
    # Simula o DynamoDB
    lambda_function.table = MagicMock()

    lambda_function.table.update_item.return_value = {
        "Attributes": {
            "visit_count": 51  # ← Corrigido
        }
    }

    # Executa a Lambda
    response = lambda_function.lambda_handler({}, None)

    # Verifica o resultado
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert body["count"] == 51


def test_lambda_increments_counter():
    # Simula o DynamoDB
    lambda_function.table = MagicMock()

    lambda_function.table.update_item.return_value = {
        "Attributes": {
            "visit_count": 51  # ← Corrigido
        }
    }

    # Executa a Lambda
    lambda_function.lambda_handler({}, None)

    # Verifica se o DynamoDB recebeu o comando correto
    lambda_function.table.update_item.assert_called_once_with(
        Key={
            "id": "visitor_count"  # ← Corrigido
        },
        UpdateExpression="ADD visit_count :inc",  # ← Corrigido
        ExpressionAttributeValues={
            ":inc": 1
        },
        ReturnValues="UPDATED_NEW"
    )


def test_lambda_returns_different_count():
    # Simula o DynamoDB
    lambda_function.table = MagicMock()

    lambda_function.table.update_item.return_value = {
        "Attributes": {
            "visit_count": 100  # ← Corrigido
        }
    }

    # Executa a Lambda
    response = lambda_function.lambda_handler({}, None)

    # Verifica o resultado
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert body["count"] == 100