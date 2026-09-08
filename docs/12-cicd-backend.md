# CI/CD do Backend — GitHub Actions + AWS SAM + OIDC

## 1. Objetivo

Implementar um pipeline de CI/CD para o backend do **Cloud Resume Challenge**, utilizando:

* GitHub Actions
* Python
* Pytest
* AWS SAM
* AWS CloudFormation
* AWS Lambda
* API Gateway
* DynamoDB
* IAM
* GitHub OIDC

O objetivo é automatizar o processo:

```text
Alteração no código
       ↓
git push
       ↓
GitHub Actions
       ↓
Testes
       ↓
SAM Build
       ↓
Autenticação AWS via OIDC
       ↓
SAM Deploy
       ↓
CloudFormation
       ↓
Lambda + API Gateway + DynamoDB
```

---

# 2. Estrutura do pipeline

O workflow possui dois jobs principais:

```text
GitHub Actions
│
├── test
│   └── pytest
│
└── deploy
    ├── SAM Build
    ├── OIDC
    ├── AWS STS
    └── SAM Deploy
```

O job `deploy` depende do job `test`.

```yaml
deploy:
  needs: test
```

Isso significa que o deploy somente será executado se os testes forem concluídos com sucesso.

Além disso:

```yaml
if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

faz com que o deploy aconteça somente em `push` para a branch `main`.

Pull Requests executam os testes, mas não fazem deploy.

---

# 3. Triggers

O workflow é executado quando existem alterações relacionadas ao backend:

```yaml
on:
  push:
    branches:
      - main
    paths:
      - "backend/**"
      - "template.yaml"
      - ".github/workflows/backend.yml"

  pull_request:
    branches:
      - main
    paths:
      - "backend/**"
      - "template.yaml"
      - ".github/workflows/backend.yml"
```

Isso evita executar o pipeline quando uma alteração não possui relação com o backend ou com sua infraestrutura.

---

# 4. Job de testes

O primeiro job é responsável por executar os testes automatizados.

```yaml
test:
  runs-on: ubuntu-latest

  permissions:
    contents: read

  env:
    AWS_DEFAULT_REGION: us-east-1
```

Foi utilizado:

```yaml
permissions:
  contents: read
```

porque o job precisa apenas ler o código do repositório.

---

## 4.1 Configuração do Python

O projeto utiliza Python 3.13:

```yaml
- name: Configurar Python
  uses: actions/setup-python@v6
  with:
    python-version: "3.13"
```

A versão foi escolhida para ficar alinhada ao runtime utilizado pela Lambda:

```yaml
Runtime: python3.13
```

---

# 5. Instalação das dependências

As dependências do projeto são instaladas através do:

```text
backend/requirements.txt
```

O workflow utiliza:

```yaml
- name: Instalar dependencias
  run: |
    python -m pip install --upgrade pip
    pip install -r backend/requirements.txt
    pip install pytest
```

---

# 6. Execução dos testes

Os testes são executados dentro da pasta `backend`:

```yaml
- name: Executar testes
  working-directory: backend
  run: pytest test_lambda_function.py -v
```

O parâmetro:

```text
-v
```

faz o Pytest apresentar informações mais detalhadas sobre os testes.

---

# 7. Primeiro problema — NoRegionError

Durante a configuração do pipeline ocorreu o erro:

```text
NoRegionError: You must specify a region.
```

## Causa

O código Python utilizava o SDK da AWS (`boto3`), mas o ambiente do GitHub Actions não tinha uma região AWS definida.

---

## Correção

Foi adicionada a variável:

```yaml
env:
  AWS_DEFAULT_REGION: us-east-1
```

Com isso, o SDK passou a saber que deveria utilizar:

```text
us-east-1
```

O problema foi resolvido.

---

# 8. Job de Deploy

Depois dos testes, o segundo job executa o build e o deploy:

```yaml
deploy:
  needs: test

  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

A dependência:

```yaml
needs: test
```

garante que:

```text
Testes passaram
      ↓
Deploy pode executar
```

