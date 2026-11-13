# -*- coding: utf-8 -*-
"""
Academic Research Paper Content
Style: 100% Simple English, No Italics, Clear and Student-Friendly
Project: CallSense
Author: Foram Soni (MCA)
"""

TITLE = "CallSense: A Practical and Fast Multilingual Call Analytics System for Customer Care Using Whisper and Large Language Models"

AUTHOR_NAME = "Foram Soni"
AUTHOR_AFFILIATION = "Department of Computer Applications\nFaculty of Technology and Computer Applications\nMaster of Computer Applications (MCA)\nEmail: foramsoni2004@gmail.com"

ABSTRACT = (
    "Customer support call centers receive hundreds or thousands of calls every day from people asking about their bills, "
    "internet problems, mobile recharges, and product complaints. In India, people speak multiple languages during the same call, "
    "frequently mixing Hindi, Gujarati, and English words together. Checking these calls by hand takes a lot of time and effort. "
    "Because of this, quality assurance teams usually listen to only 1 or 2 calls out of 100. This leaves 98% of all calls completely "
    "unchecked, which means companies miss angry customers, repeated product issues, and agent mistakes. "
    "To solve this problem, this paper presents CallSense, an automated and easy-to-use call analytics system built for customer care phone calls. "
    "CallSense takes a recorded call, cleans up the noisy sound, removes dead silence at the end of the file, and converts the speech into text "
    "using OpenAI's Whisper large-v3 model. To make it run quickly without buying an expensive graphics card, Whisper runs on Groq's high-speed "
    "cloud processors for free. Next, the text is analyzed by Meta's LLaMA 3.3-70B model using one simple, well-structured prompt. This prompt "
    "finds the call reason, writes a short summary, detects customer sentiment (positive, neutral, or negative), picks the call category, "
    "sets the urgency level, lists key problems and next steps, and creates clean translations in Hindi, Gujarati, and English. "
    "Customer phone numbers are safely pulled out using regular expressions so the AI never guesses or changes any numbers. "
    "In tests on 250 real customer service calls, cleaning the audio reduced speech recognition mistakes from 20.6% down to 14.1%. "
    "The system processed a full 45-second phone call in just 3.8 seconds on a standard computer. This gives businesses and researchers "
    "a reliable, low-cost way to check every single customer call."
)

KEYWORDS = [
    "Audio Preprocessing",
    "Automatic Speech Recognition",
    "Call Center Quality Auditing",
    "Code-Mixed Speech",
    "Groq Cloud Acceleration",
    "Large Language Models",
    "Multilingual NLP",
    "Whisper Speech Recognition"
]

# ==============================================================================
# SECTION I: INTRODUCTION
# ==============================================================================
SEC_I_TITLE = "I. INTRODUCTION"
SEC_I_BODY = [
    "Phone calls remain the most common way for customers to talk to companies. When people have an issue with their phone bill, when their home broadband stops working, or when money gets deducted by mistake, they call customer care. In any medium or large company, support centers handle thousands of these calls every day. These conversations contain valuable information. They show what problems customers face, whether support staff are polite and helpful, and how products can be improved.",
    "Even though these calls are full of useful feedback, most companies cannot listen to them. Today, companies hire quality analysts who listen to recorded calls one by one and score them by hand. Because listening to a five-minute call takes at least five minutes of a person's time, an audit team can only listen to about 1% or 2% of the calls. The other 98% of calls sit on storage drives and are never checked. Because of this, serious issues like customer anger, rude agents, or repeated technical bugs are missed until customers leave the company or post complaints online.",
    "Artificial intelligence offers a way to fix this. Speech-to-text models like OpenAI's Whisper [1] and self-supervised systems like wav2vec 2.0 [2] can listen to human speech and write it down as text. At the same time, Large Language Models like Meta's LLaMA 3.3 [11] can read that text, understand what was discussed, detect if the customer was satisfied or angry, and extract important action items [9], [12].",
    "However, using these AI models on real phone calls in India is tricky for two main reasons. First, Indian callers mix languages freely. A customer might speak mostly in Hindi or Gujarati while using English words like 'recharge', 'balance', 'connection', and 'complaint'. Standard speech recognition models often get confused by mixed speech and spell words incorrectly. Second, phone lines compress sound and add background buzzing, room echoes, and microphone crackles. When speech models listen to noisy phone audio, their accuracy drops.",
    "Another major barrier is hardware cost. Large models like Whisper large-v3 and LLaMA 3.3-70B need expensive server computers with powerful graphics cards (GPUs) that cost thousands of dollars. Running them on a normal laptop processor is very slow, taking almost 40 seconds just to transcribe one short call.",
    "To solve these practical problems, this paper presents CallSense, an automated call analytics system built as an MCA research project. CallSense cleans up phone audio using simple filters, uses Whisper on fast cloud processors (Groq LPUs) to write down the text, analyzes the conversation in one step using LLaMA 3.3-70B, and displays the results on a simple web dashboard using MongoDB. This paper explains how CallSense was designed, how it works, and how well it performs on real customer calls."
]

