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
    Incrementa o contador de visitas no DynamoDB e retorna o valor
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
