# Etapa 03: Hospedagem no Amazon S3

## Objetivo
Hospedar o currículo estático utilizando o Amazon S3 como servidor web, aplicando boas práticas de segurança com um usuário dedicado e permissões específicas.

## Status
✅ Concluído

## Recursos Utilizados
- Amazon S3 (Simple Storage Service)
- AWS CLI
- AWS IAM (Identity and Access Management)

---

## 🔒 Configuração de Segurança (IAM)

Antes de hospedar o site, criamos uma estrutura de segurança completa para garantir que o usuário que faria o upload tivesse **apenas as permissões necessárias** (princípio do menor privilégio).

### 1. Criação da Política Customizada

**Nome da política:** `s3-resume-bucket-access`

**Descrição:** Permite operações específicas apenas no bucket `cloud-resume-challenge-rafael-2026`

**JSON da política:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::cloud-resume-challenge-rafael-2026",
                "arn:aws:s3:::cloud-resume-challenge-rafael-2026/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:CreateBucket",
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::sam-artifacts-rafael-2026",
                "arn:aws:s3:::sam-artifacts-rafael-2026/*"
            ]
        }
    ]
}
```

**Permissões concedidas e seus usos:**

| Ação | Descrição | Necessidade no projeto |
|------|-----------|------------------------|
| `s3:PutObject` | Fazer upload/upload de arquivos | ✅ Necessário para enviar o site |
| `s3:GetObject` | Ler/baixar arquivos | ✅ Necessário para testar e verificar |
| `s3:DeleteObject` | Excluir arquivos | ✅ Necessário para atualizações futuras |
| `s3:ListBucket` | Listar conteúdo do bucket | ✅ Necessário para verificar arquivos |

### 2. Criação do Grupo

**Nome do grupo:** `s3-website-access`

**Política anexada:** `s3-resume-bucket-access`

**Motivo:** Grupos facilitam o gerenciamento de permissões. Se no futuro outro usuário precisar das mesmas permissões, basta adicioná-lo a este grupo.

### 3. Criação do Usuário

**Nome do usuário:** `cloud-resume-challenge-rafael-2026`

**Tipo de acesso:** Apenas programático (CLI)

**Acesso ao Console:** ❌ Desabilitado (mais seguro)

**Grupo:** `s3-website-access`

**Motivo:** O usuário foi criado exclusivamente para uso via AWS CLI, sem acesso ao console AWS, reduzindo a superfície de ataque.

### 4. Geração de Chaves de Acesso

Foi gerado um par de chaves para o usuário:

| Tipo | Descrição |
|------|-----------|
| **Access Key ID** | Identificador público (ex: AKIA...) |
| **Secret Access Key** | Chave privada (mostrada apenas uma vez) |

⚠️ **Importante:** A chave secreta foi salva em local seguro e nunca será compartilhada ou versionada no código.

---

## 🚀 Configuração AWS CLI no Raspberry Pi

Após criar o usuário e gerar as chaves, configuramos a AWS CLI no Raspberry Pi para usar essas credenciais:

```bash
aws configure
```

**Dados informados:**

| Parâmetro | Valor |
|-----------|-------|
| AWS Access Key ID | [AKIA... - chave gerada] |
| AWS Secret Access Key | [chave secreta gerada] |
| Default region name | us-east-1 |
| Default output format | json |

### Teste de conexão

```bash
aws sts get-caller-identity
```

**Resultado esperado:**
```json
{
    "UserId": "XXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/cloud-resume-challenge-rafael-2026"
}
```

---

## 📦 Deploy do Site no S3

### 1. Criação do Bucket

**Nome do bucket:** `cloud-resume-challenge-rafael-2026`

**Região:** `us-east-1`

**Acesso:** Público (necessário para site estático)

### 2. Upload dos Arquivos

Comando utilizado para subir os arquivos:

```bash
aws s3 sync frontend/ s3://cloud-resume-challenge-rafael-2026/ --region us-east-1
```

**Saída esperada:**
```
upload: frontend/index.html to s3://cloud-resume-challenge-rafael-2026/index.html
upload: frontend/style.css to s3://cloud-resume-challenge-rafael-2026/style.css
upload: frontend/script.js to s3://cloud-resume-challenge-rafael-2026/script.js
```

### 3. Verificação

```bash
aws s3 ls s3://cloud-resume-challenge-rafael-2026/
```

**Saída esperada:**
```
2026-01-XX  XX:XX:XX    3XXX  index.html
2026-01-XX  XX:XX:XX    2XXX  style.css
2026-01-XX  XX:XX:XX      XXX  script.js
```

---

## ⚙️ Configuração do Site Estático no S3

### 1. Ativação da Hospedagem

Pelo console AWS, nas propriedades do bucket:

| Configuração | Valor |
|--------------|-------|
| Hospedagem de site estático | Ativado |
| Documento de índice | `index.html` |
| Documento de erro | `error.html` |
| Regras de redirecionamento | Nenhuma |

### 2. Política de Bucket (Acesso Público)

Para permitir que o site seja acessado publicamente, foi adicionada a seguinte política:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::cloud-resume-challenge-rafael-2026/*"
        }
    ]
}
```

### 3. Bloqueio de Acesso Público

**Ação:** Todas as opções de bloqueio de acesso público foram **desativadas** para permitir a visualização do site.

---

## 🌐 URL do Site

O site está acessível na seguinte URL:

```
http://cloud-resume-challenge-rafael-2026.s3-website-us-east-1.amazonaws.com
```

---

## 🐛 Problemas e Soluções

### Erro 1: `403 Forbidden - Access Denied`

**Cenário:** Ao tentar acessar a URL do site, retornava erro 403.

**Causa:** O bucket não estava público - faltava a política de bucket permitindo acesso público e/ou o bloqueio de acesso público estava ativado.

**Solução:** 
1. Adicionar política de bucket permitindo `s3:GetObject` para `Principal: "*"`
2. Desativar o bloqueio de acesso público nas configurações do bucket

**Resultado:** Site ficou acessível publicamente.

---

## 📊 Resumo dos Recursos Criados

| Recurso | Nome | Finalidade |
|---------|------|------------|
| **Política IAM** | `s3-resume-bucket-access` | Define permissões para o bucket |
| **Grupo IAM** | `s3-website-access` | Agrupa permissões para usuários |
| **Usuário IAM** | `cloud-resume-challenge-rafael-2026` | Usuário dedicado para o projeto |
| **Bucket S3** | `cloud-resume-challenge-rafael-2026` | Hospeda o site estático |

---

## 🎯 Conclusão

O site está hospedado e acessível via HTTP com as seguintes características:

✅ Segurança: usuário dedicado com permissões restritas  
✅ Boas práticas: uso de grupos IAM e política customizada  
✅ Deploy via CLI: upload automatizado dos arquivos  
✅ Site público: acessível via URL do S3

**Próximo passo:** Configurar HTTPS com Amazon CloudFront (Etapa 04).

---

[🏠 Voltar ao README](../README.md)