# Etapa 11: Infrastructure as Code com AWS SAM

## Objetivo

Converter a infraestrutura do Cloud Resume Challenge em **Infrastructure as Code (IaC)** usando o **AWS SAM (Serverless Application Model)** e o **AWS CloudFormation**.

Nesta etapa, o SAM passa a criar e gerenciar:

- DynamoDB
- Lambda
- API Gateway HTTP
- IAM Role da Lambda
- Permissão da API Gateway para invocar a Lambda
- Stage da API Gateway

Ao final, a infraestrutura deixa de depender de criação manual pelo console e passa a ser reproduzível a partir do `template.yaml`.

---

## Status

✅ Concluído

---

## Recursos utilizados

- AWS SAM CLI
- AWS CloudFormation
- AWS CLI
- AWS Lambda
- Amazon DynamoDB
- Amazon API Gateway (HTTP API)
- IAM
- Amazon S3
- Amazon CloudFront
- Python 3.13
- YAML
- TOML

---

# 1. Conceito: Infrastructure as Code

Infrastructure as Code (IaC) é a prática de definir a infraestrutura por meio de arquivos de código, em vez de criar os recursos manualmente no console.

No projeto, o arquivo principal é:

```text
template.yaml
```

O SAM utiliza esse template e gera os recursos necessários no CloudFormation.

### Benefícios

- **Reprodutibilidade:** a infraestrutura pode ser recriada.
- **Versionamento:** o template pode ficar no Git.
- **Consistência:** os recursos seguem a configuração definida no código.
- **Automação:** a mesma infraestrutura pode ser utilizada posteriormente em CI/CD.

---

# 2. Ordem correta das etapas

Antes do SAM, a infraestrutura foi construída e testada manualmente para validar o funcionamento.

A sequência adotada foi:

```text
DynamoDB
    ↓
Lambda
    ↓
API Gateway
    ↓
Testes
    ↓
SAM / CloudFormation
```

A ordem é importante porque:

- a Lambda precisa acessar o DynamoDB;
- o API Gateway precisa de uma Lambda para integração;
- depois disso o SAM pode transformar toda a infraestrutura em código.

---

# 3. Atenção: recursos criados manualmente

Antes de executar o primeiro `sam deploy`, os recursos abaixo já haviam sido criados manualmente:

```text
DynamoDB: VisitorsCount
Lambda: visitor-counter
API Gateway: visitor-counter-API
```

O template SAM também utiliza esses mesmos nomes.

Se os recursos manuais continuarem existindo fora da stack, o CloudFormation tentará criá-los novamente e poderá ocorrer o erro:

```text
AWS::EarlyValidation::ResourceExistenceCheck
```

Durante este projeto, esse erro aconteceu porque o CloudFormation estava tentando adicionar recursos que já existiam fora da stack.

## Caminho utilizado no laboratório

Como este é um laboratório e os recursos já haviam sido testados, foi adotado o caminho mais simples:

1. Manter os buckets e o CloudFront que continuariam sendo utilizados.
2. Remover os recursos serverless criados manualmente.
3. Deixar o SAM criar novamente esses recursos.
4. Passar a gerenciar a infraestrutura pela stack CloudFormation.

### Recursos removidos antes do `sam deploy`

```text
DynamoDB: VisitorsCount
Lambda: visitor-counter
API Gateway: visitor-counter-API
IAM Role manual da Lambda
```

A stack que estava em `REVIEW_IN_PROGRESS` também foi removida antes de uma nova tentativa de deploy.

> **Alternativa avançada:** em um ambiente onde os recursos não podem ser apagados, é possível importar recursos existentes para uma stack CloudFormation. Esse processo é mais complexo e não foi utilizado neste laboratório.

---

# 4. Instalar o AWS SAM CLI

O ambiente utilizado é um Raspberry Pi ARM64, portanto deve ser utilizado o instalador ARM64.

## 4.1 Download