---

# 9. AWS SAM Build

O pipeline instala o AWS SAM CLI:

```yaml
- name: Configurar AWS SAM CLI
  uses: aws-actions/setup-sam@v2
```

Depois executa:

```yaml
- name: SAM Build
  run: sam build
```

O `sam build` prepara os recursos definidos no:

```text
template.yaml
```

para o processo de deploy.

---

# 10. Autenticação AWS utilizando OIDC

O projeto não utiliza Access Key e Secret Access Key armazenadas no GitHub.

A autenticação é realizada utilizando:

```text
GitHub Actions
      ↓
GitHub OIDC
      ↓
AWS IAM
      ↓
IAM Role
      ↓
Credenciais temporárias
```

O workflow utiliza:

```yaml
permissions:
  id-token: write
  contents: read
```

O:

```text
id-token: write
```

permite que o GitHub Actions solicite um token OIDC.

---

# 11. IAM Role utilizada

O workflow utiliza a Role:

```text
github-actions-backend-role
```

através de:

```yaml
- name: Configurar credenciais AWS via OIDC
  uses: aws-actions/configure-aws-credentials@v6
  with:
    role-to-assume: arn:aws:iam::696537703431:role/github-actions-backend-role
    aws-region: us-east-1
```

---

# 12. Problema do OIDC

Inicialmente ocorreu:

```text
Not authorized to perform sts:AssumeRoleWithWebIdentity
```

Isso significava que:

```text
GitHub → AWS
```

estava tentando assumir a Role, mas a Trust Policy da Role não aceitava aquele token.

---

# 13. Diagnóstico do OIDC

Foi utilizado temporariamente um passo de debug para descobrir os dados reais enviados pelo GitHub.

O token apresentou:

```text
OIDC issuer:
https://token.actions.githubusercontent.com

OIDC audience:
sts.amazonaws.com

OIDC subject:
repo:BarrosAmorim@24548784/cloud_resume_challenge@1357715532:ref:refs/heads/main

OIDC repository:
BarrosAmorim/cloud_resume_challenge

OIDC ref:
refs/heads/main
```

O dado mais importante foi o:

```text
sub
```

---

# 14. Correção da Trust Policy

A Trust Policy da Role foi ajustada para aceitar especificamente o repositório e a branch correta.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::696537703431:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                    "token.actions.githubusercontent.com:sub": "repo:BarrosAmorim@24548784/cloud_resume_challenge@1357715532:ref:refs/heads/main"
                }
            }
        }
    ]
}
```

Foi importante utilizar o `sub` real do projeto.

Não foi utilizado o `sub` de um projeto anterior.

---

# 15. Segurança do OIDC

A Trust Policy não foi deixada aberta para qualquer repositório.

Foi utilizado um `sub` específico:

```text
repo:BarrosAmorim@24548784/cloud_resume_challenge@1357715532:ref:refs/heads/main
```

Isso restringe a utilização da Role ao contexto esperado.

A utilização do OIDC evita armazenar credenciais permanentes da AWS no GitHub Secrets.

---

# 16. Testando o acesso AWS

Depois da autenticação OIDC, o workflow executa:

```yaml
- name: Testar acesso AWS
  run: aws sts get-caller-identity
```

Esse comando confirma que o GitHub Actions conseguiu obter credenciais AWS temporárias.

Quando essa etapa passou, ficou confirmado que o problema do OIDC estava resolvido.

---

# 17. Problema — SAM Deploy sem Stack Name

Depois que a autenticação AWS funcionou, o deploy apresentou:

```text
Error: Missing option '--stack-name'
```

## Causa

O comando utilizado era:

```bash
sam deploy --no-confirm-changeset --no-fail-on-empty-changeset
```

O projeto atual não estava fornecendo ao SAM o nome da CloudFormation Stack através da configuração utilizada pelo pipeline.

---

# 18. Correção — Stack Name

Foi adicionado:

```bash
--stack-name cloud-resume-challenge
```

O comando passou a identificar explicitamente qual stack deveria ser utilizada.

---

# 19. Problema — S3 Bucket não especificado

Depois disso ocorreu:

```text
Unable to upload artifact CloudResumeCounter referenced by CodeUri parameter of CloudResumeCounter resource.