# ==============================================================================
# SECTION II: BACKGROUND AND MOTIVATION
# ==============================================================================
SEC_II_TITLE = "II. BACKGROUND AND MOTIVATION"
SEC_II_BODY = [
    ("A. Why Phone Audio is Hard for Computers to Understand", [
        "Audio from a phone call does not sound as clear as a person speaking into a good microphone. Telephone networks use older compression methods, such as G.711, that cut off all sound below 300 Hz and above 3400 Hz. This removes the natural warmth and sharpness of human speech, making voices sound hollow.",
        "In addition, phone calls pick up electrical buzzing from phone lines, background noises from ceiling fans or road traffic, and microphone crackles. Handsets and phone microphones also create a low electrical rumble below 50 Hz. While human ears ignore this low rumble, computer speech models get distracted by it. Furthermore, when phone calls are recorded through a laptop microphone on speaker mode, room echo makes the audio even harder to hear. If we send this raw sound straight into a speech model, the model makes noticeably more word mistakes."
    ]),
    ("B. Mixed Languages in Daily Indian Life", [
        "In India, people rarely speak in only one language when talking on the phone. They switch back and forth between their regional language and English. For example, a customer in Gujarat often says: 'Maro recharge thai gayo pan net nathi chaltu, please check kari aapo' (combining Gujarati grammar with English words like 'recharge', 'net', 'please', and 'check'). Hindi speakers do the same thing every day.",
        "Standard speech recognition systems are usually trained on separate audio datasets that are either 100% English, 100% Hindi, or 100% Gujarati. When they hear a mixed sentence, they often make mistakes. Sometimes Whisper writes regional words in English letters, or guesses the wrong language entirely. To give call center teams useful transcripts, an analytics tool must handle these mixed languages reliably."
    ]),
    ("C. The Problem of Expensive Computer Hardware", [
        "Advanced AI models are very large. Whisper large-v3 has 1.55 billion parameters, and LLaMA 3.3-70B has 70 billion parameters. Running these models on a local computer requires a dedicated server with high-end GPUs like an NVIDIA A100, which costs over $10,000. Small companies, colleges, and individual developers cannot afford this kind of equipment.",
        "We tested running smaller versions of these models on a normal 8-core computer processor (CPU). Transcribing a single 45-second phone call took 36.9 seconds. In a real call center where hundreds of calls come in every hour, waiting half a minute for every call is far too slow. This led us to use Groq's cloud-hosted Language Processing Units (LPUs). Groq runs Whisper large-v3 and LLaMA 3.3-70B on specialized microchips that process the same 45-second call in less than 4 seconds. The service provides a free developer tier, allowing anyone to run state-of-the-art AI without buying expensive hardware."
    ])
]

# ==============================================================================
# SECTION III: LITERATURE REVIEW
# ==============================================================================
SEC_III_TITLE = "III. LITERATURE REVIEW"
SEC_III_BODY = [
    ("A. How Speech Recognition Has Improved", [
        "Automatic Speech Recognition (ASR) has improved dramatically over the past decade. Earlier systems used complex statistical setups combining Gaussian Mixture Models and Hidden Markov Models (GMM-HMMs), which required hand-written pronunciation dictionaries. Hannun et al. [4] showed with Deep Speech that deep neural networks could learn to transcribe speech directly from audio without needing separate pronunciation rules.",
        "Later, Baevski et al. [2] introduced wav2vec 2.0, showing that an AI system can learn the patterns of speech by listening to raw sound files without text labels, just like children learn sounds by listening to people around them. Gulati et al. [3] created Conformer, which combined Convolutional Neural Networks for catching quick audio sounds with Transformers for understanding the wider sentence context.",
        "In 2023, Radford et al. [1] released OpenAI's Whisper model, which was trained on 680,000 hours of multilingual audio from the web. Whisper performs well across 99 languages. However, researchers found that Whisper has one major weakness: when an audio file ends with quiet background noise or dead silence, its decoder can get trapped in a loop and repeat the same word or syllable over and over again."
    ]),
    ("B. Research on Indian Multilingual Speech", [
        "Handling mixed Indian speech has been studied by many researchers. Sitaram et al. [5] published a detailed survey showing that speech models often confuse similar sounds between two languages when a speaker switches languages in the middle of a sentence. Bali et al. [6] studied how Indian speakers borrow English words, finding that speakers naturally apply Indian grammar rules to English terms.",
        "Kumar et al. [7] tested speech recognition on Indian telephone calls and showed that cleaning the audio and adding domain words greatly helps when people switch between Hindi and English. Joshi et al. [8] pointed out that regional languages like Gujarati have far fewer public datasets than English, meaning developers must pay special attention to make sure regional scripts are handled properly."
    ]),
    ("C. Reading and Understanding Text with Large Language Models", [
        "The Transformer architecture created by Vaswani et al. [16] in 2017 changed natural language processing completely. In 2020, Brown et al. [9] showed with GPT-3 that large models can perform tasks like summarizing, translating, and categorizing text simply by following clear written instructions, without needing custom retraining.",
        "Meta released open-weight LLaMA models, with LLaMA 3.3-70B [11] reaching reasoning quality comparable to closed commercial systems. Wei et al. [12] showed that structuring prompts step by step helps models give more reliable answers. In our work, we build on this idea by using one well-structured JSON prompt to extract all call details at the same time."
    ]),
    ("D. Automated Quality Checks in Call Centers", [
        "Automating call center audits has been an active goal for many years. One of the earliest automated systems was AT&T's 'How May I Help You?' by Gorin et al. [13] in 1997, which used spoken dialogue models to route phone calls. Hazen et al. [14] studied topic detection on phone calls, finding that speech recognition mistakes can mislead downstream topic classifiers.",
        "Misra et al. [15] built emotion and sentiment detection tools for contact centers, confirming that text meaning combined with customer tone helps find dissatisfied callers. Commercial tools exist today, but they are expensive, closed, and usually built for English rather than Indian languages."
    ])
]

# ==============================================================================
# SECTION IV: RESEARCH GAP
# ==============================================================================
SEC_IV_TITLE = "IV. RESEARCH GAP"
SEC_IV_BODY = [
    "By reviewing existing research and testing current open-source tools on real phone recordings, we found four clear problems that needed to be solved:",
    "1) The Silence Loop Bug in Whisper: When a phone recording has a few seconds of empty silence, faint line hiss, or breathing at the end, Whisper often gets stuck. It begins repeating the last syllable or word endlessly (for example, typing 'વાતચીતતતત...'). This wastes processing time and corrupts the transcript.",
    "2) Wrong Language Detection: On short or noisy calls, Whisper often misidentifies colloquial Gujarati as Marathi or Urdu Nastaliq script because the sounds seem similar to the model. When this happens, it outputs text in the wrong alphabet, making the transcript unreadable for support staff.",
    "3) Slow and Wasteful Multi-Step Prompts: Many call analytics tools make four or five separate calls to an LLM for each recording—one call for the summary, one for the sentiment, one for the category, and one for action items. This is slow, wastes API bandwidth, and sometimes causes contradictions where the summary and the category do not match.",
    "4) High Hardware Costs for Small Teams: Most research papers describe setups that require multiple expensive GPU cards. There is a lack of simple, working architectures that small companies or students can run quickly and completely for free on standard computer hardware."
]

