# Etapa 06: JavaScript - Contador de Visitas

## Objetivo
Preparar o frontend para exibir e atualizar o contador de visitas via API, criando a função JavaScript que fará a requisição para o backend.

## Status
✅ Concluído

## Recursos Utilizados
- JavaScript (fetch API)
- HTML (elemento para exibir o contador)
- Amazon S3 (hospedagem)
- Amazon CloudFront (cache)

---

## 📋 Passos Realizados

### 1. Criar o Arquivo `frontend/script.js`

O arquivo foi criado com a função `getVisitorCount()`, que:
- Faz uma requisição GET para a URL da API Gateway (ainda não criada)
- Recebe o valor do contador em JSON
- Atualiza o elemento HTML com o valor retornado

**Código:**
```javascript
async function getVisitorCount() {
    try {
        // URL da API Gateway (será atualizada depois)
        const apiUrl = 'https://sua-api-gateway-url.execute-api.region.amazonaws.com/count';
        
        const response = await fetch(apiUrl);
        const data = await response.json();
        
        document.getElementById('visitor-count').textContent = data.count || '0';
    } catch (error) {
        console.error('Erro ao carregar contador:', error);
        document.getElementById('visitor-count').textContent = '⚠️ Erro';
    }
}

document.addEventListener('DOMContentLoaded', getVisitorCount);
```

### 2. Atualizar o HTML

O arquivo `frontend/index.html` foi atualizado com o elemento para exibir o contador:

```html
<footer>
    <p>Visitantes: <span id="visitor-count">Carregando...</span></p>
</footer>
```

### 3. Fazer Upload para o S3

```bash
aws s3 sync frontend/ s3://cloud-resume-challenge-rafael-2026/ --region us-east-1
```

**Resultado esperado:**
```
upload: frontend/script.js to s3://cloud-resume-challenge-rafael-2026/script.js
```

### 4. Invalidar Cache do CloudFront

Para garantir que os usuários vejam a versão mais recente:

```bash
aws cloudfront create-invalidation --distribution-id EGGP4OT7VLDC2 --paths "/*"
```

---

## 🔍 Verificação

**Comportamento atual (esperado):**
- O site exibe "Carregando..." ou "⚠️ Erro" no rodapé
- O console do navegador mostra erro de conexão com a API
- ✅ **Isso é esperado**, pois a API ainda não foi criada

**Próximos passos:**
1. Criar tabela DynamoDB (Etapa 08)
2. Criar API Gateway (Etapa 09)
3. Criar Lambda em Python (Etapa 10)
4. Atualizar a URL da API no `script.js`

---

## 🐛 Problemas e Soluções

### Problema 1: Upload para S3 com permissão negada
**Causa:** O usuário não tinha permissão `s3:ListBucket`.
**Solução:** Adicionar `s3:ListBucket` à política IAM `s3-resume-bucket-access`.

### Problema 2: Cache do CloudFront
**Causa:** O CloudFront armazena versões antigas dos arquivos.
**Solução:** Criar uma invalidação com o caminho `/*`.

---

## 📊 Resumo da Configuração

| Recurso | Configuração |
|---------|--------------|
| **Arquivo JavaScript** | `frontend/script.js` |
| **Função** | `getVisitorCount()` |
| **Elemento HTML** | `<span id="visitor-count">` |
| **Bucket S3** | `cloud-resume-challenge-rafael-2026` |
| **CloudFront Invalidação** | `/*` |

---

## 🎯 Conclusão

O frontend está preparado para receber o contador de visitas. A função JavaScript está no ar, aguardando a criação da API backend que fornecerá os dados.

**Próximo passo:** Criar a tabela DynamoDB para armazenar a contagem (Etapa 08).

---

[🏠 Voltar ao README](../README.md)