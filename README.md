# CallSense — Customer Call Analytics (Web App)

Splash screen → Login/Register → Dashboard. Audio call upload karo, ye
automatically transcript + summary + category nikaal ke **MongoDB** me save
kar deta hai. MongoDB Compass me tumhe live data dikhega.

## Kya naya add hua hai (accuracy, classification, data extraction, orchestration)

- **Zyada accurate transcript ke liye:**
  - Upload hote hi audio pehle "clean" hoti hai — mono + 16kHz, phone-voice band-pass filter (80Hz–3800Hz), noise reduction (`noisereduce`), aur loudness normalize — fir Whisper ko bheja jaata hai.
  - Whisper ko ek chhota "domain prompt" bhi diya jaata hai (call-center vocabulary — recharge, bill, complaint, waghera, teeno languages me) jisse spelling/word-recognition thoda behtar hoti hai.
  - `temperature=0` set kiya hai taaki Whisper deterministic rahe (random word-guessing kam ho).
  - Agar ffmpeg/noise-reduction kisi wajah se fail ho jaaye, app crash nahi karti — original audio pe hi transcription chal jaati hai.
- **Classification:** category + sentiment ke saath ab **priority** (Low/Medium/High/Urgent) aur **resolution status** (Resolved/Unresolved/Escalated/Follow-up Required) bhi milta hai.
- **Data Extraction:** transcript se customer ka naam, agent ka naam, key issues (list), action items (list), follow-up chahiye ya nahi, aur mentioned phone numbers (regex se, 100% accurate) — sab dashboard pe dikhte hain.
- **End-to-End Orchestration:** poora pipeline ab `services/pipeline.py` me ek jagah orchestrate hota hai — "preprocessing audio" → "transcribing" → "analyzing" → "completed" — har stage ka status live MongoDB/dashboard pe update hota hai, aur agar koi stage fail ho to exactly pata chalta hai kaunsa stage fail hua tha (baaki data safe rehta hai).

## Ye project original PDF plan se kaise alag hai (jaise tumne bola tha)

| PDF me plan tha | Is project me use kiya |
|---|---|
| faster-whisper (large-v2, local) | **Groq Whisper large-v3 API** (cloud, free) — koi local CPU load nahi, bahut fast |
| Ollama + Llama3/Phi-3 (local) | **Groq LLM (llama-3.3-70b)** — cloud API, free tier, koi local load nahi |
| SQLite/CSV | **MongoDB** (Compass me dekh sakte ho) |
| — | Splash screen, Login/Register, Dashboard UI (naya, tumhare requirement ke hisaab se) |

Groq use karne ki wajah: tumne bola tha PC/CPU pe load nahi dena aur fast
chahiye — Groq cloud pe chalta hai (bilkul free hai, sirf internet chahiye),
aur normal CPU pe local model se kaafi zyada fast hai.

---

## 1. Cheezein jo chahiye (ek baar install karo)

1. **Python 3.10+** — https://www.python.org/downloads/ (install karte waqt "Add to PATH" tick karna)
2. **MongoDB Community Server** (chalu rehna chahiye local machine pe) — https://www.mongodb.com/try/download/community
3. **MongoDB Compass** (already tumhare paas hai / same download page se milega)
4. **Free Groq API key** — https://console.groq.com/keys pe jaake sign up karo aur "Create API Key" dabao (bilkul free hai, credit card nahi chahiye)
5. **ffmpeg** — audio cleanup/noise-reduction step (naya, accuracy ke liye) ko ye chahiye:
   - Windows: https://www.gyan.dev/ffmpeg/builds/ pe jaake "ffmpeg-release-essentials.zip" download karo, extract karo (e.g. `C:\ffmpeg`), fir uske andar wale `bin` folder ka path (`C:\ffmpeg\bin`) Windows PATH me add karo (Search → "Edit the system environment variables" → Environment Variables → `Path` → New → path paste karo). Naya terminal kholo aur `ffmpeg -version` chala ke confirm karo.
   - Mac: `brew install ffmpeg`
   - Agar ffmpeg install nahi bhi karo to app crash nahi hogi — bas woh naya noise-reduction step automatically skip ho jayega aur seedha original audio Whisper ko chala jayega (thoda kam accurate ho sakta hai, lekin sab kaam karega).

---

## 2. Project VS Code me kholna

1. Ye poora folder (`call_analytics_pipeline`) apne PC me kahin bhi save karo.
2. VS Code kholo → **File → Open Folder** → isi folder ko select karo.
3. VS Code ke andar Terminal kholo: **Terminal → New Terminal**

---

## 3. Setup (terminal me ye commands chalao, ek-ek karke)

```bash
# 1. Virtual environment banao (recommended)
python -m venv venv

# 2. Activate karo
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Zaruri packages install karo
pip install -r requirements.txt
```

## 4. `.env` file banao

Project ke root me `.env.example` file hai — usko copy karke naam `.env` rakho:

