from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from flask_socketio import SocketIO, emit
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import logging
import eventlet

eventlet.monkey_patch()

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['SESSION_COOKIE_SECURE'] = True
app.config['PREFERRED_URL_SCHEME'] = 'https'

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet',
    logger=True,
    engineio_logger=True
)

# Configuração do Spotify
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
SCOPE = 'user-modify-playback-state user-read-playback-state user-read-currently-playing'

# Fila de músicas
song_queue = []

def create_spotify_oauth():
    try:
        return SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope=SCOPE,
            cache_path=None,
            show_dialog=True
        )
    except Exception as e:
        logger.error(f"Erro ao criar SpotifyOAuth: {str(e)}")
        raise

@app.route('/')
def index():
    try:
        logged_in = 'token_info' in session
        logger.info(f"Usuário está logado: {logged_in}")
        return render_template('index.html', logged_in=logged_in)
    except Exception as e:
        logger.error(f"Erro na rota index: {str(e)}")
        return "Erro ao carregar a página", 500

@app.route('/login')
def login():
    try:
        sp_oauth = create_spotify_oauth()
        auth_url = sp_oauth.get_authorize_url()
        logger.info(f"URL de autorização gerada: {auth_url}")
        return redirect(auth_url)
    except Exception as e:
        logger.error(f"Erro na rota login: {str(e)}")
        return "Erro ao fazer login", 500

@app.route('/callback')
def callback():
    try:
        logger.info("Callback iniciado")
        logger.info(f"Query params: {request.args}")
        
        if 'error' in request.args:
            logger.error(f"Erro retornado pelo Spotify: {request.args.get('error')}")
            return redirect(url_for('index'))
        
        if 'code' not in request.args:
            logger.error("Código de autorização não encontrado")
            return redirect(url_for('index'))
        
        sp_oauth = create_spotify_oauth()
        code = request.args.get('code')
        token_info = sp_oauth.get_access_token(code)
        
        logger.info("Token obtido com sucesso")
        session['token_info'] = token_info
        
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Erro no callback: {str(e)}")
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    try:
        session.clear()
        logger.info("Usuário deslogado com sucesso")
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Erro ao fazer logout: {str(e)}")
        return redirect(url_for('index'))

def get_spotify():
    try:
        token_info = session.get('token_info')
        if not token_info:
            logger.warning("Token não encontrado na sessão")
            return None
        
        sp_oauth = create_spotify_oauth()
        
        if sp_oauth.is_token_expired(token_info):
            logger.info("Token expirado, renovando...")
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            session['token_info'] = token_info
        
        return spotipy.Spotify(auth=token_info['access_token'])
    except Exception as e:
        logger.error(f"Erro ao obter cliente Spotify: {str(e)}")
        return None

@app.route('/search')
def search():
    try:
        if 'token_info' not in session:
            return redirect(url_for('login'))
        
        sp = get_spotify()
        query = request.args.get('q')
        if not query:
            return jsonify([])
        
        results = sp.search(q=query, limit=10, type='track')
        tracks = results['tracks']['items']
        return jsonify([{
            'id': track['id'],
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name'],
            'image': track['album']['images'][0]['url'] if track['album']['images'] else None
        } for track in tracks])
    except Exception as e:
        logger.error(f"Erro na rota search: {str(e)}")
        return "Erro ao buscar músicas", 500

@app.route('/add-to-queue', methods=['POST'])
def add_to_queue():
    try:
        track_data = request.json
        song_queue.append(track_data)
        socketio.emit('queue_update', {'queue': song_queue}, broadcast=True)
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Erro na rota add-to-queue: {str(e)}")
        return "Erro ao adicionar música à fila", 500

if __name__ == '__main__':
    socketio.run(app, debug=True)