```bash
wget https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-arm64.zip
```

## 4.2 Descompactar

```bash
unzip aws-sam-cli-linux-arm64.zip -d sam-installation
```

## 4.3 Instalar

```bash
sudo ./sam-installation/install
```

## 4.4 Verificar

```bash
sam --version
```

Exemplo:

```text
SAM CLI, version 1.166.1
```

A versão pode ser diferente conforme a versão atual do SAM CLI.

---

# 5. Criar o `template.yaml`

Na raiz do projeto:

```bash
cd ~/projects/cloud-resume-challenge-aws
```

Crie ou edite o arquivo:

```bash
nano template.yaml
```

## 5.1 Template utilizado

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
      TableName: VisitorsCount
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
      FunctionName: visitor-counter
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
      Name: visitor-counter-API
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

### Pontos importantes do template

A tabela utiliza:

```yaml
BillingMode: PAY_PER_REQUEST
```

A chave primária é:

```text
id
```

O atributo `count` não aparece em `AttributeDefinitions` porque ele **não faz parte da chave da tabela**.

A Lambda recebe o nome da tabela por variável de ambiente:

```yaml
TABLE_NAME: !Ref CloudResumeVisitorCount
```

A API cria a rota:

```text
GET /count
```

e integra essa rota à Lambda.

---

# 6. Criar o `samconfig.toml`

O arquivo `samconfig.toml` evita a necessidade de digitar os parâmetros do deploy toda vez.

Crie:

```bash
nano samconfig.toml
```

Conteúdo utilizado:

```toml
version = 0.1

[default.deploy.parameters]
stack_name = "cloud-resume-challenge-aws"
resolve_s3 = false
s3_bucket = "sam-artifacts-rafael-2026"
s3_prefix = "cloud-resume-challenge-aws"
confirm_changeset = true
capabilities = "CAPABILITY_IAM"
image_repositories = []
disable_rollback = true

[default.global.parameters]
region = "us-east-1"
```

## Por que `resolve_s3 = false`?

O projeto utiliza um bucket próprio para os artefatos do SAM:

```text
sam-artifacts-rafael-2026
```

Com:

```toml
resolve_s3 = false
```

fica definido que o SAM deve utilizar o bucket informado em:

```toml
s3_bucket = "sam-artifacts-rafael-2026"
```

Isso evita que o SAM tente utilizar um bucket gerenciado automaticamente.

---

# 7. Ambiente virtual Python

Ao instalar dependências Python diretamente no Raspberry Pi, o sistema pode retornar o erro:

```text
error: externally-managed-environment
```

Isso ocorre por causa do PEP 668.

A solução utilizada foi criar um ambiente virtual.

Na raiz do projeto:

```bash
python3 -m venv .venv
```

Ativar:

```bash
source .venv/bin/activate
```

Instalar as dependências:

```bash
pip install -r backend/requirements.txt
```

Executar os testes automatizados:

```bash
pytest -v
```

Ao terminar:

```bash
deactivate
```

Adicionar ao `.gitignore`:

```gitignore
.venv/
```

---

# 8. Configuração das permissões IAM

As permissões foram separadas por responsabilidade.

## 8.1 Políticas do usuário/grupo

O usuário utilizado no projeto é:

```text
cloud-resume-aws-2026
```

Ele pertence ao grupo:

```text
CloudResumeChallengeAWS
```

As políticas de deploy/gerenciamento ficam no **grupo**.

A organização final utilizada foi:

```text
CloudResumeChallengeAWS
├── CloudResume-APIGateway
├── CloudResume-CloudFormation
├── CloudResume-DynamoDB-Management
├── CloudResume-IAM-SAM
├── CloudResume-Lambda-Deploy
├── CloudResume-S3
└── CloudResumeChallengeAWSCloudFrontPolicy
```

A política antiga de S3 `S3StaticSiteAccess` foi removida para evitar duplicidade, pois `CloudResume-S3` passou a ser a política usada para esse acesso.

