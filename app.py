from flask import * 
import pickle 
import librosa
import numpy as np
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__, template_folder="templates_path")
model = pickle.load(open("model_knn.pkl_path", 'rb')) 
scaler = pickle.load(open("scaler.pkl_path", 'rb'))

def getmetadata(filename):
    y, sr = librosa.load(filename)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    tempo, beat_frames = librosa.beat.beat_track(y=y_percussive, sr=sr)
    #chroma_stf
    chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr) 
    #rmse
    rmse = librosa.feature.rms(y=y) 
    #fetching spectral centroid
    spec_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0] 
    #spectral bandwidth
    spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr) 
    #fetching spectral rolloff
    spec_rolloff = librosa.feature.spectral_rolloff(y=y+0.01, sr=sr)[0]
    #zero crossing rate
    zero_crossing = librosa.feature.zero_crossing_rate(y) 
    #mfcc
    mfcc = librosa.feature.mfcc(y=y, sr=sr) 
    #metadata dictionary
    metadata_dict = {
        'tempo': tempo,
        'chroma_stft': np.mean(chroma_stft),
        'rmse': np.mean(rmse), 
        'spectral_centroid': np.mean(spec_centroid),
        'spectral_bandwidth': np.mean(spec_bw),
        'rolloff': np.mean(spec_rolloff),
        'zero_crossing_rates': np.mean(zero_crossing)
    }
    for i in range(1, 21): 
        metadata_dict.update({'mfcc'+str(i): np.mean(mfcc[i-1])})
    return metadata_dict

@app.route('/') 
def upload():
    return render_template("file_upload_form.html")

@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':
        f = request.files['file']
        f.save(f.filename)
        f_name = f.filename.split('.')
        if f_name[-1] != 'wav':
            file_name = 'Upload only wav file'
        else:
            file_name = f.filename
            genre = {0: 'blues', 1: 'classical', 2: 'country', 3: 'disco', 4: 'hiphop', 5: 'jazz',
                     6: 'metal', 7: 'pop', 8: 'reggae', 9: 'rock',106:'blues'}
            mtdt = getmetadata(f.filename)
            mtdt_scaled = scaler.transform([np.array(list(mtdt.values())).ravel()])
            pred_genre = model.predict(mtdt_scaled)
            print("Predicted Genre Index:", pred_genre[0])


            # Handling unknown genres
            if pred_genre[0] in genre:
                genre_name = genre[pred_genre[0]]
            else:
                genre_name = "Unknown Genre"

        return render_template("success.html", name=file_name, genre=genre_name)		

if __name__ == '__main__': 
    app.run(debug=True)
