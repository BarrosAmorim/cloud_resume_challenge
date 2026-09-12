# CI/CD do Backend — GitHub Actions + AWS SAM + OIDC

# Criação do GitHub OIDC e IAM Role

Para permitir que o GitHub Actions realize o deploy na AWS sem utilizar Access Keys, foi configurada uma integração entre o GitHub Actions e o AWS IAM utilizando **OpenID Connect (OIDC)**.

A configuração possui duas partes:

1. Criar o provedor de identidade OIDC do GitHub.
2. Criar uma IAM Role que o GitHub Actions poderá assumir.

---

## 1. Criar o provedor de identidade OIDC

### Objetivo

O provedor OIDC permite que a AWS reconheça e confie nos tokens de identidade emitidos pelo GitHub Actions.

No Console da AWS:

**IAM → Identity providers → Add provider**

Na tela **Adicionar provedor de identidade**, selecionar:

```text
Tipo de provedor:
OpenID Connect
```

Preencher os campos:

```text
URL do provedor:
https://token.actions.githubusercontent.com

Público:
sts.amazonaws.com
```

A configuração fica:

```text
GitHub Actions
      │
      │ Token OIDC
      ▼
https://token.actions.githubusercontent.com
      │
      ▼
AWS IAM
```

Após preencher os campos, clicar em:

**Adicionar provedor**

O provedor criado será:

```text
token.actions.githubusercontent.com
```

---

# 2. Criar a IAM Role para o GitHub Actions

### Objetivo

A Role será assumida temporariamente pelo GitHub Actions através do OIDC para executar o deploy do backend.

No Console da AWS:

**IAM → Roles → Create role**

Na tela **Selecionar entidade confiável**, escolher:

```text
Política de confiança personalizada
```

Isso permite definir manualmente quais tokens do GitHub terão permissão para assumir a Role.

---

## 3. Configurar a Trust Policy

Na política de confiança personalizada, utilizar:

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
          "token.actions.githubusercontent.com:sub": "repo:BarrosAmorim/cloud-resume-challenge-aws:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

### Restrição do repositório

O campo `sub` foi configurado para aceitar somente:

```text
repo:BarrosAmorim/cloud-resume-challenge-aws:ref:refs/heads/main
```

Isso significa que a Role está restrita ao:

```text
Repositório:
BarrosAmorim/cloud-resume-challenge-aws

Branch:
main
```

A estrutura da autenticação fica:

```text
GitHub Actions
      │
      │ OIDC Token
      ▼
GitHub OIDC
      │
      │ AssumeRoleWithWebIdentity
      ▼
github-actions-backend-role
      │
      ▼
AWS
```

---

# 4. Nome da Role

Na etapa de configuração da Role, utilizar:

```text
github-actions-backend-role
```

Depois finalizar a criação com:

**Create role**

---

# 5. Permissões da Role

Foram adicionadas as seguintes políticas gerenciadas pela AWS:

```text
AmazonS3FullAccess
AWSCloudFormationFullAccess
AWSLambda_FullAccess
```

Essas permissões permitem que o GitHub Actions:

* utilize o bucket S3 utilizado pelo SAM;
* crie e atualize recursos através do CloudFormation;
* faça o deploy e atualização da função Lambda.

### Observação

Essas permissões são utilizadas neste laboratório para simplificar a configuração do CI/CD. Em um ambiente de produção, o ideal seria aplicar o princípio do **menor privilégio (Least Privilege)** e restringir as permissões aos recursos e ações realmente necessários.

---

# 6. Configuração final

Ao final desta etapa, a AWS possui:

### Provedor OIDC

```text
token.actions.githubusercontent.com
```

### IAM Role

```text
github-actions-backend-role
```

### Repositório autorizado

```text
BarrosAmorim/cloud-resume-challenge-aws
```

### Branch autorizada

```text
main
```

### Fluxo de autenticação

```text
GitHub Actions
      │
      │ OIDC
      ▼
token.actions.githubusercontent.com
      │
      ▼
AWS IAM
      │
      │ AssumeRoleWithWebIdentity
      ▼
github-actions-backend-role
      │
      ├── S3
      ├── CloudFormation
      └── Lambda
```

Com essa configuração, o GitHub Actions pode autenticar na AWS **sem armazenar Access Key e Secret Access Key como secrets do GitHub**.

---

# 7. Autenticação AWS utilizando OIDC

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

# 8. IAM Role utilizada

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

# 9. Correção da Trust Policy

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

### Consulta à API do GitHub para validação do repositório

Durante o diagnóstico da autenticação OIDC, foi consultada a API pública do GitHub para confirmar os dados do repositório utilizado pelo GitHub Actions:

`https://api.github.com/repos/BarrosAmorim/cloud-resume-challenge-aws`

A resposta permitiu confirmar:

* `full_name`: `BarrosAmorim/cloud-resume-challenge-aws`
* `owner.id`: `24548784`
* `repository.id`: `1362598451`

Esses valores são identificadores internos utilizados pelo GitHub. A consulta foi útil para confirmar que o workflow estava associado ao repositório correto.

É importante destacar que o `sub` utilizado na Trust Policy do IAM **não foi montado utilizando esses IDs**. Para este projeto, o valor que funcionou foi:

```text
repo:BarrosAmorim/cloud-resume-challenge-aws:ref:refs/heads/main
```

A Trust Policy foi então configurada para permitir que somente workflows desse repositório, executados a partir da branch `main`, assumissem a IAM Role por meio do GitHub OIDC.

A configuração foi validada posteriormente executando o GitHub Actions com sucesso.


---

# 10. Segurança do OIDC

A Trust Policy não foi deixada aberta para qualquer repositório.

Foi utilizado um `sub` específico:

```text
repo:BarrosAmorim@24548784/cloud_resume_challenge@1357715532:ref:refs/heads/main
```

Isso restringe a utilização da Role ao contexto esperado.

A utilização do OIDC evita armazenar credenciais permanentes da AWS no GitHub Secrets.

---

# 11. Pipeline final

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

# 12. Workflow final

Criar este arquivo

```text
.github/workflows/backend.yml
```

E adicionar:

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
            --no-confirm-changeset \
            --no-fail-on-empty-changeset
```
Fazer o commit do arquivo backend.yml, e verificar Actions no Github
---

# 13. Validação final

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

# 14. Resultado final

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

# 15. Modelo para próximos laboratórios

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

---

# 16. Status

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
