# Etapa 03 — S3: Armazenamento do currículo

## Objetivo

Nesta etapa será criado o armazenamento do frontend do projeto **Currículo Nuvem** utilizando Amazon S3.

Objetivos:

- Criar um bucket S3 privado.
- Manter o **Block Public Access** ativado.
- Criar um usuário IAM dedicado ao projeto.
- Criar um grupo IAM.
- Criar uma política IAM personalizada seguindo o princípio de **Least Privilege**.
- Associar a política ao grupo.
- Criar uma chave de acesso para a AWS CLI.
- Configurar um profile específico na AWS CLI.
- Validar as permissões pela linha de comando.
- Enviar os arquivos do frontend para o bucket.

> **Importante:** nesta etapa o bucket **não será público**. O acesso público ao currículo será configurado posteriormente pelo **Amazon CloudFront**, mantendo o bucket S3 privado.

---

## Arquitetura desta etapa

```text
Usuário IAM
curriculo-nuvem
        |
        v
Grupo IAM
curriculo-nuvem-group
        |
        v
Política IAM
curriculo-nuvem-s3-policy
        |
        v
Bucket S3 privado
curriculo-nuvem-s3
        |
        v
AWS CLI
        |
        v
Upload do frontend
```

Na próxima etapa:

```text
Visitante
    |
    v
CloudFront
    |
    v
S3 privado
```

---

## 1. Criar o bucket S3

Acesse:

`AWS Console → S3 → Buckets → Create bucket`

**Nome**
```
curriculo-nuvem-s3
```

**Região**
```
US East (N. Virginia) — us-east-1
```

**Object Ownership**

Mantenha:
- ACLs disabled
- Bucket owner enforced

**Block Public Access**

Mantenha:
- Block all public access

Todas as opções devem permanecer ativadas.

> Não desative o bloqueio de acesso público.

**Versioning**

Para este laboratório, pode permanecer desativado.

**Encryption**

Mantenha a criptografia padrão do S3.

Depois clique em:

`Create bucket`

---

## 2. Verificar o bucket

Abra:

`S3 → Buckets → curriculo-nuvem-s3`

- O bucket deverá estar vazio neste momento.
- O acesso público continuará bloqueado.

---

## 3. Criar o usuário IAM

Acesse:

`IAM → Users → Create users`

Nome:
```
curriculo-nuvem
```

- O usuário será utilizado pela AWS CLI.
- Não é necessário habilitar acesso ao AWS Management Console.
- As permissões serão concedidas por meio de um grupo IAM.

---

## 4. Criar o grupo IAM

Acesse:

`IAM → User groups → Create group`

Nome:
```
curriculo-nuvem-group
```

Adicione o usuário:
```
curriculo-nuvem
```

A estrutura será:

```text
curriculo-nuvem
        |
        v
curriculo-nuvem-group
```

---

## 5. Criar a política IAM personalizada

Acesse:

`IAM → Policies → Create policy`

Selecione o serviço: **S3**

Utilize o editor JSON.

Nome:
```
curriculo-nuvem-s3-policy
```

