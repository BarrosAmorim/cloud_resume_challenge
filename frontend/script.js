async function getVisitorCount() {
    try {
          const apiUrl = 'https://cwz64tvvd0.execute-api.us-east-1.amazonaws.com/count';
        
        const response = await fetch(apiUrl);
        const data = await response.json();
        
        document.getElementById('visitor-count').textContent = data.count || '0';
    } catch (error) {
        console.error('Erro ao carregar contador:', error);
        document.getElementById('visitor-count').textContent = '⚠️ Erro';
    }
}

document.addEventListener('DOMContentLoaded', getVisitorCount);
