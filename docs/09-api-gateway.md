# Etapa 08: API Gateway

## Objetivo
Criar uma API HTTP no Amazon API Gateway para expor a função Lambda que gerencia o contador de visitas, permitindo que o frontend acesse o backend de forma segura e escalável.

## Status
✅ Concluído

## Recursos Utilizados
- Amazon API Gateway (HTTP API)
- AWS Lambda
- AWS IAM

---

## 📋 Método de Criação

A API Gateway foi criada utilizando o **Console AWS** (interface web), não via CLI. Isso foi feito para facilitar o entendimento visual dos componentes e validar a integração com a Lambda antes de automatizar com SAM (Etapa 11).

---

## 📋 Passo a Passo Completo

### Parte 1: Criar a API HTTP

#### 1.1 Acessar o API Gateway

1. No console AWS, pesquisar por **"API Gateway"**
2. Clicar no resultado para abrir o serviço

#### 1.2 Iniciar a Criação

1. Clicar em **"Create API"**
2. Em **"HTTP API"**, clicar em **"Build"**

#### 1.3 Configurar a API

| Campo | Valor | Motivo |
|-------|-------|--------|
| **Nome da API** | `visitor-counter-API` | Nome descritivo para identificar a API |
| **Tipo de endereço IP** | `IPv4` | Padrão, compatível com todos os serviços |

---

### Parte 2: Configurar a Integração com Lambda

#### 2.1 Adicionar Integração

1. Em **"Integrations"**, clicar em **"Add integration"**
2. Preencher:

| Campo | Valor | Motivo |
|-------|-------|--------|
| **Integration type** | `Lambda` | Integrar com uma função Lambda |
| **AWS Region** | `us-east-1` | Mesma região do Lambda |
| **Lambda function** | `visitor-counter` | Selecionar a função criada |

3. Clicar em **"Create"** (ou "Next")

#### 2.2 Configurar a Integração

1. No menu lateral, clicar em **"Integrations"**
2. Clicar na integração criada (`visitor-counter`)
3. Configurar:

| Campo | Valor | Motivo |
|-------|-------|--------|
| **Versão do formato da carga** | `2.0` | Versão mais recente do formato |
| **Modo de resposta** | `Simples` | A Lambda retorna JSON simples |

4. Clicar em **"Save"** (ou "Update")

---

### Parte 3: Configurar a Rota

#### 3.1 Criar a Rota

1. No menu lateral, clicar em **"Routes"**
2. Clicar em **"Create"**
3. Preencher:

| Campo | Valor | Motivo |
|-------|-------|--------|
| **Method** | `GET` | Método HTTP para ler o contador |
| **Path** | `/count` | Caminho que o frontend vai chamar |

4. Clicar em **"Create"**

#### 3.2 Anexar a Integração à Rota

1. Na lista de rotas, localizar `GET /count`
2. Clicar nos **três pontinhos** (`...`) no final da linha
3. Selecionar **"Attach integration"** (Anexar integração)
4. Em **"Integration"**, selecionar `visitor-counter`
5. Clicar em **"Attach"**

#### 3.3 Verificar a Rota

A rota deve aparecer como:

```
/count   GET   visitor-counter
```

---

### Parte 4: Configurar o Estágio

#### 4.1 Criar o Estágio

1. No menu lateral, clicar em **"Stages"** (Estágios)
2. Se não houver estágio, clicar em **"Create"** (Criar)
3. Preencher:

| Campo | Valor | Motivo |
|-------|-------|--------|
| **Stage name** | `$default` | Estágio padrão para a API |
| **Auto-deploy** | `Enabled` | Implantar automaticamente as alterações |

4. Clicar em **"Create"**

#### 4.2 Verificar a URL

Após criar o estágio, a URL de invocação será exibida:

```
https://[api-id].execute-api.[region].amazonaws.com
```

**Exemplo:** `https://qjtn3yvqhe.execute-api.us-east-1.amazonaws.com`

---

### Parte 5: Configurar CORS (Cross-Origin Resource Sharing)

#### 5.1 Por que configurar CORS?

O navegador bloqueia requisições de um domínio diferente (ex: `barrosamorimd.work`) para outro (ex: `qjtn3yvqhe.execute-api.amazonaws.com`). O CORS permite que o frontend chame a API.

#### 5.2 Configurar o CORS

1. No menu lateral, clicar em **"CORS"**
2. Clicar em **"Configure"**
3. Preencher:

| Campo | Valor | Motivo |
|-------|-------|--------|
| **Access-Control-Allow-Origin** | `https://barrosamorimd.work` | Domínio do site que vai chamar a API |
| **Access-Control-Allow-Methods** | `GET` | Métodos permitidos |
| **Access-Control-Allow-Headers** | `*` | Todos os cabeçalhos permitidos |

4. Clicar em **"Save"**

---

### Parte 6: Testar a API

#### 6.1 Teste no Terminal

```bash
curl https://qjtn3yvqhe.execute-api.us-east-1.amazonaws.com/count
```

**Resultado esperado:**
```json
{"count": 0}
```

#### 6.2 Teste no Navegador

1. Acessar: `https://barrosamorimd.work`
2. Abrir o console do navegador (F12)
3. Executar:

```javascript
fetch('https://qjtn3yvqhe.execute-api.us-east-1.amazonaws.com/count')
  .then(r => r.json())
  .then(d => console.log('Contador:', d))
  .catch(e => console.error('Erro:', e));
```

**Resultado esperado:**
```
Contador: {count: 0}
```

---

## 🐛 Problemas e Soluções (Passo a Passo)

### Problema 1: API retornando "Not Found"

**Cenário:** Ao testar a API, retornava `{"message":"Not Found"}`.

**Causa:** A rota não estava implantada ou o estágio não estava configurado corretamente.

**Solução:**
1. Verificar se a rota `GET /count` existe em **"Routes"**
2. Verificar se a integração está anexada à rota
3. Verificar se o estágio `$default` foi criado
4. Criar uma nova invalidação no CloudFront (se necessário)

---

### Problema 2: Erro de CORS no navegador

**Cenário:** O navegador bloqueava a requisição com erro de CORS.

**Causa:** A API Gateway não estava configurada para aceitar requisições do domínio do site.

**Solução:**
1. Acessar **"CORS"** no API Gateway
2. Adicionar `https://barrosamorimd.work` em `Access-Control-Allow-Origin`
3. Salvar e aguardar a propagação

---

### Problema 3: Erro ao criar invalidação no CloudFront

**Cenário:** `AccessDenied` ao executar `aws cloudfront create-invalidation`.

**Causa:** O usuário IAM não tinha permissão `cloudfront:CreateInvalidation`.

**Solução:** Adicionar a permissão à política IAM `s3-resume-bucket-access`:

```json
{
    "Effect": "Allow",
    "Action": "cloudfront:CreateInvalidation",
    "Resource": "arn:aws:cloudfront::696537703431:distribution/EGGP4OT7VLDC2"
}
```

---

### Problema 4: Versão antiga do script.js no cache

**Cenário:** Mesmo atualizando o script, o navegador continuava com a versão antiga.

**Causa:** CloudFront mantinha a versão antiga em cache.

**Solução:**
1. Criar invalidação no CloudFront:
   ```bash
   aws cloudfront create-invalidation --distribution-id EGGP4OT7VLDC2 --paths "/*"
   ```
2. Ou usar "cache buster" no HTML:
   ```html
   <script src="script.js?v=2"></script>
   ```

---

## 🔒 Permissões IAM Necessárias (via CLI)

Se você fosse criar a API via CLI (AWS CLI ou SAM), o usuário IAM precisaria das seguintes permissões adicionais:

```json
 {
            "Effect": "Allow",
            "Action": "apigateway:*",
            "Resource": "*"
        }
```

**Nota:** Como a API foi criada via **Console AWS**, essas permissões não foram necessárias para o usuário IAM.

---

## 📊 Resumo da Configuração Final

| Recurso | Configuração |
|---------|--------------|
| **API Name** | `visitor-counter-API` |
| **API ID** | `qjtn3yvqhe` |
| **Tipo** | HTTP API |
| **Rota** | `GET /count` |
| **Integração** | Lambda `visitor-counter` |
| **Estágio** | `$default` |
| **Auto-deploy** | Enabled |
| **URL da API** | `https://qjtn3yvqhe.execute-api.us-east-1.amazonaws.com/count` |
| **CORS Origin** | `https://barrosamorimd.work` |
| **CORS Methods** | `GET` |
| **CORS Headers** | `*` |

---

## 🎯 Conclusão

A API Gateway está configurada e integrada com a Lambda, permitindo que o frontend faça requisições para o contador de visitas de forma segura e eficiente.

**Próximo passo:** Documentar a criação da função Lambda (Etapa 09).

---

[🏠 Voltar ao README](../README.md)