Use a política:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListResumeBucket",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::curriculo-nuvem-s3"
    },
    {
      "Sid": "ManageResumeObjects",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::curriculo-nuvem-s3/*"
    }
  ]
}
```

### Entendendo a política

**Permissão no bucket**

`s3:ListBucket`

Aplica-se a:
```
arn:aws:s3:::curriculo-nuvem-s3
```

Permite listar os objetos existentes no bucket.

**Permissões nos objetos**

`s3:GetObject`, `s3:PutObject`, `s3:DeleteObject`

Aplicam-se a:
```
arn:aws:s3:::curriculo-nuvem-s3/*
```

Significado:
- `GetObject` → baixar/ler objeto
- `PutObject` → enviar/criar/sobrescrever objeto
- `DeleteObject` → excluir objeto

### Diferença entre os ARNs

```text
arn:aws:s3:::curriculo-nuvem-s3
        |
        └── Bucket
            └── ListBucket


arn:aws:s3:::curriculo-nuvem-s3/*
        |
        └── Objetos
            ├── GetObject
            ├── PutObject
            └── DeleteObject
```

Essa separação evita conceder permissões administrativas desnecessárias.

---

## 6. Associar a política ao grupo

Acesse:

`IAM → User groups → curriculo-nuvem-group → Permissions`

Associe:
```
curriculo-nuvem-s3-policy
```

O usuário receberá as permissões através do grupo:

```text
curriculo-nuvem
        |
        v
curriculo-nuvem-group
        |
        v
curriculo-nuvem-s3-policy
        |
        v
curriculo-nuvem-s3
```

Na página do usuário, a política deverá aparecer como:

`Anexado via: curriculo-nuvem-group`

---

## 7. Criar a chave de acesso

Acesse:

`IAM → Users → curriculo-nuvem → Security credentials`

Na seção **Access keys**, clique em:

`Create access key`

Selecione a opção relacionada à:

`Command Line Interface (CLI)`

A AWS fornecerá:
- Access key ID
- Secret access key

> **Atenção:** nunca publique a Secret Access Key no GitHub, código, README, commits ou screenshots.
>
> Se você for salvar credenciais em arquivo local (ex: `.env`, `credentials`, `config.json`), adicione essas entradas ao `.gitignore` do repositório **antes** de criar o arquivo — assim evita o vazamento acidental no primeiro commit. Exemplo de linhas no `.gitignore`:
> ```
> .env
> *.credentials
> **/credentials
> aws-credentials*
> ```

---

## 8. Configurar o profile na AWS CLI

No Raspberry Pi:

```bash
aws configure --profile curriculo-nuvem
```

Informe:
```
AWS Access Key ID: SUA_ACCESS_KEY
AWS Secret Access Key: SUA_SECRET_KEY
Default region name: us-east-1
Default output format: json
```

---

## 9. Ativar o profile

No terminal atual:

```bash
export AWS_PROFILE=curriculo-nuvem
```

Verifique:

```bash
echo $AWS_PROFILE
```

Resultado esperado:
```
curriculo-nuvem
```

Também é possível especificar o profile individualmente:

```bash
aws s3 ls s3://curriculo-nuvem-s3 --profile curriculo-nuvem
```

---

## 10. Validar a identidade

Execute:

```bash
aws sts get-caller-identity
```

O resultado deverá conter:
```
arn:aws:iam::ID_DA_CONTA:user/curriculo-nuvem
```

O ponto importante é confirmar: `user/curriculo-nuvem`

Isso garante que a AWS CLI está utilizando o usuário correto.

---

## 11. Testar ListBucket

Execute:

```bash
aws s3 ls s3://curriculo-nuvem-s3
```

Como o bucket está inicialmente vazio, é normal não aparecer nenhuma saída.

O importante é não receber: `AccessDenied`

**Permissão validada:** `s3:ListBucket`

---

## 12. Testar PutObject

Crie um arquivo de teste:

```bash
echo "Teste do Curriculo Nuvem" > teste.txt
```

Envie para o S3:

```bash
aws s3 cp teste.txt s3://curriculo-nuvem-s3/
```

Confira:

```bash
aws s3 ls s3://curriculo-nuvem-s3
```

Aparecerá algo semelhante a:
```
2026-09-11 08:16:07       26 teste.txt
```

**Permissão validada:** `s3:PutObject`

---

## 13. Testar GetObject

Crie uma pasta local:

```bash
mkdir -p teste-download
```

Baixe o arquivo:

```bash
aws s3 cp s3://curriculo-nuvem-s3/teste.txt teste-download/teste.txt
```

Confira:

```bash
cat teste-download/teste.txt
```

Resultado:
```
Teste do Curriculo Nuvem
```

**Permissão validada:** `s3:GetObject`

---

## 14. Testar DeleteObject

Exclua o arquivo de teste:

```bash
aws s3 rm s3://curriculo-nuvem-s3/teste.txt
```

Confira:

```bash
aws s3 ls s3://curriculo-nuvem-s3
```

O arquivo não deverá mais aparecer.

**Permissão validada:** `s3:DeleteObject`

---

## 15. Enviar o frontend

Estrutura esperada:

```text
curriculo-nuvem-aws/
│
├── frontend/
│   ├── index.html
│   └── style.css
│
└── ...
```

Execute:

```bash
aws s3 sync frontend/ s3://curriculo-nuvem-s3/ --region us-east-1
```

Exemplo:
```
upload: frontend/index.html to s3://curriculo-nuvem-s3/index.html
upload: frontend/style.css to s3://curriculo-nuvem-s3/style.css
```

---

## 16. Confirmar os arquivos

Liste os objetos:

```bash
aws s3 ls s3://curriculo-nuvem-s3
```

Para listar tudo recursivamente:

```bash
aws s3 ls s3://curriculo-nuvem-s3/ --recursive
```

---

## 17. Permissões testadas

| Permissão | Função | Comando utilizado |
|---|---|---|
| `s3:ListBucket` | Listar objetos do bucket | `aws s3 ls` |
| `s3:PutObject` | Enviar objetos | `aws s3 cp` / `aws s3 sync` |
| `s3:GetObject` | Baixar objetos | `aws s3 cp` |
| `s3:DeleteObject` | Excluir objetos | `aws s3 rm` |

---

## 18. Permissões que não foram concedidas

A política não utiliza:
```
s3:*
```

Também não concede:
```
s3:CreateBucket
s3:DeleteBucket
```

O usuário não possui permissão administrativa geral sobre o S3.

O acesso foi limitado ao bucket: `curriculo-nuvem-s3`

Isso segue o princípio de: **Least Privilege**

---

## 19. Segurança do bucket

Nesta etapa:

- Bucket = **PRIVADO**
- Block Public Access = **ATIVADO**

Não existe uma política pública contendo:
```
"Principal": "*"
```
e:
```
"s3:GetObject"
```

O acesso do usuário ocorre através do IAM:

```text
AWS CLI
    |
    v
IAM User
    |
    v
IAM Group
    |
    v
IAM Policy
    |
    v
S3 privado
```

Isso é diferente de tornar o bucket público.

---

## 20. Estado final

```text
AWS Account
│
├── IAM
│   ├── User
│   │   └── curriculo-nuvem
│   │
│   ├── Group
│   │   └── curriculo-nuvem-group
│   │
│   └── Policy
│       └── curriculo-nuvem-s3-policy
│
└── S3
    │
    └── curriculo-nuvem-s3
        ├── index.html
        └── style.css
```

Fluxo:

```text
Raspberry Pi
     |
     v
AWS CLI
     |
     v
IAM User
curriculo-nuvem
     |
     v
IAM Group
curriculo-nuvem-group
     |
     v
IAM Policy
curriculo-nuvem-s3-policy
     |
     v
S3
curriculo-nuvem-s3
```

---

## 21. Próxima etapa

O bucket continuará privado.

Na próxima etapa será configurado:

```text
Internet
    |
    v
CloudFront
    |
    v
OAC
    |
    v
S3 privado
```

Serão documentados:
- CloudFront;
- Origin Access Control (OAC);
- política do bucket permitindo acesso somente pelo CloudFront;
- distribuição;
- HTTPS;
- acesso público ao currículo através do CloudFront.

O bucket S3 não precisará ser transformado em público.

---

## Referência rápida dos comandos

Todos os comandos usados nesta etapa já foram explicados em contexto nas seções acima. Referência rápida:

| Ação | Comando | Seção |
|---|---|---|
| Configurar profile | `aws configure --profile curriculo-nuvem` | [8](#8-configurar-o-profile-na-aws-cli) |
| Ativar profile | `export AWS_PROFILE=curriculo-nuvem` | [9](#9-ativar-o-profile) |
| Confirmar identidade | `aws sts get-caller-identity` | [10](#10-validar-a-identidade) |
| Listar bucket | `aws s3 ls s3://curriculo-nuvem-s3` | [11](#11-testar-listbucket) |
| Enviar arquivo | `aws s3 cp teste.txt s3://curriculo-nuvem-s3/` | [12](#12-testar-putobject) |
| Baixar arquivo | `aws s3 cp s3://curriculo-nuvem-s3/teste.txt teste-download/teste.txt` | [13](#13-testar-getobject) |
| Excluir arquivo | `aws s3 rm s3://curriculo-nuvem-s3/teste.txt` | [14](#14-testar-deleteobject) |
| Enviar frontend | `aws s3 sync frontend/ s3://curriculo-nuvem-s3/ --region us-east-1` | [15](#15-enviar-o-frontend) |
| Listar recursivamente | `aws s3 ls s3://curriculo-nuvem-s3/ --recursive` | [16](#16-confirmar-os-arquivos) |

---

## Cleanup e custo

Se este bucket/usuário for apenas para teste e aprendizado (não para o deploy final):

- **S3**: o bucket `curriculo-nuvem-s3` tem custo mínimo em armazenamento (poucos KB de HTML/CSS), mas vale excluir se não for usar mais: `aws s3 rb s3://curriculo-nuvem-s3 --force`.
- **IAM**: usuários e políticas IAM não geram custo, mas é boa prática remover credenciais de acesso (access keys) que não estão mais em uso, para reduzir superfície de ataque.
- Antes de excluir, confirme que o bucket não está sendo referenciado por nenhuma distribuição CloudFront (etapa seguinte) — excluir o bucket antes de desativar/remover o CloudFront quebra a distribuição.
- Se este for o ambiente final do projeto (não um teste), ignore esta seção — o bucket e o usuário devem permanecer.

---

## Status

- [x] Bucket S3 criado
- [x] Bucket mantido privado
- [x] Block Public Access ativado
- [x] Usuário IAM criado
- [x] Grupo IAM criado
- [x] Política IAM personalizada criada
- [x] Política associada ao grupo
- [x] Chave de acesso criada
- [x] AWS CLI configurada com profile
- [x] Identidade validada
- [x] ListBucket testado
- [x] PutObject testado
- [x] GetObject testado
- [x] DeleteObject testado
- [x] Frontend enviado para o S3

**Próxima etapa:** CloudFront + OAC + acesso ao bucket privado.

---

[🏠 Voltar ao README](../README.md)