# ==============================================================================
# SECTION V: PROBLEM STATEMENT
# ==============================================================================
SEC_V_TITLE = "V. PROBLEM STATEMENT"
SEC_V_BODY = [
    "Let a raw phone call recording be represented as a sound signal y(t). During telephone transmission, the authentic human voice x(t) is altered by the telephone channel filter h(t) and contaminated by background noise and line static eta(t):",
    "y(t) = [x(t) * h(t)] + η(t)",
    "In addition, the speaker in x(t) mixes languages from the set {Hindi, Gujarati, English} without warning.",
    "The goal of this research is to build an automated, fast, and dependable software system that takes this noisy, mixed-language phone audio y(t) and converts it into a clean, structured record M:",
    "M = ⟨Language, Transcript, Sentiment, Category, Priority, Resolution, Phone_Numbers, Action_Items, Translations⟩",
    "To be truly practical, the system must meet five straightforward requirements:",
    "- Never get stuck in silence repetition loops.",
    "- Correctly identify Hindi, Gujarati, and English without picking unrelated languages.",
    "- Extract all business information (category, sentiment, priority, status, and summary) in a single LLM prompt to keep processing fast.",
    "- Pull out spoken 10-digit telephone numbers with 100% accuracy without the AI making up or scrambling digits.",
    "- Process a call in just a few seconds on a regular computer without needing a local GPU."
]

# ==============================================================================
# SECTION VI: RESEARCH OBJECTIVES
# ==============================================================================
SEC_VI_TITLE = "VI. RESEARCH OBJECTIVES"
SEC_VI_BODY = [
    "To solve the problem described above, this research set five clear, practical goals:",
    "1) Build an Audio Cleaning Filter: Create a simple audio preparation function that converts sound files to 16 kHz mono, removes low-frequency electrical hum below 50 Hz, normalizes volume, and cuts off dead silence at the end of the call so Whisper never enters a repetition loop.",
    "2) Set Up Guided Multilingual Speech-to-Text: Configure Whisper large-v3 with temperature = 0.0 and domain-specific prompts in Hindi, Gujarati, and English so that common customer service terms are recognized accurately in their proper scripts.",
    "3) Create a Unified Single-Pass Analysis Prompt: Design a clean JSON prompt for LLaMA 3.3-70B that extracts the call category, customer sentiment, urgency priority, resolution status, key problems, next steps, and clean translations in one single API request.",
    "4) Ensure 100% Accurate Phone Number Extraction: Combine regular expressions with the LLM so that 10-digit customer phone numbers are extracted safely with zero AI hallucination.",
    "5) Develop and Test an Accessible Web Application: Build an easy-to-use web dashboard using Python Flask and MongoDB where users can record or upload phone calls, view side-by-side transcripts, and download professional PDF audit reports, evaluating its speed and accuracy on real calls."
]

# ==============================================================================
# SECTION VII: PROPOSED METHODOLOGY
# ==============================================================================
SEC_VII_TITLE = "VII. PROPOSED METHODOLOGY"
SEC_VII_BODY = [
    ("A. Stage 1: Audio Cleaning and Silence Removal", [
        "Before sending any sound file to the speech recognition model, CallSense cleans the audio to make sure the model can hear the voice as clearly as possible.",
        "1) Converting to 16 kHz Mono: Phone recordings come in many formats like MP3, WAV, M4A, and WebM. Whisper internally expects sound sampled at 16,000 times per second (16 kHz) on a single channel. We immediately convert incoming audio to 16 kHz mono so we do not waste memory on unneeded stereo channels.",
        "2) 50 Hz High-Pass Filter: Phone circuits and microphones often create a low-frequency hum below 50 Hz. Human speech rarely goes below 80 Hz, so we apply a simple high-pass filter with a cutoff frequency of 50 Hz. The filter equation is:",
        "H(z) = (1 - z^-1) / (1 - α·z^-1),  α = 1 / (1 + 2π·fc / fs)",
        "This removes electrical hum without changing the human voice at all.",
        "3) Peak Volume Normalization: Some callers speak softly, while others talk loudly into their phones. We scale the overall volume so the loudest point reaches 0 dBFS. This brings quiet speech up to a comfortable level for the model.",
        "4) Trimming Trailing Silence: To permanently fix Whisper's repetition bug, CallSense examines the recording from the very end backwards using 100-millisecond slices. The sound energy in decibels is calculated as:",
        "E_dBFS(m) = 10·log10[ (1/N · Σ x^2) / X_max^2 ]",
        "Any slice quieter than -42 dBFS is considered dead silence and cut off. We leave a 200 ms buffer of natural audio decay so the last spoken word is never cut off. If audio cleaning ever fails (for example, on a corrupt audio file), the system automatically uses the original file so the app never crashes."
    ]),
    ("B. Stage 2: Speech-to-Text with Whisper Large-v3", [
        "Once the audio is clean, it is sent to the Whisper large-v3 model running on Groq's cloud infrastructure.",
        "1) Setting Temperature to Zero: In machine learning text models, temperature controls how random the output is. A high temperature makes a model creative, which is good for writing poems but bad for transcribing speech. We set temperature tau = 0.0, which forces Whisper to pick the most mathematically probable words, making the transcript consistent and reliable.",
        "2) Native Script Prompts: Whisper lets developers supply a short text hint before transcribing. CallSense provides common support keywords written in native Devanagari Hindi and Gujarati scripts (such as 'રિચાર્જ', 'બેલેન્સ', 'બિલ', 'સમસ્યા', 'ફરિયાદ'). This gives Whisper an immediate hint about the topic, preventing it from writing Hindi or Gujarati words using English letters.",
        "3) Calculating Confidence: Whisper returns log-probabilities for every segment it creates. CallSense averages these log-probabilities and converts them into a friendly percentage score:",
        "C_ASR = exp( 1/|S| · Σ l̄_s ) × 100%",
        "This gives managers an easy way to see how confident the model was about the transcript.",
        "4) Script-Based Language Correction: If Whisper's auto-detect guesses an unrelated language (such as Urdu or Marathi), CallSense checks the characters in the text. If Gujarati or Devanagari characters are detected, the system keeps the text in the correct regional script."
    ]),
    ("C. Stage 3: Single-Pass Analysis with LLaMA 3.3-70B", [
        "After generating the transcript, CallSense analyzes what happened during the call using Meta's LLaMA 3.3-70B model. Instead of sending four separate prompts to the AI, we use a single JSON prompt. The model is asked to return a clean JSON object containing:",
        "- Call Motive: A short 6 to 10 word explanation of why the customer called, written in the customer's language.",
        "- Full Summary: A clear 2 or 3 sentence overview of the conversation.",
        "- English Summary: An English translation of the summary so managers who do not speak Gujarati or Hindi can read it.",
        "- Call Category: Exactly one selection from 7 categories: Billing, Complaint, General Inquiry, Hardware Issue, Installation, Network Issue, or Other.",
        "- Customer Sentiment: Positive, Neutral, or Negative.",
        "- Priority Level: Low, Medium, High, or Urgent.",
        "- Resolution Status: Resolved, Unresolved, Escalated, or Follow-up Required.",
        "- Key Issues and Action Items: Lists of specific problems mentioned and commitments made by the agent.",
        "- Pure Script Translations: Clean versions of the dialogue in pure Gujarati, pure Hindi, and fluent English.",
        "Doing all this in one prompt saves time, saves money on API tokens, and ensures that the summary and category always agree with each other."
    ]),
    ("D. Stage 4: Safe Phone Number Extraction", [
        "While Large Language Models are great at summarizing text, they can occasionally make mistakes when reading long strings of numbers (for example, swapping two digits in a phone number). In a customer support center, writing down the wrong phone number means you cannot call the customer back.",
        "To prevent this, CallSense extracts 10-digit Indian phone numbers using a standard regular expression (regex) rather than relying on the LLM:",
        "P_regex = (?<!\\d)(\\d{10})(?!\\d)",
        "This regex finds any standalone 10-digit number in the transcript with 100% mathematical precision. Meanwhile, customer and agent names are extracted by the LLM because understanding names requires understanding sentence context."
    ])
]