S3 Bucket not specified
```

## Causa

O SAM precisava de um bucket S3 para armazenar os artefatos utilizados durante o deploy.

---

# 20. Correção — S3 Bucket

Foi adicionado:

```bash
--s3-bucket sam-artifacts-rafael-2026
```

O SAM passou então a utilizar esse bucket para armazenar os artefatos.

O upload foi realizado com sucesso.

---

# 21. Problema — CAPABILITY_IAM

Depois do upload dos artefatos, o CloudFormation retornou:

```text
Requires capabilities : [CAPABILITY_IAM]
```

## Causa

O template SAM possui recursos que resultam na criação ou alteração de recursos IAM.

O CloudFormation exige uma confirmação explícita para permitir esse tipo de operação.

---

# 22. Correção — CAPABILITY_IAM

Foi adicionada a opção:

```bash
--capabilities CAPABILITY_IAM
```

Com isso, o SAM passou a informar ao CloudFormation que o deploy possui autorização explícita para trabalhar com recursos IAM.

---

# 23. Comando final do SAM Deploy

O comando final ficou:

```yaml
- name: SAM Deploy
  run: |
    sam deploy \
      --stack-name cloud-resume-challenge \
      --region us-east-1 \
      --s3-bucket sam-artifacts-rafael-2026 \
      --capabilities CAPABILITY_IAM \
      --no-confirm-changeset \
      --no-fail-on-empty-changeset
```

---

# 24. Pipeline final

O pipeline completo ficou:

```text
git push
    ↓
GitHub Actions
    ↓
Checkout
    ↓
Configuração Python
    ↓
Instalação das dependências
    ↓
Pytest
    ↓
TESTE ✅
    ↓
SAM Build
    ↓
GitHub OIDC
    ↓
AWS IAM Role
    ↓
STS GetCallerIdentity
    ↓
SAM Deploy
    ↓
Upload dos artefatos para S3
    ↓
CloudFormation
    ↓
Lambda
API Gateway
DynamoDB
    ↓
DEPLOY ✅
```

---

# 25. Workflow final

O arquivo:

```text
.github/workflows/backend.yml
```

ficou:

```yaml
name: Backend CI/CD

on:
  push:
    branches:
      - main
    paths:
      - "backend/**"
      - "template.yaml"
      - ".github/workflows/backend.yml"

  pull_request:
    branches:
      - main
    paths:
      - "backend/**"
      - "template.yaml"
      - ".github/workflows/backend.yml"

jobs:
  # ==========================================
  # JOB 1 - TESTES
  # ==========================================
  test:
    runs-on: ubuntu-latest

    permissions:
      contents: read

    env:
      AWS_DEFAULT_REGION: us-east-1

    steps:
      - name: Checkout do codigo
        uses: actions/checkout@v6

      - name: Configurar Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.13"

      - name: Instalar dependencias
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt
          pip install pytest

      - name: Executar testes
        working-directory: backend
        run: pytest test_lambda_function.py -v

  # ==========================================
  # JOB 2 - BUILD E DEPLOY
  # ==========================================
  deploy:
    needs: test

    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    runs-on: ubuntu-latest

    permissions:
      id-token: write
      contents: read

    env:
      AWS_DEFAULT_REGION: us-east-1

    steps:
      - name: Checkout do codigo
        uses: actions/checkout@v6

      - name: Configurar Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.13"

      - name: Configurar AWS SAM CLI
        uses: aws-actions/setup-sam@v2

      - name: SAM Build
        run: sam build

      # ==========================================
      # AWS OIDC
      # ==========================================
      - name: Configurar credenciais AWS via OIDC
        uses: aws-actions/configure-aws-credentials@v6
        with:
          role-to-assume: arn:aws:iam::696537703431:role/github-actions-backend-role
          aws-region: us-east-1

      - name: Testar acesso AWS
        run: aws sts get-caller-identity

      # ==========================================
      # SAM DEPLOY
      # ==========================================
      - name: SAM Deploy
        run: |
          sam deploy \
            --stack-name cloud-resume-challenge \
            --region us-east-1 \
            --s3-bucket sam-artifacts-rafael-2026 \
            --capabilities CAPABILITY_IAM \
            --no-confirm-changeset \
            --no-fail-on-empty-changeset
