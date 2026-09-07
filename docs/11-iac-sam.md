# Etapa 11: Infrastructure as Code com AWS SAM

## Objetivo
Converter toda a infraestrutura serverless (DynamoDB, Lambda, API Gateway) em código utilizando o AWS SAM (Serverless Application Model), permitindo que seja versionada, reproduzida e automatizada.

## Status
✅ Concluído

## Recursos Utilizados
- AWS SAM CLI
- AWS CloudFormation
- AWS CLI
- Python 3.13
- YAML

---

## 📋 O que é Infrastructure as Code (IaC)

**Infrastructure as Code** é a prática de definir sua infraestrutura (servidores, bancos de dados, APIs) em **arquivos de texto** (código) em vez de criar manualmente no console.

**Benefícios:**
- **Reprodutibilidade:** Recria toda a infraestrutura com um comando
- **Versionamento:** A infraestrutura fica no Git junto com o código
- **Consistência:** Sempre a mesma configuração
- **Automação:** Integração com CI/CD

---

## 📋 Passo a Passo Completo

### Parte 1: Instalar AWS SAM CLI

#### 1.1 Baixar e Instalar

```bash
# Baixar o instalador para Raspberry Pi (ARM)
wget https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-arm64.zip

# Descompactar
unzip aws-sam-cli-linux-arm64.zip -d sam-installation

# Instalar
sudo ./sam-installation/install

# Verificar instalação
sam --version
```

**Resultado esperado:**
```
SAM CLI, version 1.166.1
```

---

### Parte 2: Criar o Template SAM

#### 2.1 Criar o arquivo `template.yaml`

```bash
cd ~/projects/cloud_resume_challenge
nano template.yaml
```

#### 2.2 Conteúdo do `template.yaml`

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Description: Infraestrutura do Cloud Resume Challenge utilizando AWS SAM.

Resources:

  CloudResumeVisitorCount:
    Type: AWS::DynamoDB::Table
    DeletionPolicy: Retain
    UpdateReplacePolicy: Retain
    Properties:
      TableName: CloudResumeVisitorCountSAM
      BillingMode: PAY_PER_REQUEST

      AttributeDefinitions:
        - AttributeName: id
          AttributeType: S

      KeySchema:
        - AttributeName: id
          KeyType: HASH

      Tags:
        - Key: Project
          Value: CloudResumeChallenge


  CloudResumeCounter:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: cloud-resume-counter-sam
      Runtime: python3.13
      Handler: lambda_function.lambda_handler
      CodeUri: backend/
      Timeout: 3

      Environment:
        Variables:
          TABLE_NAME: !Ref CloudResumeVisitorCount

      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref CloudResumeVisitorCount

      Events:
        CountApi:
          Type: HttpApi
          Properties:
            ApiId: !Ref CloudResumeApi
            Path: /count
            Method: GET

    Metadata:
      SamResourceId: CloudResumeCounter


  CloudResumeApi:
    Type: AWS::Serverless::HttpApi
    Properties:
      Name: CloudResumeAPI-SAM
      StageName: $default

      CorsConfiguration:
        AllowOrigins:
          - https://barrosamorimd.work

        AllowMethods:
          - GET

        AllowHeaders:
          - Content-Type


Outputs:

  ApiUrl:
    Description: URL da API do contador de visitantes

    Value: !Sub
      - https://${ApiId}.execute-api.${AWS::Region}.amazonaws.com
      - ApiId: !Ref CloudResumeApi

  ApiCountUrl:
    Description: URL completa do endpoint do contador

    Value: !Sub
      - https://${ApiId}.execute-api.${AWS::Region}.amazonaws.com/count
      - ApiId: !Ref CloudResumeApi

  DynamoDBTableName:
    Description: Nome da tabela DynamoDB

    Value: !Ref CloudResumeVisitorCount

  LambdaFunctionName:
    Description: Nome da função Lambda

    Value: !Ref CloudResumeCounter
```

---

### Parte 3: Criar o Arquivo de Configuração do SAM

#### 3.1 Criar o `samconfig.toml`

```bash
nano samconfig.toml
```

#### 3.2 Conteúdo do `samconfig.toml`

```toml
version = 0.1