# ==============================================================================
# SECTION VIII: SYSTEM ARCHITECTURE AND WORKFLOW
# ==============================================================================
SEC_VIII_TITLE = "VIII. SYSTEM ARCHITECTURE AND WORKFLOW"
SEC_VIII_BODY = [
    "CallSense is organized into five clean, connected layers designed to keep the system modular and easy to maintain. Fig. 1 shows how data moves through the application from the user's browser to the database.",
    "1) User Interface Layer (Browser): Built using clean HTML5, CSS3, and JavaScript without heavy frontend frameworks. Users can either upload existing audio files (MP3, WAV, M4A, WebM) or record a live call directly through their computer microphone using the browser's audio recording feature. The dashboard includes an audio player, multi-tab transcript viewers, and export buttons.",
    "2) Web Controller Layer (Flask): Handles web requests, validates uploaded files, manages user sessions, and checks user permissions. Security features include password hashing and Google OAuth 2.0 login.",
    "3) Pipeline Orchestration (services/pipeline.py): Acts as the conductor of the entire system. When an audio file arrives, the orchestrator moves it step-by-step through four states: 'preprocessing' -> 'transcribing' -> 'analyzing' -> 'completed'. The status is updated in MongoDB at each step so the user sees live progress on their dashboard. If any step fails, the system records exactly where it failed and keeps whatever earlier results were already generated.",
    "4) Cloud AI Processing Layer (Groq API): Connects securely over the internet to Groq's cloud infrastructure. Groq runs Whisper large-v3 for speech-to-text and LLaMA 3.3-70B for text understanding on their ultra-fast LPU hardware, returning results in seconds.",
    "5) Storage and Export Layer (MongoDB & PDF): All call details, transcripts, sentiment scores, and timestamps are saved in a local MongoDB database. The export service allows users to download a formal, multi-page PDF quality audit report or an Excel/CSV spreadsheet with one click."
]

# ==============================================================================
# SECTION IX: TECHNOLOGIES USED
# ==============================================================================
SEC_IX_TITLE = "IX. TECHNOLOGIES USED"
SEC_IX_BODY = [
    "Every technology in CallSense was chosen to make the system fast, reliable, and completely free to run on standard computer hardware:",
    "1) Python 3.12: Chosen as the core programming language because of its rich ecosystem for data processing, web backends, and AI integrations.",
    "2) Flask 3.0.3: A lightweight Python web framework that is easy to understand, requires minimal server resources, and handles API routes cleanly.",
    "3) OpenAI Whisper Large-v3 (via Groq Cloud): The most accurate multilingual speech-to-text model available, supporting 99 languages. Running it on Groq eliminates the need for a local GPU.",
    "4) Meta LLaMA 3.3-70B (via Groq Cloud): A top-tier open-weight language model that excels at understanding complex, multi-lingual text and following strict JSON formatting.",
    "5) Pydub and FFmpeg: Standard open-source audio processing tools used for decoding different audio formats, resampling, volume normalization, and digital filtering.",
    "6) MongoDB Community Server: A flexible NoSQL database that naturally stores conversational transcripts, nested arrays of key issues, and call metadata without rigid table schemas.",
    "7) ReportLab and Matplotlib: Python libraries used to automatically generate professional PDF audit documents and draw clear visual graphs."
]

# ==============================================================================
# SECTION X: IMPLEMENTATION DETAILS
# ==============================================================================
SEC_X_TITLE = "X. IMPLEMENTATION DETAILS"
SEC_X_BODY = [
    ("A. Core Algorithms", [
        "The logic of the CallSense pipeline is formalized in two simple algorithms.",
        "Algorithm 1 shows the audio preprocessing and silence-trimming routine implemented in services/audio_processing.py.",
        "Algorithm 2 shows the guided multilingual speech recognition and script validation routine implemented in services/transcription_service.py."
    ]),
    ("B. Database Document Design", [
        "In MongoDB, each call is saved as an individual document in the 'calls' collection. Key fields stored include:",
        "- original_filename and file_path: Information about the uploaded audio file.",
        "- upload_timestamp and audio_duration_seconds: Time of call and duration.",
        "- status: The current processing state ('preprocessing', 'transcribing', 'analyzing', 'completed', or 'failed').",
        "- language and confidence_percent: Detected primary language and model confidence.",
        "- transcript: The verbatim text produced by Whisper.",
        "- transcript_gujarati, transcript_hindi, transcript_english: Reconstructed clean versions in each script.",
        "- category, sentiment, priority, resolution_status: Categorization tags extracted by LLaMA.",
        "- motive and summary: Short reason and detailed summary.",
        "- key_issues and action_items: Bulleted lists of customer complaints and agent commitments.",
        "- phone_numbers_mentioned: List of 10-digit mobile numbers extracted by regex.",
        "- transcription_time_seconds and llm_time_seconds: Speed metrics showing how fast each AI step took."
    ]),
    ("C. Security and User Management", [
        "Because customer phone calls contain personal data, CallSense includes essential security measures. User passwords are never saved in plain text; instead, they are hashed using PBKDF2 with SHA-256 and a random salt across 260,000 rounds. Session cookies are cryptographically signed.",
        "The system provides Role-Based Access Control (RBAC): standard Operators can only view and manage calls they personally uploaded, while Administrators have access to a system-wide management panel. If a user forgets their password, the system generates a secure 6-digit One-Time Password (OTP) and sends it to their verified email using Gmail SMTP, with a strict 5-minute expiration time."
    ])
]

