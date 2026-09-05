# Etapa 04: HTTPS com Amazon CloudFront

## Objetivo
Configurar uma distribuição Amazon CloudFront para servir o site estático hospedado no S3 com **HTTPS**, melhorando a segurança, performance e permitindo que o bucket seja mantido privado.

## Status
✅ Concluído

## Recursos Utilizados
- Amazon CloudFront
- Amazon S3
- AWS Certificate Manager (ACM)
- Origin Access Control (OAC)

---

## 🏗️ Arquitetura da Solução

```
Usuário → https://dxxxxxxxx.cloudfront.net → CloudFront (HTTPS) → S3 (privado)
```

**Benefícios:**
- **HTTPS:** Conexão segura e criptografada
- **Bucket Privado:** Apenas o CloudFront pode acessar
- **Performance:** CDN global com cache
- **Custo:** Menos requisições diretas ao S3

---

## 📋 Passos Realizados

### 1. Criar Distribuição CloudFront

**Acesso:** Console AWS → CloudFront → Create distribution

| Configuração | Valor | Observação |
|--------------|-------|------------|
| **Origin domain** | `cloud-resume-challenge-rafael-2026.s3.us-east-1.amazonaws.com` | Usar **bucket endpoint**, NÃO o website endpoint |
| **Origin path** | Deixar em branco | Os arquivos estão na raiz do bucket |
| **Name** | `cloud-resume-challenge-rafael-2026` | Nome descritivo |

⚠️ **Importante:** O CloudFront mostra um aviso sobre o website endpoint, mas **deve ser ignorado** quando se usa OAC.

### 2. Configurar Origin Access Control (OAC)

**Motivo:** O OAC permite que o bucket S3 fique **privado**, com acesso restrito apenas ao CloudFront.

| Configuração | Valor |
|--------------|-------|
| **Origin access** | `Origin access control settings (recommended)` |
| **OAC Name** | `cloud-resume-oac-rafael` |
| **Signing behavior** | `Sign requests (recommended)` |

**Política gerada para o bucket:**
```json
{
    "Version": "2008-10-17",
    "Id": "PolicyForCloudFrontPrivateContent",
    "Statement": [
        {
            "Sid": "AllowCloudFrontServicePrincipal",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudfront.amazonaws.com"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::cloud-resume-challenge-rafael-2026/*",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceArn": "arn:aws:cloudfront::[ID_CONTA]:distribution/[ID_DISTRIBUICAO]"
                }
            }
        }
    ]
}
```

### 3. Configurações Adicionais

| Configuração | Valor | Motivo |
|--------------|-------|--------|
| **Default root object** | `index.html` | Define o arquivo padrão ao acessar a raiz do site |
| **Viewer protocol policy** | `Redirect HTTP to HTTPS` | Força redirecionamento para HTTPS |
| **Cache policy** | `Managed-CachingOptimized` | Performance otimizada |
| **Allowed HTTP methods** | `GET, HEAD` | Métodos permitidos para o site |

### 4. Configurar Bucket S3

**Política do bucket:**
- Substituída pela política gerada pelo OAC
- Removeu o acesso público (`Principal: "*"`)

---

## 🔍 Verificação

**URL de teste:**
```
https://[distribution-domain-name].cloudfront.net
```

**Testes realizados:**
1. ✅ Acesso via HTTPS (certificado válido)
2. ✅ Redirecionamento de HTTP para HTTPS
3. ✅ Site carregando corretamente
4. ✅ Bucket S3 privado (acesso direto bloqueado)

---

## 🐛 Problemas e Soluções

### Problema 1: Acesso Negado (Access Denied)

**Cenário:** Ao acessar a URL do CloudFront, retornava erro `403 AccessDenied`.

**Causas:**
1. **Default root object não configurado** → CloudFront não sabia qual arquivo servir
2. **OAC não estava selecionado na origem** → CloudFront tentava acessar como público
3. **Política do bucket com ID de distribuição incorreto** → A permissão apontava para outra distribuição

**Solução:**
1. Adicionar `index.html` no campo `Default root object`
2. Selecionar o OAC correto na origem
3. Verificar se o ID da distribuição na política corresponde ao da distribuição


### Problema 2: Aviso sobre S3 website endpoint

**Cenário:** Mensagem no CloudFront: "This S3 bucket has static web hosting enabled. If you plan to use this distribution as a website, we recommend using the S3 website endpoint"

**Causa:** O bucket tem hospedagem estática ativada, mas o CloudFront está usando o bucket endpoint.

**Solução:** **Ignorar o aviso.** O bucket endpoint é o correto para usar com OAC. O website endpoint **não suporta OAC**.

### Problema 3: OAC não aparecia na tela de edição

**Cenário:** A opção de OAC não aparecia ao editar a origem.

**Causa:** O endpoint de website estava selecionado (`s3-website`), que não suporta OAC.

**Solução:** Alterar o `Origin domain` para o bucket endpoint (`s3.us-east-1.amazonaws.com`).

---

## 📊 Resumo da Configuração Final

| Recurso | Configuração |
|---------|--------------|
| **Bucket S3** | `cloud-resume-challenge-rafael-2026` (privado) |
| **CloudFront Distribution** | `cloud-resume-challenge-rafael-2026` |
| **Origin** | `cloud-resume-challenge-rafael-2026.s3.us-east-1.amazonaws.com` |
| **Default root object** | `index.html` |
| **OAC** | `cloud-resume-oac-rafael` |
| **HTTPS** | Ativo (certificado da AWS) |
| **Bucket público** | ❌ Desativado (apenas CloudFront acessa) |

---

## 🎯 Conclusão

O site está agora disponível com **HTTPS** via CloudFront, com maior segurança e performance. O bucket S3 permanece **privado** e o acesso é restrito apenas ao CloudFront através do OAC. 

**URL de acesso:**
```
https://[distribution-domain-name].cloudfront.net
```

**Próximo passo:** Configurar DNS personalizado (Etapa 05) para usar um domínio próprio.

---

[🏠 Voltar ao README](../README.md)