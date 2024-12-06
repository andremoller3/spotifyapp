const socket = io();
let searchTimeout;

function searchTracks() {
    const query = document.getElementById('searchInput').value;
    
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        if (query.length > 0) {
            fetch(`/search?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(tracks => displaySearchResults(tracks));
        }
    }, 300);
}

function displaySearchResults(tracks) {
    const resultsDiv = document.getElementById('searchResults');
    resultsDiv.innerHTML = '';
    
    tracks.forEach(track => {
        const div = document.createElement('div');
        div.className = 'search-result';
        div.innerHTML = `
            <img src="${track.image || 'placeholder.jpg'}" alt="${track.name}">
            <div class="track-info">
                <div class="track-name">${track.name}</div>
                <div class="track-artist">${track.artist}</div>
            </div>
            <button class="btn btn-primary btn-add" onclick='addToQueue(${JSON.stringify(track)})'>
                Adicionar à Fila
            </button>
        `;
        resultsDiv.appendChild(div);
    });
}

function addToQueue(track) {
    fetch('/add-to-queue', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(track)
    })
    .then(response => response.json())
    .then(data => console.log('Success:', data))
    .catch(error => console.error('Error:', error));
}

function updateQueue(data) {
    const queueDiv = document.getElementById('queueList');
    queueDiv.innerHTML = '';
    
    data.queue.forEach((track, index) => {
        const div = document.createElement('div');
        div.className = 'queue-item';
        div.innerHTML = `
            <img src="${track.image || 'placeholder.jpg'}" alt="${track.name}">
            <div class="track-info">
                <div class="track-name">${index + 1}. ${track.name}</div>
                <div class="track-artist">${track.artist}</div>
            </div>
        `;
        queueDiv.appendChild(div);
    });
}

socket.on('queue_update', function(data) {
    updateQueue(data);
});

document.getElementById('searchInput').addEventListener('input', searchTracks);