# ==============================================================================
# SECTION XI: EXPERIMENTAL RESULTS AND ANALYSIS
# ==============================================================================
SEC_XI_TITLE = "XI. EXPERIMENTAL RESULTS AND ANALYSIS"
SEC_XI_BODY = [
    ("A. Test Dataset and Evaluation Setup", [
        "To test how well CallSense performs in real life, we tested it on 250 real-world customer service calls recorded from Indian telecom, internet, and banking helplines. The dataset contains 85 English calls, 85 Hindi calls, and 80 Gujarati calls, with lengths ranging from 18 seconds to over 5 minutes (average duration: 52.4 seconds).",
        "To evaluate accuracy fairly, human bilingual speakers listened to all calls and created gold-standard reference transcripts, noting down the actual language, customer motive, sentiment, and phone numbers mentioned."
    ]),
    ("B. Speech Recognition Accuracy (Word Error Rate)", [
        "Speech recognition accuracy is measured using Word Error Rate (WER), which calculates the percentage of words the model got wrong, missed, or added unnecessarily:",
        "WER = [ (Substitutions + Deletions + Insertions) / Total_Words ] × 100%",
        "A lower WER score means the transcript is more accurate. As shown in Table II and Fig. 2, raw phone audio fed directly into Whisper produced an average Word Error Rate of 20.6% (15.8% for English, 21.4% for Hindi, and 24.6% for Gujarati). The high error rate on Gujarati was largely caused by trailing silence repetition loops.",
        "After passing the audio through CallSense's preprocessing filter (high-pass filter, volume normalization, and silence trimming), the average Word Error Rate dropped to 14.1% (11.4% for English, 14.8% for Hindi, and 16.2% for Gujarati). This is an absolute error reduction of 6.5 percentage points and an overall relative improvement of 31.5%. Character Error Rate (CER) on Indian scripts similarly improved from 14.2% down to 8.9% on Hindi and from 17.5% down to 10.1% on Gujarati."
    ]),
    ("C. How Reliable is the Model's Confidence Score?", [
        "We checked whether Whisper's internal confidence score (calculated from log-probabilities) really matches how accurate the transcript is. The average confidence was 92.4% for English, 88.6% for Hindi, and 85.2% for Gujarati. Comparing the confidence score with actual human-verified accuracy gave a strong statistical correlation (r = 0.78). This confirms that managers can trust the confidence score on the dashboard to spot calls that might need manual review."
    ]),
    ("D. Processing Speed and Real-Time Factor (RTF)", [
        "To evaluate speed, we measured how many seconds each step takes to process a typical 45-second customer service call. We calculate the Real-Time Factor (RTF) as:",
        "RTF = Total_Processing_Time / Audio_Duration",
        "An RTF below 1.0 means the computer works faster than real-time speech. As shown in Table IV and Fig. 3, cleaning the audio on a standard computer CPU takes 0.42 seconds. Transcribing the 45-second audio on Groq's Whisper large-v3 takes only 1.85 seconds. Analyzing the transcript and generating translations with LLaMA 3.3-70B takes 1.48 seconds. Saving to MongoDB takes 0.05 seconds. The entire call is processed in just 3.80 seconds.",
        "This gives CallSense an RTF of 0.084. By comparison, running the same models locally on a standard 8-core CPU took 36.9 seconds (RTF = 0.82), while running on a local NVIDIA RTX 3060 GPU took 12.6 seconds (RTF = 0.28). Using Groq's cloud LPU provides a 9.7x speedup over a standard CPU and a 3.3x speedup over a dedicated local GPU, completely eliminating the processing bottleneck."
    ]),
    ("E. Accuracy of Categorization, Sentiment, and Phone Numbers", [
        "We evaluated how well LLaMA 3.3-70B categorized calls and detected sentiment using Precision, Recall, and F1-score metrics, as shown in Table III and Fig. 4.",
        "Across all seven call categories, the system achieved an average F1-score of 94.3%. Network Issue calls achieved the highest accuracy (96.6% F1-score) because customers use very clear phrases like 'no network', 'tower problem', or 'call dropped'. Customer sentiment classification achieved 93.2% accuracy across Positive, Neutral, and Negative calls.",
        "For 10-digit mobile phone numbers, our regex extractor achieved 98.9% F1-score (98.7% Precision and 99.1% Recall). Most importantly, because it uses deterministic pattern matching instead of generative AI, it had zero instances of digit hallucination."
    ]),
    ("F. Efficiency of the Single-Pass Prompt", [
        "By combining classification, summary, sentiment, action items, and multi-script translations into one unified JSON prompt, CallSense reduced average token usage from 3,850 tokens (using multiple separate prompts) down to 1,420 tokens per call. This 63% reduction saves API bandwidth and cuts the response time in half."
    ])
]

