document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    let searchTimeout;

    window.searchTracks = function() {
        const query = document.getElementById('searchInput').value;
        
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            if (query.length > 0) {
                fetch(`/search?q=${encodeURIComponent(query)}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Erro na busca');
                        }
                        return response.json();
                    })
                    .then(tracks => displaySearchResults(tracks))
                    .catch(error => {
                        console.error('Erro:', error);
                        if (error.message === 'Failed to fetch') {
                            window.location.href = '/login';
                        }
                    });
            }
        }, 300);
    }

    function displaySearchResults(tracks) {
        const resultsDiv = document.getElementById('searchResults');
        resultsDiv.innerHTML = '';
        
        if (!tracks || tracks.length === 0) {
            resultsDiv.innerHTML = '<div class="alert alert-info">Nenhuma música encontrada</div>';
            return;
        }
        
        tracks.forEach(track => {
            const div = document.createElement('div');
            div.className = 'list-group-item d-flex justify-content-between align-items-center';
            div.innerHTML = `
                <div class="d-flex align-items-center">
                    <img src="${track.image || 'placeholder.jpg'}" alt="${track.name}" style="width: 50px; height: 50px; margin-right: 15px;">
                    <div>
                        <h6 class="mb-0">${track.name}</h6>
                        <small class="text-muted">${track.artist} - ${track.album}</small>
                    </div>
                </div>
                <button class="btn btn-primary btn-sm" onclick='addToQueue(${JSON.stringify(track)})'>
                    Adicionar à Fila
                </button>
            `;
            resultsDiv.appendChild(div);
        });
    }

    window.addToQueue = function(track) {
        fetch('/add-to-queue', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(track)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao adicionar à fila');
            }
            return response.json();
        })
        .then(data => {
            console.log('Adicionado com sucesso:', data);
            // Opcional: mostrar mensagem de sucesso
        })
        .catch(error => {
            console.error('Erro:', error);
            if (error.message === 'Failed to fetch') {
                window.location.href = '/login';
            }
        });
    }

    function updateQueue(data) {
        const queueList = document.getElementById('queueList');
        if (!queueList) return;

        queueList.innerHTML = '';
        
        if (!data.queue || data.queue.length === 0) {
            queueList.innerHTML = '<div class="alert alert-info">Fila vazia</div>';
            return;
        }

        data.queue.forEach((track, index) => {
            const div = document.createElement('div');
            div.className = 'list-group-item d-flex justify-content-between align-items-center';
            div.innerHTML = `
                <div class="d-flex align-items-center">
                    <span class="badge bg-secondary me-3">${index + 1}</span>
                    <img src="${track.image || 'placeholder.jpg'}" alt="${track.name}" style="width: 40px; height: 40px; margin-right: 15px;">
                    <div>
                        <h6 class="mb-0">${track.name}</h6>
                        <small class="text-muted">${track.artist}</small>
                    </div>
                </div>
            `;
            queueList.appendChild(div);
        });
    }

    socket.on('queue_update', function(data) {
        updateQueue(data);
    });

    // Inicializar a fila vazia
    updateQueue({ queue: [] });

    document.getElementById('searchInput').addEventListener('input', searchTracks);
});