[default.deploy.parameters]
stack_name = "cloud-resume-challenge"
resolve_s3 = false
s3_bucket = "sam-artifacts-rafael-2026"
s3_prefix = "cloud-resume-challenge"
region = "us-east-1"
confirm_changeset = true
capabilities = "CAPABILITY_IAM"
image_repositories = []

[default.global.parameters]
region = "us-east-1"
```

---

### Parte 4: Configurar Permissões IAM

#### 4.1 Política IAM Necessária

O usuário IAM `cloud-resume-challenge-rafael-2026` precisou das seguintes permissões:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:CreateBucket",
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::cloud-resume-challenge-rafael-2026",
                "arn:aws:s3:::cloud-resume-challenge-rafael-2026/*",
                "arn:aws:s3:::sam-artifacts-rafael-2026",
                "arn:aws:s3:::sam-artifacts-rafael-2026/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:CreateTable",
                "dynamodb:DeleteTable",
                "dynamodb:TagResource",
                "dynamodb:UntagResource",
                "dynamodb:DescribeTable",
                "dynamodb:GetItem",
                "dynamodb:UpdateItem"
            ],
            "Resource": "arn:aws:dynamodb:us-east-1:696537703431:table/CloudResumeVisitorCountSAM"
        },
        {
            "Effect": "Allow",
            "Action": "cloudfront:CreateInvalidation",
            "Resource": "arn:aws:cloudfront::696537703431:distribution/EGGP4OT7VLDC2"
        },
        {
            "Effect": "Allow",
            "Action": "cloudformation:*",
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:GetRole",
                "iam:ListRoles",
                "iam:ListAttachedRolePolicies",
                "iam:ListRolePolicies",
                "iam:GetRolePolicy",
                "iam:CreateRole",
                "iam:DeleteRole",
                "iam:PutRolePolicy",
                "iam:DeleteRolePolicy",
                "iam:AttachRolePolicy",
                "iam:DetachRolePolicy",
                "iam:TagRole",
                "iam:UntagRole"
            ],
            "Resource": "arn:aws:iam::696537703431:role/cloud-resume-challenge-*"
        },
        {
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": "arn:aws:iam::696537703431:role/cloud-resume-challenge-*",
            "Condition": {
                "StringEquals": {
                    "iam:PassedToService": "lambda.amazonaws.com"
                }
            }
        },
        {
            "Effect": "Allow",
            "Action": [
                "lambda:GetFunction",
                "lambda:CreateFunction",
                "lambda:UpdateFunctionCode",
                "lambda:UpdateFunctionConfiguration",
                "lambda:DeleteFunction",
                "lambda:AddPermission",
                "lambda:RemovePermission",
                "lambda:TagResource",
                "lambda:UntagResource"
            ],
            "Resource": "arn:aws:lambda:us-east-1:696537703431:function:cloud-resume-*"
        },
        {
            "Effect": "Allow",
            "Action": "apigateway:*",
            "Resource": "*"
        }
    ]
}
```

---

### Parte 5: Criar o Bucket para Artefatos

```bash
# Criar o bucket
aws s3 mb s3://sam-artifacts-rafael-2026 --region us-east-1

# Verificar
aws s3 ls s3://sam-artifacts-rafael-2026 --region us-east-1
```

---

### Parte 6: Validar e Buildar

#### 6.1 Validar o Template

```bash
sam validate
```

**Resultado esperado:**
```
/home/rafael/projects/cloud_resume_challenge/template.yaml is a valid SAM Template
```

#### 6.2 Fazer o Build

```bash
# Ativar o ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r backend/requirements.txt

# Fazer o build
sam build
```

**Resultado esperado:**
```
Building codeuri: /home/rafael/projects/cloud_resume_challenge/backend runtime: python3.13 architecture: x86_64 functions: CloudResumeCounter
Running PythonPipBuilder:ResolveDependencies
Running PythonPipBuilder:CopySource
Build Succeeded

Built Artifacts  : .aws-sam/build
Built Template   : .aws-sam/build/template.yaml
```

---