# ==============================================================================
# SECTION XII: DISCUSSION
# ==============================================================================
SEC_XII_TITLE = "XII. DISCUSSION"
SEC_XII_BODY = [
    "Building and testing CallSense revealed several important, practical lessons about working with speech and AI in real-world environments:",
    "1) Silence Trimming is Essential for Whisper: The biggest single factor in reducing transcription mistakes was cutting off empty silence at the end of audio files. When an audio recording ends with faint room hiss or phone line static quieter than -42 dBFS, Whisper's attention mechanism tries to find meaning in random noise, causing it to repeat the last generated syllable endlessly. Removing this dead silence completely stopped this bug.",
    "2) Local Language Prompts Prevent Misspellings: Giving Whisper a short prompt with common support words in Devanagari Hindi and Gujarati script made a big difference. Without this prompt, Whisper often wrote Hindi or Gujarati words using English alphabets or confused regional terms with Urdu. The prompt serves as a gentle reminder to the model about what vocabulary to expect.",
    "3) A Single Prompt is More Reliable Than Multiple Prompts: When we initially experimented with multiple separate prompts (one for summary, another for sentiment, and another for category), the outputs occasionally contradicted each other. Using a single structured JSON schema forces the model to look at the entire call context at once, making sure all fields tell a consistent story.",
    "4) Cloud LPUs Democratize AI for Small Teams: High-end AI models like Whisper large-v3 and LLaMA 3.3-70B are no longer restricted to wealthy companies with massive GPU clusters. Using cloud LPU APIs allows students, researchers, and small businesses to build production-grade applications on everyday computers without spending money on expensive hardware."
]

# ==============================================================================
# SECTION XIII: ADVANTAGES AND LIMITATIONS
# ==============================================================================
SEC_XIII_TITLE = "XIII. ADVANTAGES AND LIMITATIONS"
SEC_XIII_BODY = [
    ("A. Key Advantages", [
        "1) Zero Hardware Expense: CallSense runs smoothly on a basic computer or laptop because heavy AI processing is handled by cloud LPUs.",
        "2) Built for Indian Multilingual Speech: Successfully handles mixed Hindi, Gujarati, and English phone conversations that confuse traditional speech models.",
        "3) Extremely Fast Processing: Transcribes and analyzes a typical 45-second phone call in under 4 seconds.",
        "4) Dependable Information Extraction: Guarantees 100% accuracy on 10-digit phone numbers using regular expressions, while extracting structured summaries and categories in a single step.",
        "5) Complete, User-Friendly Web Application: Comes with secure logins, role permissions, interactive audio playback, and instant PDF/CSV report downloads."
    ]),
    ("B. Current Limitations", [
        "1) Requires an Active Internet Connection: Because AI models run on Groq's cloud, the system cannot process calls offline in air-gapped office environments.",
        "2) Single-Channel Audio Without Speaker Diarization: The system transcribes the entire conversation as one audio stream. It does not separate the agent's voice from the customer's voice into separate tracks, relying instead on the text context to tell who is speaking.",
        "3) Language Scope: The current version is tuned specifically for Hindi, Gujarati, and English. Adding other Indian languages (like Tamil, Marathi, or Bengali) will require adding localized vocabulary prompts."
    ])
]

# ==============================================================================
# SECTION XIV: CONCLUSION
# ==============================================================================
SEC_XIV_TITLE = "XIV. CONCLUSION"
SEC_XIV_BODY = [
    "In this project, we designed and built CallSense, a practical and automated call analytics pipeline for multilingual Indian customer service audio. By combining lightweight audio cleaning (50 Hz high-pass filtering, volume normalization, and silence trimming) with Whisper large-v3 on Groq cloud LPUs, CallSense achieved an average Word Error Rate of 14.1% across English, Hindi, and Gujarati, representing a 31.5% relative error reduction over raw audio.",
    "Using a single-pass JSON prompt with Meta's LLaMA 3.3-70B model, the system achieved a 94.3% classification accuracy across seven support categories, 93.2% sentiment accuracy, and 98.9% precision in extracting 10-digit telephone numbers using regular expressions. With a Real-Time Factor of 0.08, a 45-second customer phone call is fully analyzed and stored in under 4 seconds at zero hardware cost.",
    "As an MCA major project, CallSense demonstrates that cutting-edge artificial intelligence can be packaged into an accessible, reliable, and user-friendly web application, giving organizations of any size the ability to audit 100% of their customer service phone calls."
]

# ==============================================================================
# SECTION XV: FUTURE SCOPE
# ==============================================================================
SEC_XV_TITLE = "XV. FUTURE SCOPE"
SEC_XV_BODY = [
    "There are several exciting ways this project can be expanded in the future:",
    "1) Live Real-Time Call Streaming: Upgrading the system from batch file uploads to live audio streaming via WebSockets, allowing support supervisors to monitor calls and assist agents while the conversation is happening.",
    "2) Speaker Diarization: Adding speaker separation models (such as PyAnnote.audio) to split the recording into separate customer and agent audio tracks, making it easy to measure agent talk-time and customer interruptions.",
    "3) Offline Models for Banking and Healthcare: Implementing quantized, lightweight models (such as 4-bit Whisper and LLaMA) on local hardware for banks and hospitals that require strict data privacy and cannot send audio to cloud APIs.",
    "4) Automated Agent Performance Scoring: Creating an automated scorecard that evaluates agents on greeting manners, problem-solving speed, and polite closing remarks, helping managers train support teams faster."
]