```bash
# Windows:
copy .env.example .env
# Mac/Linux:
cp .env.example .env
```

Ab `.env` file kholo aur ye edit karo:

```
GROQ_API_KEY=yaha_apni_groq_key_paste_karo
SECRET_KEY=koi_bhi_random_lamba_text
```

`MONGO_URI=mongodb://localhost:27017` waisa hi rehne do agar MongoDB tumhare
apne PC pe hi chal raha hai (default setting).

---

## 5. MongoDB chalu karo

Zyadatar Windows/Mac installs me MongoDB service apne aap background me chalu
ho jaati hai install ke baad. Agar nahi chal rahi, MongoDB Compass kholo aur
`mongodb://localhost:27017` se connect karne ki koshish karo — agar connect ho
jaaye to service already chalu hai.

---

## 6. App run karo

Terminal me (venv activate hone ke baad):

```bash
python app.py
```

Terminal me kuch aisa dikhega:
```
Running on http://127.0.0.1:5000
```

Browser me `http://127.0.0.1:5000` kholo — Splash screen dikhega, 2-3 second
me Login page pe le jayega.

1. **Register** pe click karke ek account banao (username, email, password).
2. **Login** karo.
3. **Dashboard** pe audio file upload karo — `sample_calls/` folder me tumhare
   diye hue 5 sample calls already hain, wahi try kar sakte ho.
4. Kuch second me transcript + summary + category + language + sentiment
   dashboard pe dikh jayega.

---

## 6b. Live call record karna (browser mic se)

Dashboard pe "Record a live call" section hai jisse tum apne phone ki call
directly is app se process kara sakti ho:

1. Apne phone se normal call karo aur usko **speaker mode** pe daal do,
   phone ko is laptop/computer ke paas rakho.
2. Dashboard pe **"Start Recording"** button dabao — browser mic permission
   maangega, allow kar do.
3. Call khatam hone par **"Stop Recording"** dabao.
4. Recording sun ke check karo, phir **"Yes, process this recording"**
   dabao — yeh recording bhi wahi upload-wale pipeline se guzregi
   (transcribe → summary → motive → category → sentiment).

**Zaroori baatein:**
- Mic permission sirf `localhost` ya HTTPS pe milti hai — agar app kahi
  aur (jaise koi cloud server) deploy karogi to HTTPS zaroori hai, warna
  browser recording block kar dega.
- Yeh feature asli telecom call ko directly "tap" nahi karta — call ki
  awaaz speaker se laptop/computer ke mic tak jaati hai, isliye recording
  quality thodi kam ho sakti hai upload-wali clean files ke muqable.
- Call record karne se pehle doosre insaan ko batana better practice hai
  (kai jagah legally zaroori bhi hota hai).

---

## 7. MongoDB Compass me data dekhna

1. MongoDB Compass kholo.
2. `mongodb://localhost:27017` se connect karo.
3. `call_analytics` naam ki database dikhegi.
4. Usme 2 collections honge:
   - **users** — registered users (username, email, hashed password)
   - **calls** — har uploaded call ka transcript, summary, category, sentiment, language, timestamp

Data live update hota rahega jaise-jaise tum app use karogi — Compass me
refresh (⟳) dabake dekh sakti ho.

---

## Folder structure

```
call_analytics_pipeline/
├── app.py                     # Main Flask app (saare routes)
├── config.py                  # Settings (.env se load hota hai)
├── requirements.txt
├── .env.example                # copy karke .env banao
├── services/
│   ├── db.py                  # MongoDB connection
│   ├── auth_service.py        # register/login logic
│   ├── audio_processing.py    # noise reduction / cleanup before transcription
│   ├── transcription_service.py  # Groq Whisper (audio → text)
│   ├── llm_service.py         # Groq LLM (text → classification + extracted data JSON)
│   └── pipeline.py            # end-to-end orchestrator (ties every stage together)
├── templates/
│   ├── base.html
│   ├── splash.html
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
├── static/css/style.css       # design
├── uploads/                   # uploaded audio yaha temporarily save hota hai
└── sample_calls/              # tumhare 5 sample test calls
```

---

## Common problems

- **"ModuleNotFoundError"** → `pip install -r requirements.txt` dubara chalao (venv activate hona chahiye).
- **MongoDB connect error** → MongoDB service chalu hai ya nahi check karo (Compass se connect karke test karo).
- **Groq error / 401** → `.env` me `GROQ_API_KEY` sahi se paste hui hai check karo, aur file ka naam `.env` hi hona chahiye (`.env.example` nahi).
- **Upload fail ho raha** → sirf mp3/wav/m4a/ogg/webm files allowed hain.

---

## Aage kya add kar sakte ho (optional, future)

- Multiple calls ek saath (batch) upload karna
- CSV/Excel me export karna
- Team ke hisaab se filter/search
- Chart/graph — category-wise call counts