### Parte 7: Fazer o Deploy

```bash
sam deploy --guided
```

**Respostas durante o deploy:**
| Pergunta | Resposta |
|----------|----------|
| Stack Name [cloud-resume-challenge] | Enter |
| AWS Region [us-east-1] | Enter |
| Confirm changes before deploy [Y/n] | `y` |
| Allow SAM CLI IAM role creation [Y/n] | `y` |
| CloudResumeCounter has no authentication. Is this okay? [y/N] | `y` |
| Save arguments to configuration file [Y/n] | `y` |
| SAM configuration file [samconfig.toml] | Enter |
| SAM configuration environment [default] | Enter |

**Resultado esperado:**
```
Successfully created/updated stack - cloud-resume-challenge in us-east-1

Outputs:
  ApiEndpoint: https://cwz64tvvd0.execute-api.us-east-1.amazonaws.com/count
  DynamoDBTableName: CloudResumeVisitorCountSAM
  LambdaFunctionName: cloud-resume-counter-sam
```

---

### Parte 8: Testar a API

```bash
curl https://cwz64tvvd0.execute-api.us-east-1.amazonaws.com/count
```

**Resultado esperado:**
```json
{"count": 1}
```

---

## 🐛 Problemas e Soluções

### Problema 1: SAM CLI não instalado no Raspberry Pi

**Cenário:** `sam --version` não funcionava.

**Causa:** O instalador baixado era para arquitetura x86_64, mas o Pi é ARM.

**Solução:** Baixar a versão ARM64:
```bash
wget https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-arm64.zip
```

---

### Problema 2: AccessDenied ao criar bucket

**Cenário:** `aws s3 mb` retornava `AccessDenied`.

**Causa:** O usuário IAM não tinha permissão `s3:CreateBucket`.

**Solução:** Adicionar `s3:CreateBucket` à política IAM.

---

### Problema 3: AccessDenied no DynamoDB

**Cenário:** Erro `dynamodb:DescribeTable` ou `dynamodb:TagResource`.

**Causa:** O usuário IAM não tinha permissões para o DynamoDB.

**Solução:** Adicionar `dynamodb:DescribeTable`, `dynamodb:TagResource`, `dynamodb:CreateTable` à política IAM.

---

### Problema 4: AccessDenied no API Gateway

**Cenário:** Erro `apigateway:TagResource`.

**Causa:** O usuário IAM não tinha permissão para o API Gateway.

**Solução:** Adicionar `apigateway:*` à política IAM.

---

### Problema 5: Erro `ResourceExistenceCheck`

**Cenário:** SAM falhava com `AWS::EarlyValidation::ResourceExistenceCheck`.

**Causa:** O SAM não conseguia validar a existência da tabela DynamoDB.

**Solução:** Adicionar `dynamodb:ListTables` e `dynamodb:DescribeTable` à política IAM.

---

### Problema 6: CloudFront cache antigo

**Cenário:** O site continuava mostrando `⚠️ Erro` mesmo com a API funcionando.

**Causa:** O CloudFront mantinha a versão antiga do `script.js` em cache.

**Solução:** Invalidar o cache:
```bash
aws cloudfront create-invalidation --distribution-id EGGP4OT7VLDC2 --paths "/*"
```

---

## 📊 Resumo dos Recursos Criados

| Recurso | Nome na AWS | Tipo |
|---------|-------------|------|
| **Tabela DynamoDB** | `CloudResumeVisitorCountSAM` | Banco de dados |
| **Função Lambda** | `cloud-resume-counter-sam` | Backend Python |
| **API Gateway** | `CloudResumeAPI-SAM` | API HTTP |
| **URL da API** | `https://cwz64tvvd0.execute-api.us-east-1.amazonaws.com/count` | Endpoint |

---

## 🎯 Conclusão

A infraestrutura foi completamente migrada para Infrastructure as Code usando AWS SAM. Agora, todo o backend pode ser recriado com um único comando:

```bash
sam deploy
```

**Próximo passo:** Configurar CI/CD com GitHub Actions (Etapa 12 e 13).

---

[🏠 Voltar ao README](../README.md)