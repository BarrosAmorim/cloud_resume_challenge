# Cloud Resume Challenge — Rafael

[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)](https://github.com/BarrosAmorim/cloud_resume_challenge) [![AWS](https://img.shields.io/badge/AWS-Cloud-orange)](https://aws.amazon.com/)

Currículo online construído seguindo o **Cloud Resume Challenge**, aplicando na prática conceitos de Cloud Computing, Infraestrutura como Código, back-end serverless e CI/CD na AWS.

🔗 **Site publicado:** em breve

> 🚧 **Este projeto está em construção.** A estrutura de pastas e a documentação abaixo representam o **planejamento completo** do desafio — as etapas concluídas até o momento estão marcadas na tabela de [Progresso e Documentação](#-progresso-e-documentação). Acompanhe o progresso real pelo histórico de commits.

---

## 📑 Navegação

- [Sobre o projeto](#-sobre-o-projeto)
- [Arquitetura](#-arquitetura)
- [Tecnologias utilizadas](#-tecnologias-utilizadas)
- [Estrutura do projeto](#-estrutura-do-projeto)
- [Progresso e Documentação](#-progresso-e-documentação)
- [Segurança](#-segurança)
- [O que estou aprendendo](#-o-que-estou-aprendendo)
- [Status do projeto](#-status-do-projeto)

---

## 📖 Sobre o projeto

O Cloud Resume Challenge é um desafio prático que consiste em construir e publicar um currículo online utilizando serviços de nuvem, infraestrutura como código, controle de versão e CI/CD — do zero até produção.

Este projeto está sendo desenvolvido inteiramente na AWS, cobrindo desde a configuração inicial até a automação completa do deploy de front-end e back-end.

**Diferencial:** Todo o desenvolvimento está sendo feito em um **Raspberry Pi 5**, demonstrando que é possível trabalhar com Cloud e DevOps mesmo em ambientes de baixo custo.

---

## 🏗️ Arquitetura

```
Usuário
   │
   │ HTTPS
   ▼
seudominio.com ──(DNS via Cloudflare)
   │
   ▼
Amazon CloudFront ──(SSL via ACM)
   │
   ▼
Amazon S3 (Static Website Hosting)
   │
   ▼
index.html + style.css + script.js
   │
   │ JavaScript / fetch()
   ▼
Amazon API Gateway ── GET /count
   │
   ▼
AWS Lambda (Python) ── boto3
   │
   ▼
Amazon DynamoDB ── contador de visitantes
```

**CI/CD (dois pipelines independentes via GitHub Actions + OIDC):**

```
Backend                          Frontend
  │                                 │
  git push → backend/**            git push → frontend/**
  │                                 │
  pytest                            AWS OIDC
  │                                 │
  sam build                        S3 sync
  │                                 │
  AWS OIDC → sam deploy            CloudFront invalidation
  │                                 │
  CloudFormation                   Currículo atualizado
  (Lambda, API Gateway, DynamoDB)
```

---

## 🛠️ Tecnologias utilizadas

| Categoria                       | Tecnologias                                                                |
| --------------------------------| ---------------------------------------------------------------------------|
| **Front-end**                   | HTML, CSS, JavaScript                                                      |
| **Back-end**                    | Python (AWS Lambda), Boto3, Pytest                                         |
| **Infraestrutura AWS**          | S3, CloudFront, ACM, DynamoDB, API Gateway (HTTP API), IAM, CloudFormation |
| **IaC**                         | AWS SAM                                                                    |
| **CI/CD**                       | GitHub Actions, autenticação via OIDC (sem chaves de longa duração)        |
| **DNS**                         | Cloudflare                                                                 |
| **Versionamento**               | Git, GitHub                                                                |
| **Ambiente de desenvolvimento** | Raspberry Pi 5                                                             |

---

## 📁 Estrutura do projeto

> ℹ️ Estrutura final prevista para o projeto completo. Pastas e arquivos ainda não criados estão marcados como `(planejado)`.

```
cloud_resume_challenge/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── backend/                          
│   ├── lambda_function.py
│   └── test_lambda_function.py
│
├── .github/                          (planejado)
│   └── workflows/
│       ├── backend.yml
│       └── frontend.yml
│
├── docs/
│   ├── 01-certificacao.md
│   ├── 02-frontend.md
│   ├── 03-s3-hospedagem.md
│   ├── 04-cloudfront-https.md        
│   ├── 05-dns-cloudflare.md          
│   ├── 06-javascript-contador.md     
│   ├── 07-dynamodb.md                
│   ├── 08-api-gateway.md             
│   ├── 09-lambda-backend.md          
│   ├── 10-testes-automatizados.md    
│   ├── 11-iac-sam.md                 (planejado)
│   ├── 12-cicd-backend.md            (planejado)
│   └── 13-cicd-frontend.md           (planejado)
│
├── template.yaml                     (planejado)
├── samconfig.toml                    (planejado)
├── .gitignore
└── README.md
```

---

## 📚 Progresso e Documentação

O processo completo — incluindo passo a passo, comandos utilizados, problemas encontrados e soluções — está documentado etapa por etapa. Clique em "ver" para acessar o detalhamento de cada uma:

| Etapa | Descrição                           | Status       | Doc                                     |
| ----- | ------------------------------------| ------------ | ----------------------------------------|
| 01    | Certificação AWS                    | ✅ Concluído | [ver](docs/01-certificacao.md)         |
| 02    | Front-end — HTML e CSS              | ✅ Concluído | [ver](docs/02-frontend.md)             |
| 03    | Amazon S3 — Static Website Hosting  | ✅ Concluído | [ver](docs/03-s3-hospedagem.md)        |
| 04    | HTTPS com Amazon CloudFront         | ✅ Concluído | [ver](docs/04-cloudfront-https.md)     |
| 05    | DNS personalizado                   | ✅ Concluído | [ver](docs/05-dns-cloudflare.md)       |
| 06    | JavaScript e contador de visitantes | ✅ Concluído | [ver](docs/06-javascript-contador.md)  |
| 07    | Banco de dados — DynamoDB           | ✅ Concluído | [ver](docs/07-dynamodb.md)             |
| 08    | API — API Gateway                   | ✅ Concluído | [ver](docs/08-api-gateway.md)          |
| 09    | Back-end — Python/Lambda            | ✅ Concluído | [ver](docs/09-lambda-backend.md)       |
| 10    | Testes automatizados                | ✅ Concluído | [ver](docs/10-testes-automatizados.md) |
| 11    | Infrastructure as Code — AWS SAM    | ⬜ Pendente  | _(planejado)_                          |
| 12    | CI/CD — Back-end                    | ⬜ Pendente  | _(planejado)_                          |
| 13    | CI/CD — Front-end                   | ⬜ Pendente  | _(planejado)_                          |
| —     | Blog post                           | ⬜ Pendente  | _(planejado)_                          |

---

## 🔒 Segurança

- Autenticação do GitHub Actions com a AWS via **OIDC**, sem armazenamento de credenciais de longa duração (`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`) no repositório.
- Trust Policy das IAM Roles restrita ao repositório e branch específicos.
- Permissões de IAM Role segmentadas por pipeline (backend e frontend possuem roles distintas, cada uma limitada aos recursos que realmente utiliza).
- Bucket S3 com bloqueio de acesso público desativado apenas onde necessário, com política restrita a `s3:GetObject`.
- Aplicação do princípio do menor privilégio em todas as permissões IAM.

---

## 🧠 O que estou aprendendo

Este projeto está sendo utilizado como laboratório prático para consolidar conhecimentos em:

- Arquitetura serverless na AWS (S3, CloudFront, API Gateway, Lambda, DynamoDB)
- Infrastructure as Code com AWS SAM e CloudFormation
- CI/CD com GitHub Actions e autenticação federada via OIDC
- Testes automatizados em Python com Pytest e mocks
- Diagnóstico e resolução de problemas reais de DNS, IAM e permissões
- Desenvolvimento em ambiente Raspberry Pi 5

---

## 🚧 Status do projeto

🚧 **Em desenvolvimento** — próxima etapa: HTTPS com Amazon CloudFront.

---

## 👨‍💻 Autor

**Rafael (Barros Amorim)** - [GitHub](https://github.com/BarrosAmorim) | LinkedIn: _(adicionar link)_

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](https://github.com/BarrosAmorim/cloud_resume_challenge/blob/main/LICENSE) para mais detalhes.

---

## 🙏 Agradecimentos

- [Forrest Brazeal](https://forrestbrazeal.com/) pelo desafio [Cloud Resume Challenge](https://cloudresumechallenge.dev/)
- Comunidade AWS e DevOps que compartilha conhecimento diariamente
- A todos que contribuíram com dicas e feedback durante o desenvolvimento