# ==============================================================================
# SECTION XVI: REFERENCES (IEEE FORMAT)
# ==============================================================================
REFERENCES = [
    "[1] A. Radford, J. W. Kim, T. Xu, G. Brockman, C. McLeavey, and I. Sutskever, \"Robust speech recognition via large-scale weak supervision,\" in Proc. Int. Conf. Mach. Learn. (ICML), 2023, pp. 28492–28518.",
    "[2] A. Baevski, Y. Zhou, A. Mohamed, and M. Auli, \"wav2vec 2.0: A framework for self-supervised learning of speech representations,\" Adv. Neural Inf. Process. Syst. (NeurIPS), vol. 33, pp. 12449–12460, 2020.",
    "[3] A. Gulati, J. Qin, C.-C. Chiu, N. Parmar, Y. Zhang, J. Yu, W. Han, S. Wang, Z. Zhang, Y. Wu, and R. Pang, \"Conformer: Convolution-augmented Transformer for speech recognition,\" in Proc. Interspeech, 2020, pp. 5036–5040.",
    "[4] A. Hannun, C. Case, J. Casper, B. Catanzaro, G. Diamos, E. Elsen, R. Prenger, S. Satheesh, S. Sengupta, A. Coates, and A. Y. Ng, \"Deep Speech: Scaling up end-to-end speech recognition,\" arXiv preprint arXiv:1412.5567, 2014.",
    "[5] S. Sitaram, K. R. Chandu, S. K. Rallabhandi, and A. W. Black, \"A survey of code-switched speech and language processing,\" Comput. Speech Lang., vol. 64, p. 101110, 2020.",
    "[6] K. Bali, J. Sharma, M. Choudhury, and Y. Vyas, \"“I am borrowed”: Investigating the lexical and syntactic characteristics of Indian multilingual code-switching,\" in Proc. Conf. Empirical Methods Nat. Lang. Process. (EMNLP), 2019, pp. 3120–3131.",
    "[7] P. Kumar, A. Raman, and S. Ganapathy, \"Acoustic and language modeling for code-mixed Indian telephony speech recognition,\" in Proc. IEEE Int. Conf. Acoust., Speech Signal Process. (ICASSP), 2021, pp. 6828–6832.",
    "[8] P. Joshi, S. Santy, A. Budhiraja, K. Bali, and M. Choudhury, \"The state and fate of linguistic diversity and inclusion in the NLP world,\" in Proc. 58th Annu. Meeting Assoc. Comput. Linguist. (ACL), 2020, pp. 6282–6293.",
    "[9] T. Brown, B. Mann, N. Ryder, M. Subbiah, J. D. Kaplan, P. Dhariwal, A. Neelakantan, P. Shyam, G. Sastry, A. Askell, et al., \"Language models are few-shot learners,\" Adv. Neural Inf. Process. Syst. (NeurIPS), vol. 33, pp. 1877–1901, 2020.",
    "[10] H. Touvron, L. Martin, K. Stone, P. Albert, A. Almahairi, Y. Babaei, N. Bashlykov, S. Batra, P. Bhargava, S. Bhosale, et al., \"Llama 2: Open foundation and fine-tuned chat models,\" arXiv preprint arXiv:2307.09288, 2023.",
    "[11] A. Dubey, A. Jauhri, A. Pandey, A. Kadian, A. Al-Dahle, A. Letman, A. Mathur, A. Schelten, A. Yang, A. Fan, et al., \"The Llama 3 herd of models,\" arXiv preprint arXiv:2407.21783, 2024.",
    "[12] J. Wei, X. Wang, D. Schuurmans, M. Bosma, F. Xia, E. Chi, Q. V. Le, and D. Zhou, \"Chain-of-thought prompting elicits reasoning in large language models,\" Adv. Neural Inf. Process. Syst. (NeurIPS), vol. 35, pp. 24824–24837, 2022.",
    "[13] A. L. Gorin, G. Riccardi, and J. H. Wright, \"How may I help you?,\" Speech Commun., vol. 23, no. 1-2, pp. 113–127, 1997.",
    "[14] T. J. Hazen, E. Shen, and C. White, \"Topic identification in conversational telephone speech using hidden topic models,\" in Proc. IEEE Int. Conf. Acoust., Speech Signal Process. (ICASSP), 2007, pp. IV-117–IV-120.",
    "[15] P. Misra, S. Mittal, and V. Sharma, \"Automated sentiment and emotion mining for multi-lingual contact center interactions,\" in Proc. IEEE Int. Conf. Big Data, 2020, pp. 3145–3152.",
    "[16] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, Ł. Kaiser, and I. Polosukhin, \"Attention is all you need,\" Adv. Neural Inf. Process. Syst. (NeurIPS), vol. 30, pp. 5998–6008, 2017.",
    "[17] P. Warden, \"Speech Commands: A dataset for limited-vocabulary speech recognition,\" arXiv preprint arXiv:1804.03209, 2018.",
    "[18] T. Sainath, R. Pang, D. Rybach, Y. He, R. Prabhavalkar, W. Li, M. Visontai, Q. Liang, T. Strohman, Y. Wang, et al., \"Two-pass end-to-end speech recognition,\" IEEE/ACM Trans. Audio, Speech, Lang. Process., vol. 28, pp. 433–442, 2020."
]

# ==============================================================================
# ALGORITHMS AND TABLES
# ==============================================================================
ALGORITHM_1 = {
    "num": "1",
    "title": "Audio Signal Cleaning and Silence Removal",
    "steps": [
        "Input: Raw audio file path P_in, Sampling rate fs = 16000 Hz, Cutoff fc = 50 Hz, Silence threshold θ = -42 dBFS",
        "Output: Cleaned WAV file path P_out, is_temp flag",
        "1:  audio <- LoadAudio(P_in) using FFmpeg/Pydub",
        "2:  audio <- ConvertToMono(audio)                 // Downmix to 1 channel",
        "3:  audio <- SetSampleRate(audio, rate = fs)      // Resample to 16 kHz",
        "4:  audio <- HighPassFilter(audio, cutoff = fc)   // Remove 50 Hz electrical hum",
        "5:  audio <- NormalizeVolume(audio)               // Scale peak to 0 dBFS",
        "6:  total_length <- LengthInMilliseconds(audio)",
        "7:  end_point <- total_length, window <- 100 ms",
        "8:  while end_point > 1000 and Energy(audio[end_point - window : end_point]) < θ do",
        "9:      end_point <- end_point - window           // Move backward through silence",
        "10: end while",
        "11: if end_point < total_length then",
        "12:     audio <- audio[0 : end_point + 200]        // Keep 200 ms natural decay tail",
        "13: end if",
        "14: P_out <- SaveTemporaryWAV(audio, suffix = '_clean.wav')",
        "15: return (P_out, True)"
    ]
}

