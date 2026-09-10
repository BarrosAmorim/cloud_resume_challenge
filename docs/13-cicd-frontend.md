# Etapa 13: CI/CD - Frontend

## Objetivo

Implementar um pipeline de CI/CD para o frontend do Cloud Resume Challenge utilizando:

* GitHub Actions
* GitHub OIDC
* AWS IAM
* Amazon S3
* Amazon CloudFront

O objetivo é permitir que um `push` na branch `main` execute automaticamente:

1. Checkout do código.
2. Autenticação na AWS utilizando GitHub OIDC.
3. Assunção de uma IAM Role específica para o frontend.
4. Upload dos arquivos do frontend para o Amazon S3.
5. Invalidação do cache do CloudFront.

A autenticação utiliza OIDC, portanto não é necessário armazenar Access Key e Secret Access Key da AWS como secrets de longa duração no GitHub. O GitHub gera um token OIDC temporário e a AWS utiliza esse token para permitir que o workflow assuma a IAM Role.

---

# 1. Arquitetura

```text
GitHub Repository
BarrosAmorim/cloud-resume-challenge-aws
        |
        | push na branch main
        v
GitHub Actions
        |
        | GitHub OIDC
        v
IAM Identity Provider
token.actions.githubusercontent.com
        |
        | AssumeRoleWithWebIdentity
        v
github-actions-frontend-role
        |
        v
GitHubActionsFrontendDeployPolicy
        |
        +-------------------------+
        |                         |
        v                         v
Amazon S3                  Amazon CloudFront
        |                         |
        | upload                  | invalidation
        v                         v
Frontend                  Cache atualizado
```

---

# 2. Recursos utilizados

| Recurso                 | Valor                                     |
| ----------------------- | ----------------------------------------- |
| Repositório             | `BarrosAmorim/cloud-resume-challenge-aws` |
| Branch                  | `main`                                    |
| Região AWS              | `us-east-1`                               |
| IAM Role                | `github-actions-frontend-role`            |
| IAM Policy              | `GitHubActionsFrontendDeployPolicy`       |
| S3 Bucket               | `cloud-resume-challenge-rafael-2026`      |
| CloudFront Distribution | `E1LPZAUDPQIFSS`                          |
| OIDC Provider           | `token.actions.githubusercontent.com`     |

---

# 3. Pré-requisito — GitHub OIDC

## 3.1 Verificar se o provedor OIDC já existe

Como o projeto já possui uma integração GitHub Actions + AWS, primeiro verificar se o provedor OIDC do GitHub já foi criado.

No console da AWS:

```text
IAM
  |
  +-- Provedores de identidade
```

Localizar:

```text
token.actions.githubusercontent.com
```

O provedor deve utilizar:

```text
URL:
https://token.actions.githubusercontent.com

Audience:
sts.amazonaws.com
```

### Importante

Não é necessário criar outro provedor OIDC para o frontend.

O mesmo provedor pode ser utilizado por diferentes IAM Roles.

Neste projeto existem roles separadas para diferentes responsabilidades.

```text
GitHub OIDC Provider
        |
        +-- github-actions-backend-role
        |
        +-- github-actions-frontend-role
```

O OIDC permite que o GitHub Actions autentique na AWS sem armazenar credenciais AWS de longa duração no GitHub.

---

# 4. Criar a política do frontend

A Role do frontend não deve utilizar políticas administrativas como:

```text
AmazonS3FullAccess
AWSCloudFormationFullAccess
AWSLambda_FullAccess
```

Essas permissões são desnecessárias para o deploy dos arquivos estáticos.

O frontend precisa somente das permissões necessárias para:

```text
S3
  |
  +-- ListBucket
  +-- GetObject
  +-- PutObject
  +-- DeleteObject

CloudFront
  |
  +-- CreateInvalidation
```

Isso segue o princípio do menor privilégio.

---

# 5. Criar GitHubActionsFrontendDeployPolicy

No console AWS:

```text
IAM
  |
  +-- Políticas
      |
      +-- Criar política
```

Selecionar:

```text
JSON
```

