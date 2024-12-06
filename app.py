from flask import Flask, render_template, request, redirect, session, jsonify
from flask_socketio import SocketIO, emit
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

# Configuração do Spotify
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
SCOPE = 'user-modify-playback-state user-read-playback-state user-read-currently-playing'

# Fila de músicas
song_queue = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    sp_oauth = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_oauth = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE
    )
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect('/')

@app.route('/search')
def search():
    if 'token_info' not in session:
        return redirect('/login')
    
    sp = spotipy.Spotify(auth=session['token_info']['access_token'])
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

@app.route('/add-to-queue', methods=['POST'])
def add_to_queue():
    track_data = request.json
    song_queue.append(track_data)
    socketio.emit('queue_update', {'queue': song_queue}, broadcast=True)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    socketio.run(app, debug=True)