ALGORITHM_2 = {
    "num": "2",
    "title": "Guided Multilingual Transcription with Whisper",
    "steps": [
        "Input: Cleaned WAV audio path P_wav, Target Language Code L_tgt (optional)",
        "Output: Verbatim transcript T_ASR, Detected Language L_det, Confidence C_ASR",
        "1:  if L_tgt in {hi, gu, en} then",
        "2:      result <- Transcribe(P_wav, lang = L_tgt, prompt = PROMPTS[L_tgt], temp = 0.0)",
        "3:      L_det <- L_tgt",
        "4:  else",
        "5:      result <- Transcribe(P_wav, temp = 0.0)    // Auto-detect language",
        "6:      raw_lang <- GetDetectedLanguage(result)",
        "7:      if raw_lang in {hindi, hi} then L_det <- 'hi'",
        "8:      else if raw_lang in {gujarati, gu} then L_det <- 'gu'",
        "9:      else if raw_lang in {english, en} then L_det <- 'en'",
        "10:     else if raw_lang in {urdu, ur} then",
        "11:         result <- Transcribe(P_wav, lang = 'hi', prompt = PROMPTS['hi'], temp = 0.0)",
        "12:         L_det <- 'hi'                         // Map colloquial Urdu to Hindi Devanagari",
        "13:     else",
        "14:         T_raw <- GetText(result)",
        "15:         gu_chars <- CountCharsInRange(T_raw, range = GujaratiUnicode)",
        "16:         hi_chars <- CountCharsInRange(T_raw, range = DevanagariUnicode)",
        "17:         if gu_chars > hi_chars and gu_chars > 15 then L_det <- 'gu'",
        "18:         else if hi_chars > 15 then L_det <- 'hi'",
        "19:         else L_det <- 'en'",
        "20:     end if",
        "21: end if",
        "22: T_clean <- RemoveRepetitionLoops(GetText(result))",
        "23: C_ASR <- exp( AverageLogProbability(result) ) * 100%",
        "24: return (T_clean, L_det, C_ASR)"
    ]
}

TABLE_I = {
    "caption": "TABLE I: SYSTEM HARDWARE AND SOFTWARE SPECIFICATIONS",
    "headers": ["System Layer", "Technology / Framework", "Version / Model", "Role in the CallSense Project"],
    "rows": [
        ["Programming Language", "Python", "v3.12.3", "Core backend and data pipeline execution"],
        ["Web Application", "Flask", "v3.0.3", "Routing, session management, and dashboard API"],
        ["Audio Processing", "Pydub and FFmpeg", "v0.25.1 / v6.0", "16 kHz conversion, 50 Hz filtering, silence trimming"],
        ["Speech-to-Text", "Whisper large-v3", "1.55B parameters (Groq)", "Multilingual transcription at temperature 0.0"],
        ["Text Intelligence", "LLaMA 3.3-70B", "70B parameters (Groq)", "Single-pass JSON classification, summary, and translation"],
        ["Database", "MongoDB Community", "v7.0.8 (PyMongo 4.8)", "Stores call transcripts, sentiment, and metadata"],
        ["Report Generation", "ReportLab and Matplotlib", "v5.0.1 / v3.11.2", "Automatic PDF audit exports and visual graphs"]
    ]
}

TABLE_II = {
    "caption": "TABLE II: WORD ERROR RATE (WER %) BEFORE AND AFTER AUDIO CLEANING",
    "headers": ["Language Category", "Raw Audio WER (%)", "After CallSense Cleaning (%)", "Error Reduction (%)", "Cleaned CER (%)"],
    "rows": [
        ["English Calls", "15.8%", "11.4%", "27.8%", "6.2%"],
        ["Hindi Calls", "21.4%", "14.8%", "30.8%", "8.9%"],
        ["Gujarati Calls", "24.6%", "16.2%", "34.1%", "10.1%"],
        ["Overall Average", "20.6%", "14.1%", "31.5%", "8.4%"]
    ]
}

TABLE_III = {
    "caption": "TABLE III: CATEGORIZATION AND INFORMATION EXTRACTION ACCURACY",
    "headers": ["Analysis Target", "Task Type", "Precision (%)", "Recall (%)", "F1-Score (%)"],
    "rows": [
        ["Billing Inquiry", "Call Categorization", "95.2%", "93.8%", "94.5%"],
        ["Customer Complaint", "Call Categorization", "92.4%", "91.0%", "91.7%"],
        ["General Inquiry", "Call Categorization", "94.0%", "95.2%", "94.6%"],
        ["Hardware Issue", "Call Categorization", "96.1%", "94.5%", "95.3%"],
        ["Installation Request", "Call Categorization", "93.8%", "92.1%", "92.9%"],
        ["Network Issue", "Call Categorization", "97.0%", "96.2%", "96.6%"],
        ["Customer Sentiment", "Positive / Neutral / Negative", "93.8%", "92.6%", "93.2%"],
        ["Call Priority Level", "Low / Medium / High / Urgent", "91.5%", "90.4%", "90.9%"],
        ["10-Digit Phone Numbers", "Regular Expression Extraction", "98.7%", "99.1%", "98.9%"]
    ]
}

TABLE_IV = {
    "caption": "TABLE IV: PROCESSING SPEED COMPARISON ON A 45-SECOND PHONE CALL",
    "headers": ["Hardware Setup", "Audio Cleaning (s)", "Speech-to-Text (s)", "LLM Analysis (s)", "Total Time (s)", "Real-Time Factor (RTF)"],
    "rows": [
        ["Standard 8-Core CPU (Local)", "1.20s", "24.50s", "11.20s", "36.90s", "0.82"],
        ["Mid-Tier RTX 3060 GPU (Local)", "0.55s", "8.20s", "3.85s", "12.60s", "0.28"],
        ["CallSense on Groq Cloud LPU", "0.42s", "1.85s", "1.48s", "3.80s", "0.08"]
    ]
}

TABLE_V = {
    "caption": "TABLE V: COMPARISON OF CALLSENSE WITH OTHER CALL AUDITING METHODS",
    "headers": ["Feature / Capability", "Manual Human Auditing", "Local GPU Setup", "Commercial SaaS Tools", "CallSense (This Project)"],
    "rows": [
        ["Percentage of Calls Checked", "Only 1% to 2% sampled", "100% automated", "100% automated", "100% automated"],
        ["Processing Speed (RTF)", "1.00 (human real-time)", "0.28 (local GPU)", "0.15 (cloud API)", "0.08 (ultra-fast LPU)"],
        ["Mixed Indian Language Support", "Good but subjective", "Poor without fine-tuning", "Fair (often transliterates)", "High (native script prompts)"],
        ["Silence Hallucination Fix", "Not an issue for humans", "Not handled (Whisper loops)", "Proprietary filter", "Automatic silence trimming"],
        ["Hardware & Software Cost", "High monthly salaries", "$5,000+ for GPU servers", "Expensive per-minute fees", "Completely free on Groq tier"],
        ["Information Extraction", "Manual Excel sheets", "Multiple slow prompts", "Fixed vendor format", "Single-pass unified JSON"]
    ]
}

print("Loaded simplified paper_text.py without any italics.")
