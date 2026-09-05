# Etapa 05: DNS Personalizado com Cloudflare

## Objetivo
Configurar um domínio personalizado (`barrosamorimd.work`) para a distribuição CloudFront, utilizando o Cloudflare como provedor de DNS.

## Status
✅ Concluído

## Recursos Utilizados
- Cloudflare (DNS)
- AWS Certificate Manager (ACM)
- Amazon CloudFront

---

## 📋 Passos Realizados

### 1. Obter o Distribution Domain Name do CloudFront

No CloudFront, copiar o nome da distribuição:
```
d1abv1sjhfv11d.cloudfront.net
```

### 2. Criar Certificado no AWS Certificate Manager (ACM)

**Região:** `us-east-1` (obrigatório para CloudFront)

**Domínios adicionados:**
- `barrosamorimd.work`
- `*.barrosamorimd.work` (para subdomínios como `www`)

**Método de validação:** DNS

### 3. Validar o Certificado via Cloudflare

No Cloudflare, adicionar o registro CNAME fornecido pelo ACM:

| Campo | Valor |
|-------|-------|
| **Type** | CNAME |
| **Name** | `_79fadd4bc97a9f9b7971bdbbe56004bc.barrosamorimd.work` |
| **Target** | `_751991cbeb5cb4dd262876982f9b5387.jkddzztszm.acm-validations.aws` |
| **Proxy status** | DNS only |

### 4. Configurar Registro Principal no Cloudflare

| Campo | Valor |
|-------|-------|
| **Type** | CNAME |
| **Name** | `@` (domínio principal) |
| **Target** | `d1abv1sjhfv11d.cloudfront.net` |
| **Proxy status** | **DNS only** (não ativar proxy laranja) |

### 5. Associar Certificado ao CloudFront

1. No CloudFront, editar a distribuição
2. Adicionar `barrosamorimd.work` em "Alternate domain names (CNAMEs)"
3. Selecionar o certificado criado no ACM
4. Salvar alterações

---

## 🔍 Verificação

**URL de acesso:**
```
https://barrosamorimd.work
```

**Testes realizados:**
- ✅ Acesso via HTTPS com certificado válido
- ✅ Redirecionamento HTTP → HTTPS
- ✅ Site carregando corretamente
- ✅ DNS propagado com sucesso

---

## 🐛 Problemas e Soluções

### Problema: Certificado não era encontrado
**Causa:** O certificado não estava sendo validado via DNS.
**Solução:** Adicionar o registro CNAME exato no Cloudflare e aguardar a propagação.

### Problema: Proxy do Cloudflare ativado
**Causa:** O proxy (nuvem laranja) estava ativo.
**Solução:** Desativar o proxy, deixando apenas "DNS only".

---

## 📊 Resumo da Configuração

| Recurso | Configuração |
|---------|--------------|
| **Domínio** | `barrosamorimd.work` |
| **CloudFront** | `d1abv1sjhfv11d.cloudfront.net` |
| **DNS** | Cloudflare (DNS only) |
| **Certificado** | ACM (us-east-1) |

---

## 🎯 Conclusão

O domínio personalizado está configurado com sucesso. O site agora é acessível via `https://barrosamorimd.work` com certificado SSL válido.

**Próximo passo:** Implementar o contador de visitas (JavaScript + DynamoDB + API Gateway + Lambda).

---

[🏠 Voltar ao README](../README.md)