# Spotify Queue App

Uma aplicação web que permite que múltiplos usuários adicionem músicas a uma fila de reprodução compartilhada do Spotify.

## Configuração

1. Primeiro, crie uma aplicação no [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Copie o arquivo `.env.example` para `.env` e preencha com suas credenciais do Spotify:
```
SPOTIPY_CLIENT_ID=seu_client_id_aqui
SPOTIPY_CLIENT_SECRET=seu_client_secret_aqui
SPOTIPY_REDIRECT_URI=http://localhost:5000/callback
```

4. Execute a aplicação:
```bash
python app.py
```

5. Acesse `http://localhost:5000` no seu navegador

## Funcionalidades

- Login com Spotify
- Busca de músicas
- Adição de músicas à fila
- Atualização em tempo real da fila para todos os usuários
- Interface responsiva e amigável

## Tecnologias Utilizadas

- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript
- Real-time: Flask-SocketIO
- API: Spotify Web API