```

---

# 26. Validação final

Após o pipeline ficar verde no GitHub Actions, foi realizado um teste direto no endpoint da API:

```bash
curl https://cwz64tvvd0.execute-api.us-east-1.amazonaws.com/count
```

Resultado:

```json
{
  "count": 10
}
```

Isso confirmou que o backend continuava funcionando após o deploy automatizado.

---

# 27. Resultado final

O CI/CD do backend foi concluído com sucesso.

```text
GitHub
  │
  ▼
GitHub Actions
  │
  ├── Pytest ✅
  │
  ├── SAM Build ✅
  │
  ├── OIDC ✅
  │
  ├── IAM Role ✅
  │
  └── SAM Deploy ✅
          │
          ▼
    CloudFormation
          │
    ┌─────┼─────┐
    ▼     ▼     ▼
 Lambda  API   DynamoDB
    │
    ▼
Backend funcionando ✅
```

---

# 28. Principais aprendizados

Durante este laboratório foram praticados:

* GitHub Actions
* CI/CD
* Jobs e Steps
* GitHub Actions Permissions
* Pytest
* Python
* AWS SAM
* SAM Build
* SAM Deploy
* CloudFormation
* IAM
* IAM Trust Policy
* GitHub OIDC
* Credenciais temporárias AWS
* AWS STS
* S3 para artefatos
* Lambda
* API Gateway
* DynamoDB
* Troubleshooting de pipeline

---

# 29. Erros encontrados e soluções

| Erro                                                      | Causa                             | Solução                                 |
| --------------------------------------------------------- | --------------------------------- | --------------------------------------- |
| `NoRegionError`                                           | Região AWS não definida           | `AWS_DEFAULT_REGION: us-east-1`         |
| `Not authorized to perform sts:AssumeRoleWithWebIdentity` | Trust Policy OIDC incorreta       | Corrigir `sub` da Trust Policy          |
| `Missing option '--stack-name'`                           | Stack não especificada            | `--stack-name cloud-resume-challenge`   |
| `S3 Bucket not specified`                                 | Bucket de artefatos não informado | `--s3-bucket sam-artifacts-rafael-2026` |
| `Requires capabilities : [CAPABILITY_IAM]`                | Template cria/usa recursos IAM    | `--capabilities CAPABILITY_IAM`         |

---

# 30. Modelo para próximos laboratórios

Este projeto pode ser utilizado como referência para futuros laboratórios com AWS SAM.

Entretanto, os valores específicos devem ser alterados conforme o novo projeto.

Por exemplo:

```text
Stack Name
S3 Artifact Bucket
IAM Role
Repository
Branch
AWS Region
```

O conceito permanece:

```text
Test
 ↓
Build
 ↓
OIDC
 ↓
AWS
 ↓
Deploy
```

Para laboratórios, é interessante manter os parâmetros do `sam deploy` explícitos, pois isso facilita o aprendizado e permite entender exatamente o que cada opção faz.

Em projetos mais maduros, parte dessas configurações pode ser centralizada em um `samconfig.toml`.

---

# 31. Status

**CI/CD Backend — CONCLUÍDO ✅**

Pipeline validado com:

* Testes automatizados passando
* GitHub Actions funcionando
* OIDC funcionando
* IAM Role funcionando
* SAM Build funcionando
* SAM Deploy funcionando
* CloudFormation funcionando
* API Gateway funcionando
* Lambda funcionando
* DynamoDB funcionando
* Endpoint `/count` validado
* Contador retornando `{"count": 10}`
