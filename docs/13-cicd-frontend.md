# Etapa 13: CI/CD - Frontend

## Objetivo
Implementar um pipeline de CI/CD para o frontend utilizando GitHub Actions, AWS OIDC e CloudFront, automatizando o processo de deploy dos arquivos estáticos (HTML, CSS, JS) e a invalidação do cache do CloudFront.

## Status
✅ Concluído

## Recursos Utilizados
- GitHub Actions
- AWS OIDC (OpenID Connect)
- AWS IAM
- Amazon S3
- Amazon CloudFront
- AWS CLI

---

## 📋 O que é CI/CD para Frontend

**CI/CD** (Continuous Integration / Continuous Deployment) para frontend automatiza o processo de deploy do site estático.

**Analogia:** É como uma esteira de fábrica:
1. Você coloca os arquivos na esteira (`git push`)
2. A esteira envia para o S3 (`aws s3 sync`)
3. A esteira limpa o cache do CloudFront (`aws cloudfront create-invalidation`)

---

## 🏗️ Arquitetura do Pipeline

```
git push
    ↓
GitHub Actions
    ↓
Checkout
    ↓
GitHub OIDC
    ↓
AWS IAM Role
    ↓
STS GetCallerIdentity
    ↓
aws s3 sync
    ↓
S3 Bucket
    ↓
aws cloudfront create-invalidation
    ↓
CloudFront
    ↓
SITE ATUALIZADO ✅
```

---

## 📋 Passo a Passo Completo

### Parte 1: Criar a Role IAM para Frontend

#### 1.1 Criar a Role

1. No console AWS, vá em **IAM** → **Roles** → **Create role**
2. Em **"Trusted entity type"**, selecione **"Identidade Web"**
3. Preencher:

| Campo | Valor |
|-------|-------|
| **Provedor de identidade** | `token.actions.githubusercontent.com` |
| **Audience** | `sts.amazonaws.com` |
| **GitHub organization** | `BarrosAmorim` |
| **GitHub repository** | `cloud_resume_challenge` |

#### 1.2 Anexar Permissões

1. Selecione **"Attach existing policies"**
2. Pesquise e marque a política `s3-resume-bucket-access`
3. Clique em **"Next"**

#### 1.3 Nomear a Role

| Campo | Valor |
|-------|-------|
| **Role name** | `github-actions-frontend-role` |

4. Clique em **"Create role"**

#### 1.4 Trust Policy

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

#### 1.5 Permissões da Role

A política `s3-resume-bucket-access` deve conter:

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
				"dynamodb:UntagResource"
			],
			"Resource": "*"
		},
		{
			"Effect": "Allow",
			"Action": [
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

### Parte 2: Criar o Workflow

#### 2.1 Criar o arquivo `frontend.yml`

```bash
cd ~/projects/cloud_resume_challenge
nano .github/workflows/frontend.yml
```

#### 2.2 Conteúdo do `frontend.yml`

```yaml
name: Frontend CI/CD

on:
  push:
    branches:
      - main
    paths:
      - "frontend/**"
      - ".github/workflows/frontend.yml"

jobs:
  deploy:
    runs-on: ubuntu-latest

    permissions:
      id-token: write
      contents: read

    env:
      AWS_DEFAULT_REGION: us-east-1

    steps:
      - name: Checkout do codigo
        uses: actions/checkout@v6

      - name: Configurar credenciais AWS via OIDC
        uses: aws-actions/configure-aws-credentials@v6
        with:
          role-to-assume: arn:aws:iam::696537703431:role/github-actions-frontend-role
          aws-region: us-east-1

      - name: Testar acesso AWS
        run: aws sts get-caller-identity

      - name: Publicar frontend no S3
        run: aws s3 sync frontend/ s3://cloud-resume-challenge-rafael-2026 --delete

      - name: Invalidar cache do CloudFront
        run: aws cloudfront create-invalidation --distribution-id EGGP4OT7VLDC2 --paths "/*"
```

---

### Parte 3: Subir para o GitHub

```bash
cd ~/projects/cloud_resume_challenge

git add .github/workflows/frontend.yml
git commit -m "ci: adiciona workflow de deploy do frontend"
git push origin main
```

---

## 🔍 Verificação

### 1. Verificar no GitHub Actions

1. Acesse: `https://github.com/BarrosAmorim/cloud_resume_challenge/actions`
2. Veja o workflow `Frontend CI/CD` executando

### 2. Verificar o Site

1. Acesse: `https://barrosamorimd.work`
2. As mudanças devem aparecer após o pipeline concluir

### 3. Verificar a Invalidação do CloudFront

1. No console AWS, vá em **CloudFront**
2. Vá na aba **"Invalidations"**
3. Veja a invalidação criada

---

## 🐛 Problemas e Soluções

| Erro | Causa | Solução |
|------|-------|---------|
| `AccessDenied` no S3 | Role não tem permissão para o bucket | Adicionar `s3:PutObject`, `s3:GetObject`, `s3:ListBucket` |
| `AccessDenied` no CloudFront | Role não tem permissão para invalidar | Adicionar `cloudfront:CreateInvalidation` |
| `Not authorized to perform sts:AssumeRoleWithWebIdentity` | Trust Policy incorreta | Corrigir o `sub` na Trust Policy |
| `Invalidation not created` | Distribution ID incorreto | Verificar o ID da distribuição CloudFront |

---

## 📊 Resumo da Configuração

| Recurso | Configuração |
|---------|--------------|
| **Role IAM** | `github-actions-frontend-role` |
| **Provedor OIDC** | `token.actions.githubusercontent.com` |
| **Bucket S3** | `cloud-resume-challenge-rafael-2026` |
| **CloudFront Distribution ID** | `EGGP4OT7VLDC2` |
| **Workflow** | `.github/workflows/frontend.yml` |

---

## 🎯 O que o Pipeline faz

| Etapa | Comando | O que faz |
|-------|---------|-----------|
| **1. Checkout** | `actions/checkout@v6` | Baixa o código do GitHub |
| **2. OIDC** | `configure-aws-credentials` | Autentica na AWS sem chaves |
| **3. Teste** | `aws sts get-caller-identity` | Confirma a autenticação |
| **4. Sync S3** | `aws s3 sync` | Envia arquivos para o S3 |
| **5. Invalidate** | `aws cloudfront create-invalidation` | Limpa o cache do CloudFront |

---

## 🎯 Conclusão

O CI/CD do frontend foi concluído com sucesso. Agora, qualquer alteração nos arquivos do frontend dispara automaticamente:

1. ✅ Autenticação via OIDC
2. ✅ Upload dos arquivos para o S3
3. ✅ Invalidação do cache do CloudFront

**Resultado:** O site é atualizado automaticamente após cada `git push`.

---

[🏠 Voltar ao README](../README.md)