---

## 8.2 Política `CloudResume-S3`

Responsável pelos buckets utilizados no projeto.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:CreateBucket"
            ],
            "Resource": [
                "arn:aws:s3:::sam-artifacts-rafael-2026"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::curriculo-rafael-barros-2026",
                "arn:aws:s3:::sam-artifacts-rafael-2026"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::curriculo-rafael-barros-2026/*",
                "arn:aws:s3:::sam-artifacts-rafael-2026/*"
            ]
        }
    ]
}
```

O bucket do site já existente é:

```text
curriculo-rafael-barros-2026
```

O bucket utilizado pelos artefatos do SAM é:

```text
sam-artifacts-rafael-2026
```

> O `CreateBucket` foi separado do `ListBucket` e das ações de objeto porque o bucket e os objetos utilizam tipos de ARN diferentes.

---

## 8.3 Política `CloudResume-CloudFront`

Responsável por invalidar o cache da distribuição.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cloudfront:CreateInvalidation"
            ],
            "Resource": "arn:aws:cloudfront::696537703431:distribution/EGGP4OT7VLDC2"
        }
    ]
}
```

No grupo, permanece a política existente:

```text
CloudResumeChallengeAWSCloudFrontPolicy
```

caso ela já seja a política utilizada para a distribuição.

---

## 8.4 Política `CloudResume-DynamoDB-Management`

Responsável por operações administrativas do DynamoDB necessárias ao processo de infraestrutura.

```json
{
    "Version": "2012-10-17",
    "Statement": [
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
        }
    ]
}
```

> **Atenção:** se o nome da tabela definido no template for alterado, o ARN dessa política também precisa ser revisado.

---

## 8.5 Política `CloudResume-CloudFormation`

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "cloudformation:*",
            "Resource": "*"
        }
    ]
}
```

Ela permite ao usuário trabalhar com a stack do CloudFormation durante o deploy do SAM.

---

## 8.6 Política `CloudResume-IAM-SAM`

Responsável pelas operações IAM utilizadas para criar e administrar as Roles relacionadas ao deploy.

```json
{
    "Version": "2012-10-17",
    "Statement": [
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
        }
    ]
}
```

---

## 8.7 Política `CloudResume-Lambda-Deploy`

```json
{
    "Version": "2012-10-17",
    "Statement": [
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
        }
    ]
}
```

---

## 8.8 Política `CloudResume-APIGateway`

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "apigateway:*",
            "Resource": "*"
        }
    ]
}
```

---

# 9. Permissões da Lambda

As permissões usadas pela **execução da Lambda** não ficam no grupo do usuário.

A Role da Lambda deve ter as permissões necessárias para executar a função.

Estrutura:

```text
Lambda visitor-counter
        ↓
Execution Role
├── AWSLambdaBasicExecutionRole
└── VisitorsCount-DynamoDB-Access
```

### `VisitorsCount-DynamoDB-Access`

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
        }
    ]
}
```

A política `AWSLambdaBasicExecutionRole` permanece na Role para permitir os logs de execução da Lambda.

> Mesmo que o projeto não utilize o CloudWatch como parte funcional da aplicação, manter a política básica de execução evita perder os logs da Lambda, que são úteis para diagnóstico.

---

# 10. Criar o bucket de artefatos do SAM

O bucket utilizado pelo `samconfig.toml` é:

```text
sam-artifacts-rafael-2026
```

Criar:

```bash
aws s3 mb s3://sam-artifacts-rafael-2026 --region us-east-1
```

Verificar:

```bash
aws s3 ls s3://sam-artifacts-rafael-2026 --region us-east-1
```

O bucket pode estar vazio antes do primeiro deploy. Durante o deploy, o SAM envia os artefatos para ele.

### Bucket automático do SAM

Quando `resolve_s3 = true`, o SAM pode criar/usar um bucket gerenciado automaticamente, com nome semelhante a:

```text
aws-sam-cli-managed-default-samclisourcebucket-...
```

Como o projeto utiliza um bucket próprio, o `samconfig.toml` foi configurado com:

```toml
resolve_s3 = false
s3_bucket = "sam-artifacts-rafael-2026"
```

---

# 11. Selecionar o perfil AWS

O projeto utiliza o perfil:

```text
cloud-resume-aws
```

Antes dos comandos AWS/SAM, no terminal atual:

```bash
export AWS_PROFILE=cloud-resume-aws
```

Verificar a identidade:

```bash
aws sts get-caller-identity
```

O `export` vale para a sessão atual do terminal.

---

# 12. Validar o template

Na raiz do projeto:

```bash
sam validate
```

O esperado é uma mensagem indicando que o template é válido.

---

# 13. Fazer o build

Ativar o ambiente virtual:

```bash
source .venv/bin/activate
```

Instalar dependências, caso ainda não tenha feito:

```bash
pip install -r backend/requirements.txt
```

Executar:

```bash
sam build
```

O SAM deverá construir a Lambda a partir de:

```text
backend/
```

O resultado fica em:

```text
.aws-sam/build/
```

---

# 14. Fazer o deploy

Com o `samconfig.toml` configurado, o deploy pode ser executado simplesmente com:

```bash
sam deploy
```

O SAM utilizará os parâmetros salvos no `samconfig.toml`.

Durante o processo, serão criados pelo CloudFormation os recursos definidos no template.

Exemplo dos eventos observados durante o deploy:

```text
CREATE_IN_PROGRESS  AWS::DynamoDB::Table      CloudResumeVisitorCount
CREATE_COMPLETE     AWS::DynamoDB::Table      CloudResumeVisitorCount

CREATE_IN_PROGRESS  AWS::IAM::Role            CloudResumeCounterRole
CREATE_COMPLETE     AWS::IAM::Role            CloudResumeCounterRole

CREATE_IN_PROGRESS  AWS::Lambda::Function     CloudResumeCounter
CREATE_COMPLETE     AWS::Lambda::Function     CloudResumeCounter

CREATE_IN_PROGRESS  AWS::ApiGatewayV2::Api    CloudResumeApi
CREATE_COMPLETE     AWS::ApiGatewayV2::Api    CloudResumeApi

CREATE_COMPLETE     AWS::Lambda::Permission
CREATE_COMPLETE     AWS::ApiGatewayV2::Stage

CREATE_COMPLETE     AWS::CloudFormation::Stack
```

---

# 15. Outputs do deploy

Ao finalizar, o SAM/CloudFormation mostra os outputs definidos no template.

Exemplo:

```text
ApiUrl
https://1wwa2j23cc.execute-api.us-east-1.amazonaws.com

ApiCountUrl
https://1wwa2j23cc.execute-api.us-east-1.amazonaws.com/count

DynamoDBTableName
VisitorsCount

LambdaFunctionName
visitor-counter
```

> O ID da API pode mudar quando a infraestrutura for recriada. Portanto, a URL apresentada pelo deploy deve ser considerada a fonte correta para a nova API.

---

# 16. Testar a API criada pelo SAM

Testar diretamente o endpoint:

```bash
curl https://1wwa2j23cc.execute-api.us-east-1.amazonaws.com/count
```

Exemplo de retorno:

```json
{
  "count": 1
}
```

Cada chamada ao endpoint executa a Lambda, que incrementa o contador no DynamoDB.

---

# 17. Atualizar o frontend após o SAM

Como o SAM criou uma **nova API**, o `script.js` precisa utilizar a nova URL de saída do deploy.

Exemplo:

```javascript
const apiUrl = 'https://1wwa2j23cc.execute-api.us-east-1.amazonaws.com/count';
```

O código utilizado para o contador é:

```javascript
async function getVisitorCount() {
    try {
        const apiUrl = 'https://1wwa2j23cc.execute-api.us-east-1.amazonaws.com/count';

        const response = await fetch(apiUrl);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        document.getElementById('visitor-count').textContent = data.count || '0';

    } catch (error) {
        console.error('Erro ao carregar contador:', error);
        document.getElementById('visitor-count').textContent = '⚠️ Erro';
    }
}

document.addEventListener('DOMContentLoaded', getVisitorCount);
```

### Atenção

Não deve existir uma linha como:

```javascript
document.getElementById('visitor-count').textContent = count;
```

porque `count` não foi declarado nesse código.

O valor correto vem da resposta da API:

```javascript
data.count
```

---

# 18. Enviar o `script.js` atualizado para o S3

Após alterar o arquivo local, confirmar:

```bash
grep "apiUrl" frontend/script.js
```

A URL deve ser a URL da API criada pelo SAM.

Depois enviar para o bucket do site:

```bash
aws s3 cp frontend/script.js \
  s3://curriculo-rafael-barros-2026/script.js \
  --region us-east-1
```

Confirmar o conteúdo diretamente no S3:

```bash
aws s3 cp \
  s3://curriculo-rafael-barros-2026/script.js \
  - \
  --region us-east-1 | grep "apiUrl"
```

Isso é importante porque permite verificar o arquivo que realmente está armazenado no bucket, sem depender do navegador ou do CloudFront.

---

# 19. Invalidar o cache do CloudFront

Depois de confirmar que o `script.js` correto está no S3, invalidar o arquivo no CloudFront:

```bash
aws cloudfront create-invalidation \
  --distribution-id E1LPZAUDPQIFSS \
  --paths "/script.js"
```

A invalidação faz o CloudFront buscar novamente o `script.js` atualizado.

Depois, no navegador:

```text
Ctrl + F5
```

---

# 20. Fluxo final da aplicação

A arquitetura final fica:

```text
                    Usuário
                       │
                       ▼
              CloudFront / S3
                       │
                       │ script.js
                       ▼
             GET /count
                       │
                       ▼
              API Gateway HTTP
                       │
                       ▼
             Lambda visitor-counter
                       │
                       ▼
              DynamoDB VisitorsCount
                       │
                       ▼
                 {"count": N}
```

Com SAM/IaC, a infraestrutura serverless é descrita em:

```text
template.yaml
```

e administrada pelo:

```text
AWS SAM
    ↓
CloudFormation
```

---

# 21. Verificações finais

Antes de considerar a etapa concluída:

### SAM

```bash
sam validate
sam build
sam deploy
```

### API

```bash
curl https://<API-ID>.execute-api.us-east-1.amazonaws.com/count
```

### DynamoDB

A tabela deve existir:

```text
VisitorsCount
```

com o item:

```text
id = visitor_count
count = N
```

### Lambda

A função deve ser:

```text
visitor-counter
```

### Frontend

O `script.js` deve apontar para a **URL `/count` gerada pelo SAM**.

### S3

O arquivo `script.js` atualizado deve estar no:

```text
curriculo-rafael-barros-2026
```

### CloudFront

Após atualizar o `script.js`, realizar a invalidação do arquivo.

---

# 22. Problemas encontrados e soluções

## Problema 1 — `externally-managed-environment`

### Erro

```text
error: externally-managed-environment
```

### Causa

O Python do sistema está protegido contra instalação direta via `pip`.

### Solução

Criar e ativar um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

---

## Problema 2 — Bucket do SAM não encontrado

### Erro

```text
S3 Bucket does not exist.
```

### Causa

O bucket definido no `samconfig.toml` não existia ou o SAM estava tentando usar um bucket gerenciado automaticamente diferente do esperado.

### Solução

Criar o bucket:

```bash
aws s3 mb s3://sam-artifacts-rafael-2026 --region us-east-1
```

E usar:

```toml
resolve_s3 = false
s3_bucket = "sam-artifacts-rafael-2026"
```

---

## Problema 3 — `AccessDenied` ao criar o bucket

### Erro

```text
not authorized to perform: s3:CreateBucket
```

### Causa

Faltava a permissão `s3:CreateBucket` para o usuário responsável pelo deploy.

### Solução

Adicionar essa ação à política de S3 e anexar a política ao grupo do usuário.

---

## Problema 4 — `AccessDenied` no DynamoDB pela Lambda

### Erro

```text
is not authorized to perform: dynamodb:UpdateItem
```

### Causa

A política do DynamoDB estava associada ao usuário/grupo, mas a Lambda executava com outra IAM Role.

### Solução

Anexar `VisitorsCount-DynamoDB-Access` à **Execution Role da Lambda**.

Estrutura:

```text
Lambda Role
├── AWSLambdaBasicExecutionRole
└── VisitorsCount-DynamoDB-Access
```

---

## Problema 5 — `ResourceExistenceCheck`

### Erro

```text
AWS::EarlyValidation::ResourceExistenceCheck
```

### Causa

A stack do CloudFormation estava tentando criar recursos que já existiam fora da stack, como:

```text
VisitorsCount
visitor-counter
visitor-counter-API
```

### Solução utilizada neste laboratório

Remover os recursos serverless criados manualmente e deixar o SAM recriá-los e passar a gerenciá-los.

> Em ambientes onde os recursos não podem ser apagados, a alternativa é importá-los para o CloudFormation.

---

## Problema 6 — `ERR_NAME_NOT_RESOLVED` no navegador

### Erro

```text
GET https://<API-antiga>/count
net::ERR_NAME_NOT_RESOLVED
```

### Causa

O `script.js` ainda estava apontando para uma URL antiga da API.

### Solução

Atualizar a URL para a URL gerada pelo SAM:

```javascript
const apiUrl = 'https://<API-ID>.execute-api.us-east-1.amazonaws.com/count';
```

Enviar o arquivo ao S3 e invalidar o CloudFront.

---

## Problema 7 — `ReferenceError: count is not defined`

### Erro

```text
ReferenceError: count is not defined
```

### Causa

O `script.js` continha uma linha como:

```javascript
document.getElementById('visitor-count').textContent = count;
```

mas a variável `count` não havia sido declarada.

### Solução

Usar o valor retornado pela API:

```javascript
document.getElementById('visitor-count').textContent = data.count || '0';
```

---

## Problema 8 — CloudFront ainda servindo o `script.js` antigo

### Sintoma

O S3 já tinha o arquivo novo, mas o site continuava executando a versão antiga.

### Causa

Cache do CloudFront.

### Solução

Depois de confirmar o arquivo no S3:

```bash
aws cloudfront create-invalidation \
  --distribution-id E1LPZAUDPQIFSS \
  --paths "/script.js"
```

Depois:

```text
Ctrl + F5
```

---

# 23. Resultado final da etapa

Ao finalizar esta etapa, a infraestrutura serverless passa a ser gerenciada por uma stack CloudFormation criada pelo SAM:

```text
cloud-resume-challenge-aws
```

Recursos gerenciados pela stack:

```text
CloudResumeVisitorCount
        ↓
DynamoDB VisitorsCount

CloudResumeCounter
        ↓
Lambda visitor-counter

CloudResumeApi
        ↓
API Gateway visitor-counter-API

CloudResumeCounterRole
        ↓
IAM Role da Lambda

CloudResumeCounterCountApiPermission
        ↓
Permissão API Gateway → Lambda

CloudResumeApiApiGatewayDefaultStage
        ↓
Stage $default
```

O projeto passa a ter uma fonte declarativa da infraestrutura em:

```text
template.yaml
```

e os parâmetros de implantação em:

```text
samconfig.toml
```

Isso prepara o projeto para a próxima etapa: **CI/CD do backend**, onde o processo de validação, build e deploy poderá ser automatizado.
