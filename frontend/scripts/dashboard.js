// Simular carregamento de dados
        window.addEventListener('load', function() {
            const cards = document.querySelectorAll('.info-card');
            cards.forEach((card, index) => {
                card.classList.add('loading');
                setTimeout(() => {
                    card.classList.remove('loading');
                }, 500 + (index * 200));
            });
        });

        // Funcionalidade dos botões de controle
        const controlBtns = document.querySelectorAll('.control-btn');
        controlBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const action = this.textContent.trim();
                console.log('Ação executada:', action);
                // Aqui você pode adicionar funcionalidades específicas
                alert(`Funcionalidade "${action}" em desenvolvimento!`);
            });
        });

        // Funcionalidade das ferramentas
        const toolCards = document.querySelectorAll('.tool-card');
        toolCards.forEach(card => {
            card.addEventListener('click', function() {
                const toolName = this.querySelector('h4').textContent;
                console.log('Ferramenta selecionada:', toolName);
                alert(`Abrindo: ${toolName}`);
            });
        });

        // Filtros
        const filterInput = document.querySelector('.filter-input');
        if (filterInput) {
        filterInput.addEventListener('input', function() {
                console.log('Filtro aplicado:', this.value);
                // Implementar lógica de filtro aqui
            });
      }

        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                console.log('Categoria selecionada:', this.nextSibling.textContent.trim());
                // Implementar lógica de filtragem por categoria
            });
        });

// ADICIONADO CONFORME IMAGEM
function logout() {
  if(confirm('Deseja realmente sair?')) {
    window.location.href = 'index.html';
  }
}