Inserir:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3BucketAccess",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::cloud-resume-challenge-rafael-2026"
    },
    {
      "Sid": "S3ObjectAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::cloud-resume-challenge-rafael-2026/*"
    },
    {
      "Sid": "CloudFrontInvalidation",
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateInvalidation"
      ],
      "Resource": "arn:aws:cloudfront::696537703431:distribution/E1LPZAUDPQIFSS"
    }
  ]
}
```

## 5.1 Nome da política

Utilizar:

```text
GitHubActionsFrontendDeployPolicy
```

Descrição:

```text
Permissões mínimas para deploy do frontend via GitHub Actions
```

Clicar em:

```text
Criar política
```

---

# 6. Entendendo a política

A política possui três blocos.

## 6.1 Listar o bucket

```json
{
  "Sid": "S3BucketAccess",
  "Effect": "Allow",
  "Action": [
    "s3:ListBucket"
  ],
  "Resource": "arn:aws:s3:::cloud-resume-challenge-rafael-2026"
}
```

O `ListBucket` utiliza o ARN do bucket sem `/*`.

```text
arn:aws:s3:::cloud-resume-challenge-rafael-2026
```

---

## 6.2 Trabalhar com os objetos

```json
{
  "Sid": "S3ObjectAccess",
  "Effect": "Allow",
  "Action": [
    "s3:PutObject",
    "s3:GetObject",
    "s3:DeleteObject"
  ],
  "Resource": "arn:aws:s3:::cloud-resume-challenge-rafael-2026/*"
}
```

Aqui o `/*` é necessário porque as ações trabalham sobre os objetos dentro do bucket.

Essas permissões permitem:

```text
PutObject
    |
    +-- enviar arquivos

GetObject
    |
    +-- acessar objetos

DeleteObject
    |
    +-- remover arquivos antigos
```

---

## 6.3 Invalidar o CloudFront

```json
{
  "Sid": "CloudFrontInvalidation",
  "Effect": "Allow",
  "Action": [
    "cloudfront:CreateInvalidation"
  ],
  "Resource": "arn:aws:cloudfront::696537703431:distribution/E1LPZAUDPQIFSS"
}
```

Essa permissão permite que o GitHub Actions solicite uma invalidação do cache da distribuição específica.

Não é necessário conceder acesso amplo ao CloudFront.

---

# 7. Criar a IAM Role

No console AWS:

```text
IAM
  |
  +-- Funções
      |
      +-- Criar função
```

Selecionar como entidade confiável:

```text
Identidade da Web
```

Selecionar o provedor:

```text
token.actions.githubusercontent.com
```

Audience:

```text
sts.amazonaws.com
```

Configurar o repositório:

```text
BarrosAmorim/cloud-resume-challenge-aws
```

Branch:

```text
main
```

Nome da função:

```text
github-actions-frontend-role
```

A AWS permite configurar a Role do GitHub OIDC limitando a organização, repositório e branch.

---

# 8. Adicionar a política à Role

Depois de criar a Role:

```text
IAM
  |
  +-- Funções
      |
      +-- github-actions-frontend-role
```

Abrir:

```text
Permissões
```

Selecionar:

```text
Adicionar permissões
```

Depois:

```text
Anexar políticas
```

Procurar:

```text
GitHubActionsFrontendDeployPolicy
```

Selecionar e adicionar.

A Role deverá possuir somente a política criada para o frontend.

---

# 9. Política de confiança

Abrir:

```text
IAM
  |
  +-- Funções
      |
      +-- github-actions-frontend-role
          |
          +-- Relações de confiança
```

A política utilizada pelo projeto é:

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
          "token.actions.githubusercontent.com:sub": "repo:BarrosAmorim@24548784/cloud-resume-challenge-aws@1362598451:ref:refs/heads/main",
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        }
      }
    }
  ]
}
```

## 9.1 Por que o `sub` possui os IDs?

O GitHub passou a oferecer declarações `sub` imutáveis contendo os IDs da organização/usuário e do repositório para repositórios criados a partir de 15 de julho de 2026 ou que optaram por esse formato.

Portanto, o formato utilizado deve corresponder ao formato efetivamente emitido pelo repositório.

Neste projeto:

```text
repo:BarrosAmorim@24548784/cloud-resume-challenge-aws@1362598451:ref:refs/heads/main
```

Esse valor deve ser mantido exatamente igual ao configurado no ambiente atual.

A documentação atual do GitHub confirma o formato com IDs imutáveis.

---

# 10. Entendendo a Trust Policy

## Principal

```json
"Principal": {
  "Federated": "arn:aws:iam::696537703431:oidc-provider/token.actions.githubusercontent.com"
}
```

Indica que a identidade federada confiável é o provedor OIDC do GitHub.

---

## Action

```json
"Action": "sts:AssumeRoleWithWebIdentity"
```

Permite que uma identidade autenticada pelo OIDC assuma a Role.

---

## Audience

```json
"token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
```

Restringe o token para o público utilizado pelo AWS STS.

---

## Subject

```json
"token.actions.githubusercontent.com:sub": "repo:BarrosAmorim@24548784/cloud-resume-challenge-aws@1362598451:ref:refs/heads/main"
```

Restringe quem pode assumir a Role.

Nesse caso:

```text
Organização/usuário:
BarrosAmorim

Repositório:
cloud-resume-challenge-aws

Branch:
main
```

Essa condição é importante porque evita que qualquer repositório usando o mesmo provedor OIDC possa assumir a Role. A AWS e o GitHub recomendam restringir o `sub` na política de confiança.

---

# 11. ARN da Role

Depois da criação, copiar o ARN da Role.

Neste projeto:

```text
arn:aws:iam::696537703431:role/github-actions-frontend-role
```

Esse ARN será utilizado no workflow do GitHub Actions.

---

# 12. Configurar o GitHub Actions

O workflow precisa permitir que o GitHub solicite um token OIDC.

Adicionar:

```yaml
permissions:
  id-token: write
  contents: read
```

O `id-token: write` não concede permissões AWS ao workflow. Ele apenas permite solicitar o token OIDC utilizado para autenticação.

---

# 13. Autenticação no workflow

Utilizar:

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v6
  with:
    role-to-assume: arn:aws:iam::696537703431:role/github-actions-frontend-role
    aws-region: us-east-1
```

A action troca o token OIDC do GitHub por credenciais temporárias da AWS.

---

# 14. Deploy para o S3

Depois da autenticação:

```yaml
- name: Deploy frontend
  run: |
    aws s3 sync ./frontend s3://cloud-resume-challenge-rafael-2026 --delete
```

O comando:

```text
aws s3 sync
```

compara os arquivos locais com o conteúdo do bucket.

O parâmetro:

```text
--delete
```

remove do bucket arquivos que não existem mais no diretório local.

---

# 15. Invalidar o CloudFront

Depois do upload:

```yaml
- name: Invalidate CloudFront
  run: |
    aws cloudfront create-invalidation \
      --distribution-id E1LPZAUDPQIFSS \
      --paths "/*"
```

Isso solicita que o CloudFront invalide o cache dos arquivos.

Fluxo:

```text
Alteração no código
       |
       v
Git push
       |
       v
GitHub Actions
       |
       v
S3 sync
       |
       v
Arquivos atualizados no S3
       |
       v
CloudFront Invalidation
       |
       v
Novo conteúdo entregue
```

---

# 16. Exemplo completo do workflow

```yaml
name: Frontend CI/CD

on:
  push:
    branches:
      - main

permissions:
  id-token: write
  contents: read

env:
  AWS_REGION: us-east-1
  S3_BUCKET: cloud-resume-challenge-rafael-2026
  CLOUDFRONT_DISTRIBUTION_ID: E1LPZAUDPQIFSS

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:

      - name: Checkout repository
        uses: actions/checkout@v6

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v6
        with:
          role-to-assume: arn:aws:iam::696537703431:role/github-actions-frontend-role
          aws-region: ${{ env.AWS_REGION }}

      - name: Deploy frontend to S3
        run: |
          aws s3 sync ./frontend s3://${{ env.S3_BUCKET }} --delete

      - name: Invalidate CloudFront
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ env.CLOUDFRONT_DISTRIBUTION_ID }} \
            --paths "/*"
```

> Ajustar `./frontend` caso os arquivos do frontend estejam em outro diretório do repositório.

---

# 17. Fazer o primeiro teste

Alterar algum arquivo do frontend.

Por exemplo:

```text
frontend/index.html
```

Fazer commit:

```bash
git add .
git commit -m "test: frontend ci cd"
git push origin main
```

O GitHub Actions deverá iniciar automaticamente.

---

# 18. Validar o workflow

No GitHub:

```text
Repository
  |
  +-- Actions
      |
      +-- Frontend CI/CD
```

Verificar:

```text
Checkout repository
        |
        v
Configure AWS credentials
        |
        v
Deploy frontend to S3
        |
        v
Invalidate CloudFront
```

Todos os passos devem apresentar:

```text
✓
```

---

# 19. Validar o S3

No console AWS:

```text
S3
  |
  +-- cloud-resume-challenge-rafael-2026
```

Verificar se os arquivos do frontend foram atualizados.

---

# 20. Validar o CloudFront

No console:

```text
CloudFront
  |
  +-- E1LPZAUDPQIFSS
  |
  +-- Invalidations
```

Deve existir uma invalidação criada pelo workflow.

---

# 21. Teste de segurança

A Role do frontend deve possuir somente:

```text
S3
  |
  +-- s3:ListBucket
  +-- s3:GetObject
  +-- s3:PutObject
  +-- s3:DeleteObject

CloudFront
  |
  +-- cloudfront:CreateInvalidation
```

Não deve possuir:

```text
CloudFormation
Lambda
DynamoDB
API Gateway
IAM
```

Esses serviços pertencem a outras responsabilidades do projeto.

---

# 22. Resultado final

A arquitetura final fica:

```text
                    GitHub
                       |
                       | OIDC
                       v
          token.actions.githubusercontent.com
                       |
                       v
          github-actions-frontend-role
                       |
                       v
       GitHubActionsFrontendDeployPolicy
                       |
              +--------+--------+
              |                 |
              v                 v
             S3             CloudFront
              |                 |
              | upload          | invalidate
              v                 v
          Frontend          Cache atualizado
```

## Separação de responsabilidades

```text
BACKEND
github-actions-backend-role
        |
        +-- Lambda
        +-- DynamoDB
        +-- API Gateway
        +-- CloudFormation
        +-- outras permissões necessárias ao backend


FRONTEND
github-actions-frontend-role
        |
        +-- S3
        +-- CloudFront
```

Essa separação reduz o impacto caso uma das pipelines seja comprometida.

---

# 23. Checklist

### IAM

```text
[✓] GitHub OIDC Provider existente
[✓] github-actions-frontend-role criada
[✓] GitHubActionsFrontendDeployPolicy criada
[✓] Política anexada à Role
[✓] Trust Policy configurada
[✓] Repositório limitado
[✓] Branch main limitada
```

### S3

```text
[✓] s3:ListBucket
[✓] s3:GetObject
[✓] s3:PutObject
[✓] s3:DeleteObject
```

### CloudFront

```text
[✓] cloudfront:CreateInvalidation
```

### GitHub Actions

```text
[✓] permissions.id-token = write
[✓] permissions.contents = read
[✓] configure-aws-credentials
[✓] role-to-assume configurado
[✓] aws s3 sync
[✓] CloudFront invalidation
```

### Teste

```text
[✓] git push
[✓] Workflow executado
[✓] Autenticação OIDC funcionando
[✓] S3 atualizado
[✓] Invalidation criada
[✓] Frontend atualizado no CloudFront
```

## Resultado

O frontend passa a ter um processo de deploy automatizado:

```text
git push
   |
   v
GitHub Actions
   |
   v
OIDC
   |
   v
IAM Role
   |
   +----> S3
   |
   +----> CloudFront
```

Não são utilizadas Access Keys permanentes do usuário IAM para o GitHub Actions. O acesso AWS é obtido através de credenciais temporárias após a autenticação OIDC.
