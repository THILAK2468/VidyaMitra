// VidyaMitra Frontend Logic
document.addEventListener('DOMContentLoaded', () => {
  // State
  let currentLanguage = 'te';
  let mediaRecorder = null;
  let audioChunks = [];
  let isRecording = false;
  let timerInterval = null;
  let recordingStartTime = 0;
  let currentTopic = null;
  let conversationHistory = []; // stores [{question, answer}] bounded to 2-3 turns
  let currentQuizQuestions = [];

  // DOM Elements
  const langTeBtn = document.getElementById('lang-te');
  const langEnBtn = document.getElementById('lang-en');
  const authLangTeBtn = document.getElementById('auth-lang-te');
  const authLangEnBtn = document.getElementById('auth-lang-en');
  const topicChips = document.querySelectorAll('.topic-chip');
  const textForm = document.getElementById('text-form');
  const questionInput = document.getElementById('question-input');
  const submitBtn = document.getElementById('submit-btn');
  const micBtn = document.getElementById('mic-btn');
  const micIcon = document.getElementById('mic-icon');
  const voiceStatusText = document.getElementById('voice-status-text');
  const recordingTimer = document.getElementById('recording-timer');
  const progressBox = document.getElementById('progress-box');
  const resultsCard = document.getElementById('results-card');
  const resTopic = document.getElementById('res-topic');
  const resTimings = document.getElementById('res-timings');
  const resQuestion = document.getElementById('res-question');
  const resAnswer = document.getElementById('res-answer');
  const resSource = document.getElementById('res-source');
  const resExampleBox = document.getElementById('res-example-box');
  const resExample = document.getElementById('res-example');
  const resTermsBox = document.getElementById('res-terms-box');
  const resTerms = document.getElementById('res-terms');
  const resAudioBox = document.getElementById('res-audio-box');
  const audioPlayer = document.getElementById('audio-player');
  const resOosNotice = document.getElementById('res-oos-notice');
  const launchQuizBtn = document.getElementById('launch-quiz-btn');

  // Quiz DOM Elements
  const quizCard = document.getElementById('quiz-card');
  const quizTitle = document.getElementById('quiz-title');
  const closeQuizBtn = document.getElementById('close-quiz-btn');
  const quizForm = document.getElementById('quiz-form');
  const quizQuestionsList = document.getElementById('quiz-questions-list');
  const quizResultsBox = document.getElementById('quiz-results-box');
  const scoreNumber = document.getElementById('score-number');
  const scoreText = document.getElementById('score-text');
  const quizFeedbackList = document.getElementById('quiz-feedback-list');
  const quizRetryBtn = document.getElementById('quiz-retry-btn');

  // UI Translations
  const UI_TEXT = {
    te: {
      tagline: 'మీ భాషలో నేర్చుకోండి. మీ శైలిలో అర్థం చేసుకోండి.',
      topicsLabel: 'సిలబస్ పాఠాలు (Available Topics):',
      placeholder: 'మీ ప్రశ్నను ఇక్కడ టైప్ చేయండి... (e.g. కిరణజన్య సంయోగక్రియ అంటే ఏమిటి?)',
      submitBtn: 'అడుగు',
      micReady: 'మాట్లాడటానికి మైక్ బటన్ నొక్కండి (Click mic to speak)',
      micRecording: 'వింటున్నాను... మాట్లాడండి (Listening... Click to stop)',
      micStopping: 'ఆడియో ప్రాసెస్ అవుతోంది...',
      questionTitle: 'మీ ప్రశ్న (Your Question):',
      tutorTitle: 'విద్యామిత్ర సమాధానం (Tutor Explanation):',
      exampleTitle: '💡 రోజువారీ ఉదాహరణ (Daily-life Example):',
      termsTitle: '🔑 ముఖ్యమైన పదాలు (Key Vocabulary):',
      audioTitle: '🔊 సమాధానాన్ని వినండి (Click to Listen):',
      audioHint: '▶️ వినడానికి ప్లే బటన్ నొక్కండి (Click play to listen)',
      oosNotice: 'ℹ️ ఈ ప్రశ్న ప్రస్తుత 8వ తరగతి సిలబస్‌లో లేదు. దయచేసి పైన ఇచ్చిన పాఠాలలో ఒకదానిని అడగండి.',
      quizLaunch: '🎯 ఈ పాఠంపై క్విజ్ రాయండి (Take Quiz)',
      quizSubmit: 'సమాధానాలు సమర్పించు (Submit Quiz)',
      quizRetry: '🔄 మళ్లీ రాయండి (Retake Quiz)',
      sttLabel: '🎙️ స్పీచ్ నుండి గుర్తించిన పాఠ్యం (Speech Converted to Text):',
      auth: {
        subtitle: 'మీ భాషలో నేర్చుకోండి • AI Science Learning Companion',
        desc: '8వ తరగతి సైన్స్ పాఠాలను తెలుగులో సులభంగా అర్థం చేసుకోండి.',
        tabLogin: 'లాగిన్ (Login)',
        tabRegister: 'నమోదు (Register)',
        loginEmail: 'ఈమెయిల్ (Email)',
        loginPassword: 'పాస్‌వర్డ్ (Password)',
        loginBtn: 'లాగిన్ అవ్వండి (Login) ➔',
        noAccount: 'ఖాతా లేదా?',
        registerLink: 'ఇక్కడ నమోదు చేసుకోండి (Register)',
        regName: 'విద్యార్థి పేరు (Student Name)',
        regNamePlaceholder: 'మీ పూర్తి పేరు',
        regClass: 'తరగతి (Class / Grade)',
        regEmail: 'ఈమెయిల్ (Email)',
        regPassword: 'పాస్‌వర్డ్ (Password - కనీసం 6 అక్షరాలు)',
        regConfirmPassword: 'కన్ఫర్మ్ పాస్‌వర్డ్ (Confirm Password)',
        regBtn: 'నమోదు చేసుకోండి (Register) ➔',
        haveAccount: 'ఇప్పటికే ఖాతా ఉందా?',
        loginLink: 'ఇక్కడ లాగిన్ అవ్వండి (Login)',
        guestOr: 'లేదా (OR)',
        guestBtn: '🚀 అతిథిగా ప్రవేశించండి (Explore as Guest)'
      }
    },
    en: {
      tagline: 'Learn in your language. Understand in your way.',
      topicsLabel: 'Available Topics:',
      placeholder: 'Type your question here... (e.g. What is Photosynthesis?)',
      submitBtn: 'Ask',
      micReady: 'Click the mic button to speak',
      micRecording: 'Listening... Click to stop recording',
      micStopping: 'Processing audio...',
      questionTitle: 'Your Question:',
      tutorTitle: 'VidyaMitra Explanation:',
      exampleTitle: '💡 Daily-life Example:',
      termsTitle: '🔑 Key Vocabulary:',
      audioTitle: '🔊 Listen to Explanation (Click to Listen):',
      audioHint: '▶️ Click play button to listen to explanation',
      oosNotice: 'ℹ️ This question is outside our current Class 8 Science syllabus. Please choose one of the topics above.',
      quizLaunch: '🎯 Take Quiz on this Topic',
      quizSubmit: 'Submit Quiz',
      quizRetry: '🔄 Retake Quiz',
      sttLabel: '🎙️ Speech Converted to Text:',
      auth: {
        subtitle: 'Learn in your language • AI Science Learning Companion',
        desc: 'Understand Class 8 Science concepts with ease.',
        tabLogin: 'Login',
        tabRegister: 'Register',
        loginEmail: 'Email',
        loginPassword: 'Password',
        loginBtn: 'Sign In / Login ➔',
        noAccount: "Don't have an account?",
        registerLink: 'Register here',
        regName: 'Student Name',
        regNamePlaceholder: 'Your full name',
        regClass: 'Class / Grade',
        regEmail: 'Email',
        regPassword: 'Password (min 6 characters)',
        regConfirmPassword: 'Confirm Password',
        regBtn: 'Create Account / Register ➔',
        haveAccount: 'Already have an account?',
        loginLink: 'Sign In here',
        guestOr: 'OR',
        guestBtn: '🚀 Continue as Guest'
      }
    }
  };

  function setLanguage(lang) {
    currentLanguage = lang;
    
    // Synchronize Main Header language toggles
    if (langTeBtn && langEnBtn) {
      if (lang === 'te') {
        langTeBtn.classList.add('active');
        langEnBtn.classList.remove('active');
      } else {
        langEnBtn.classList.add('active');
        langTeBtn.classList.remove('active');
      }
    }

    // Synchronize Auth Screen language toggles
    if (authLangTeBtn && authLangEnBtn) {
      if (lang === 'te') {
        authLangTeBtn.classList.add('active');
        authLangEnBtn.classList.remove('active');
      } else {
        authLangEnBtn.classList.add('active');
        authLangTeBtn.classList.remove('active');
      }
    }

    const t = UI_TEXT[lang];

    // Main App Text Updates
    const taglineEl = document.querySelector('.logo-tagline');
    if (taglineEl) taglineEl.textContent = t.tagline;

    const lblTopicsEl = document.getElementById('lbl-topics');
    if (lblTopicsEl) lblTopicsEl.textContent = t.topicsLabel;

    if (questionInput) questionInput.placeholder = t.placeholder;
    if (submitBtn) {
      const submitSpan = submitBtn.querySelector('span:first-child');
      if (submitSpan) submitSpan.textContent = t.submitBtn;
    }
    if (!isRecording && voiceStatusText) voiceStatusText.textContent = t.micReady;

    const lblQuestionEl = document.getElementById('lbl-question');
    if (lblQuestionEl) lblQuestionEl.textContent = t.questionTitle;

    const tutorNameEl = document.querySelector('.tutor-name');
    if (tutorNameEl) tutorNameEl.textContent = t.tutorTitle;

    const exampleLabelEl = document.querySelector('.example-box .box-label');
    if (exampleLabelEl) exampleLabelEl.textContent = t.exampleTitle;

    const termsLabelEl = document.querySelector('.key-terms-box .box-label');
    if (termsLabelEl) termsLabelEl.textContent = t.termsTitle;

    const audioTitleEl = document.getElementById('lbl-audio-title') || document.querySelector('.audio-header span:first-child');
    if (audioTitleEl) audioTitleEl.textContent = t.audioTitle;

    const audioHintEl = document.getElementById('audio-hint');
    if (audioHintEl) audioHintEl.textContent = t.audioHint;

    if (resOosNotice) resOosNotice.textContent = t.oosNotice;

    if (launchQuizBtn) {
      const quizSpan = launchQuizBtn.querySelector('span');
      if (quizSpan) quizSpan.textContent = t.quizLaunch;
    }

    const sttLabel = document.getElementById('stt-live-label');
    if (sttLabel) sttLabel.textContent = t.sttLabel;

    // Auth Screen Text Updates
    const a = t.auth;
    const authSubtitle = document.getElementById('auth-hero-subtitle');
    if (authSubtitle) authSubtitle.textContent = a.subtitle;

    const authDesc = document.getElementById('auth-hero-desc');
    if (authDesc) authDesc.textContent = a.desc;

    const tabLoginBtnEl = document.getElementById('tab-login-btn');
    if (tabLoginBtnEl) tabLoginBtnEl.textContent = a.tabLogin;

    const tabRegisterBtnEl = document.getElementById('tab-register-btn');
    if (tabRegisterBtnEl) tabRegisterBtnEl.textContent = a.tabRegister;

    const lblLoginEmail = document.getElementById('lbl-login-email');
    if (lblLoginEmail) lblLoginEmail.textContent = a.loginEmail;

    const lblLoginPassword = document.getElementById('lbl-login-password');
    if (lblLoginPassword) lblLoginPassword.textContent = a.loginPassword;

    const loginSubmitBtn = document.getElementById('login-submit-btn');
    if (loginSubmitBtn) loginSubmitBtn.textContent = a.loginBtn;

    const lblNoAccount = document.getElementById('lbl-no-account');
    if (lblNoAccount) lblNoAccount.textContent = a.noAccount;

    const switchToRegisterEl = document.getElementById('switch-to-register');
    if (switchToRegisterEl) switchToRegisterEl.textContent = a.registerLink;

    const lblRegName = document.getElementById('lbl-reg-name');
    if (lblRegName) lblRegName.textContent = a.regName;

    const regNameInput = document.getElementById('reg-name');
    if (regNameInput) regNameInput.placeholder = a.regNamePlaceholder;

    const lblRegClass = document.getElementById('lbl-reg-class');
    if (lblRegClass) lblRegClass.textContent = a.regClass;

    const lblRegEmail = document.getElementById('lbl-reg-email');
    if (lblRegEmail) lblRegEmail.textContent = a.regEmail;

    const lblRegPassword = document.getElementById('lbl-reg-password');
    if (lblRegPassword) lblRegPassword.textContent = a.regPassword;

    const lblRegConfirmPassword = document.getElementById('lbl-reg-confirm-password');
    if (lblRegConfirmPassword) lblRegConfirmPassword.textContent = a.regConfirmPassword;

    const regSubmitBtn = document.getElementById('reg-submit-btn');
    if (regSubmitBtn) regSubmitBtn.textContent = a.regBtn;

    const lblHaveAccount = document.getElementById('lbl-have-account');
    if (lblHaveAccount) lblHaveAccount.textContent = a.haveAccount;

    const switchToLoginEl = document.getElementById('switch-to-login');
    if (switchToLoginEl) switchToLoginEl.textContent = a.loginLink;

    const lblGuestOr = document.getElementById('lbl-guest-or');
    if (lblGuestOr) lblGuestOr.textContent = a.guestOr;

    const guestEnterBtnEl = document.getElementById('guest-enter-btn');
    if (guestEnterBtnEl) guestEnterBtnEl.textContent = a.guestBtn;

    // Update Class dropdown options text
    const regClassSelect = document.getElementById('reg-class');
    if (regClassSelect) {
      const prevIndex = regClassSelect.selectedIndex >= 0 ? regClassSelect.selectedIndex : 2;
      const classOptions = lang === 'te' ? [
        { val: "6వ తరగతి (Class 6)", text: "6వ తరగతి (Class 6)" },
        { val: "7వ తరగతి (Class 7)", text: "7వ తరగతి (Class 7)" },
        { val: "8వ తరగతి (Class 8)", text: "8వ తరగతి (Class 8)" },
        { val: "9వ తరగతి (Class 9)", text: "9వ తరగతి (Class 9)" },
        { val: "10వ తరగతి (Class 10)", text: "10వ తరగతి (Class 10)" }
      ] : [
        { val: "Class 6", text: "Class 6" },
        { val: "Class 7", text: "Class 7" },
        { val: "Class 8", text: "Class 8" },
        { val: "Class 9", text: "Class 9" },
        { val: "Class 10", text: "Class 10" }
      ];
      regClassSelect.innerHTML = '';
      classOptions.forEach((opt, idx) => {
        const optEl = document.createElement('option');
        optEl.value = opt.val;
        optEl.textContent = opt.text;
        if (idx === prevIndex) optEl.selected = true;
        regClassSelect.appendChild(optEl);
      });
    }
  }

  // Language switcher button listeners
  if (langTeBtn) langTeBtn.addEventListener('click', () => setLanguage('te'));
  if (langEnBtn) langEnBtn.addEventListener('click', () => setLanguage('en'));
  if (authLangTeBtn) authLangTeBtn.addEventListener('click', () => setLanguage('te'));
  if (authLangEnBtn) authLangEnBtn.addEventListener('click', () => setLanguage('en'));

  // Topic Chips Click
  topicChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const query = chip.getAttribute('data-query');
      questionInput.value = query;
      submitTextQuestion(query);
    });
  });

  // Text Form Submission
  textForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = questionInput.value.trim();
    if (query) submitTextQuestion(query);
  });

  // Submit Text Question to /tutor/ask (Supports Follow-up Context)
  async function submitTextQuestion(query) {
    showProgress(['step-llm', 'step-tts']);
    resetResults();

    try {
      const response = await fetch('/tutor/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: query,
          language: currentLanguage,
          previous_topic: currentTopic,
          conversation_history: conversationHistory.slice(-2)
        })
      });

      const data = await response.json();
      hideProgress();

      if (data.success) {
        currentTopic = data.topic;
        conversationHistory.push({ question: query, answer: data.answer });

        displayResults({
          transcript: query,
          topic: data.topic,
          answer: data.answer,
          example: data.example,
          key_terms: data.key_terms || [],
          source: data.source || 'gemini_grounded',
          timings: { llm_latency: data.latency, total_latency: data.latency }
        });

        generateTtsAudio(data.answer);
      } else {
        displayOutOfScope(query, data.message);
      }
    } catch (err) {
      hideProgress();
      alert('Error fetching answer: ' + err.message);
    }
  }

  // Synthesize Text to Speech
  async function generateTtsAudio(text) {
    try {
      const response = await fetch('/voice/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text, language: currentLanguage })
      });
      const data = await response.json();
      if (data.success && data.audio_url) {
        resAudioBox.classList.remove('hidden');
        audioPlayer.src = data.audio_url;
        // Do NOT autoplay right after generation; play only when the user explicitly clicks the play button.
      }
    } catch (err) {
      console.warn('TTS auto-playback failed:', err);
    }
  }

  // Audio Recording State (Direct 16-bit PCM WAV for Gnani Prisma STT)
  let audioCtx = null;
  let mediaStreamSource = null;
  let scriptProcessor = null;
  let audioStream = null;
  let pcmBuffers = [];
  let currentSampleRate = 16000;

  // Microphone Recording Flow
  micBtn.addEventListener('click', async () => {
    if (!isRecording) {
      startRecording();
    } else {
      stopRecording();
    }
  });

  async function startRecording() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert(
        "Microphone API is disabled by your browser.\n\n" +
        "Please ensure you are opening VidyaMitra using:\n" +
        "👉 http://localhost:8000 or http://127.0.0.1:8000\n\n" +
        "(Browsers block microphone recording on non-localhost HTTP addresses)."
      );
      return;
    }

    try {
      audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
      currentSampleRate = audioCtx.sampleRate;
      mediaStreamSource = audioCtx.createMediaStreamSource(audioStream);
      scriptProcessor = audioCtx.createScriptProcessor(4096, 1, 1);
      pcmBuffers = [];

      scriptProcessor.onaudioprocess = (e) => {
        if (!isRecording) return;
        const channelData = e.inputBuffer.getChannelData(0);
        pcmBuffers.push(new Float32Array(channelData));
      };

      mediaStreamSource.connect(scriptProcessor);
      scriptProcessor.connect(audioCtx.destination);

      isRecording = true;
      micBtn.classList.add('recording');
      micIcon.textContent = '⏹️';
      voiceStatusText.textContent = UI_TEXT[currentLanguage].micRecording;
      recordingTimer.classList.remove('hidden');

      recordingStartTime = Date.now();
      timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
        const mins = String(Math.floor(elapsed / 60)).padStart(2, '0');
        const secs = String(elapsed % 60).padStart(2, '0');
        recordingTimer.textContent = `🔴 ${mins}:${secs}`;
      }, 500);

    } catch (err) {
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        alert(
          "Microphone permission was denied!\n\n" +
          "How to enable:\n" +
          "1. Click the 'View site information' or Lock 🔒 icon in the address bar (to the left of http://localhost:8000).\n" +
          "2. Toggle 'Microphone' to 'Allow' (or reset permissions).\n" +
          "3. Refresh the page and try again!"
        );
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        alert("No microphone found on your computer. Please check that your headset or mic is connected.");
      } else {
        alert('Microphone access error: ' + err.message);
      }
    }
  }

  function stopRecording() {
    if (!isRecording) return;
    isRecording = false;
    micBtn.classList.remove('recording');
    micIcon.textContent = '🎙️';
    voiceStatusText.textContent = UI_TEXT[currentLanguage].micStopping;
    recordingTimer.classList.add('hidden');
    clearInterval(timerInterval);

    // Stop and disconnect Web Audio nodes
    if (scriptProcessor) scriptProcessor.disconnect();
    if (mediaStreamSource) mediaStreamSource.disconnect();
    if (audioStream) audioStream.getTracks().forEach(t => t.stop());
    if (audioCtx && audioCtx.state !== 'closed') audioCtx.close();

    // Flatten Float32 PCM samples
    let totalLength = 0;
    for (let i = 0; i < pcmBuffers.length; i++) {
      totalLength += pcmBuffers[i].length;
    }

    if (totalLength === 0) {
      voiceStatusText.textContent = UI_TEXT[currentLanguage].micReady;
      return;
    }

    const mergedSamples = new Float32Array(totalLength);
    let offset = 0;
    for (let i = 0; i < pcmBuffers.length; i++) {
      mergedSamples.set(pcmBuffers[i], offset);
      offset += pcmBuffers[i].length;
    }

    // Encode directly to standard 16-bit Mono WAV required by Gnani Prisma STT
    const wavBlob = encodeWAV(mergedSamples, currentSampleRate);
    uploadVoiceQuestion(wavBlob, 'audio/wav');
  }

  // Canonical 16-bit Mono WAV encoder for Gnani Prisma STT compatibility
  function encodeWAV(samples, sampleRate) {
    const buffer = new ArrayBuffer(44 + samples.length * 2);
    const view = new DataView(buffer);

    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + samples.length * 2, true);
    writeString(view, 8, 'WAVE');
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);          // Subchunk1Size (16 for PCM)
    view.setUint16(20, 1, true);           // AudioFormat (1 = PCM)
    view.setUint16(22, 1, true);           // NumChannels (1 = Mono)
    view.setUint32(24, sampleRate, true);  // SampleRate
    view.setUint32(28, sampleRate * 2, true); // ByteRate (SampleRate * NumChannels * BitsPerSample/8)
    view.setUint16(32, 2, true);           // BlockAlign (NumChannels * BitsPerSample/8)
    view.setUint16(34, 16, true);          // BitsPerSample (16 bits)
    writeString(view, 36, 'data');
    view.setUint32(40, samples.length * 2, true);

    // Convert Float32 [-1.0, 1.0] to 16-bit signed PCM [-32768, 32767]
    let p = 44;
    for (let i = 0; i < samples.length; i++, p += 2) {
      const s = Math.max(-1, Math.min(1, samples[i]));
      view.setInt16(p, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }

    return new Blob([view], { type: 'audio/wav' });
  }

  function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  }

  // DOM Elements for Speech-to-Text Live Display
  const sttLiveBanner = document.getElementById('stt-live-banner');
  const sttLiveText = document.getElementById('stt-live-text');

  // Upload Voice Question to /voice/ask (Full Vertical Slice)
  async function uploadVoiceQuestion(audioBlob, mimeType) {
    showProgress(['step-stt', 'step-llm', 'step-tts']);
    resetResults();
    if (sttLiveBanner) sttLiveBanner.classList.add('hidden');

    const formData = new FormData();
    formData.append('audio_file', audioBlob, 'question.wav');
    formData.append('language', currentLanguage);
    formData.append('play_audio', 'true');
    if (currentTopic) {
      formData.append('previous_topic', currentTopic);
    }

    try {
      const response = await fetch('/voice/ask', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      hideProgress();
      voiceStatusText.textContent = UI_TEXT[currentLanguage].micReady;

      if (!response.ok) {
        throw new Error(data.detail || 'Voice processing failed');
      }

      // Display transcribed text on website (in both input box and live STT banner)
      if (data.transcript) {
        if (questionInput) questionInput.value = data.transcript;
        if (sttLiveBanner && sttLiveText) {
          sttLiveText.textContent = `"${data.transcript}"`;
          sttLiveBanner.classList.remove('hidden');
        }
      }

      if (data.success) {
        currentTopic = data.topic;
        conversationHistory.push({ question: data.transcript, answer: data.answer });
        displayResults(data);
      } else {
        displayOutOfScope(data.transcript, data.answer);
      }
    } catch (err) {
      hideProgress();
      voiceStatusText.textContent = UI_TEXT[currentLanguage].micReady;
      alert('Error: ' + err.message);
    }
  }

  // Display Result Data
  function displayResults(data) {
    resultsCard.classList.remove('hidden');
    resOosNotice.classList.add('hidden');

    resTopic.textContent = data.topic || 'Class 8 Science';
    resQuestion.textContent = data.transcript || questionInput.value;
    resAnswer.textContent = data.answer || '';
    resSource.textContent = data.source === 'gemini_grounded' ? 'Google Gemini 3.5 Flash (Grounded)' : 'Curriculum Direct';

    // Latency Timings
    if (data.timings) {
      const t = data.timings;
      let timingStr = `⚡ Total: ${t.total_latency || 0}s`;
      if (t.stt_latency) timingStr += ` • STT: ${t.stt_latency}s`;
      if (t.llm_latency) timingStr += ` • AI: ${t.llm_latency}s`;
      if (t.tts_latency) timingStr += ` • TTS: ${t.tts_latency}s`;
      resTimings.textContent = timingStr;
    }

    if (data.example) {
      resExampleBox.classList.remove('hidden');
      resExample.textContent = data.example;
    } else {
      resExampleBox.classList.add('hidden');
    }

    resTerms.innerHTML = '';
    if (data.key_terms && data.key_terms.length > 0) {
      resTermsBox.classList.remove('hidden');
      data.key_terms.forEach(term => {
        const span = document.createElement('span');
        span.className = 'term-tag';
        span.textContent = term;
        resTerms.appendChild(span);
      });
    } else {
      resTermsBox.classList.add('hidden');
    }

    if (data.audio_url) {
      resAudioBox.classList.remove('hidden');
      audioPlayer.src = data.audio_url;
      // Do NOT autoplay right after generation; play only when the user explicitly clicks the play button.
    } else {
      resAudioBox.classList.add('hidden');
    }

    resultsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function displayOutOfScope(query, message) {
    resultsCard.classList.remove('hidden');
    resOosNotice.classList.remove('hidden');
    resTopic.textContent = 'సిలబస్ వెలుపల (Out of Scope)';
    resQuestion.textContent = query;
    resAnswer.textContent = message;
    resExampleBox.classList.add('hidden');
    resTermsBox.classList.add('hidden');
    resAudioBox.classList.add('hidden');
    resTimings.textContent = '⚠️';
  }

  // --- QUIZ LOGIC ---
  launchQuizBtn.addEventListener('click', () => {
    if (!currentTopic) return;
    loadQuiz(currentTopic);
  });

  closeQuizBtn.addEventListener('click', () => {
    quizCard.classList.add('hidden');
  });

  quizRetryBtn.addEventListener('click', () => {
    if (currentTopic) loadQuiz(currentTopic);
  });

  async function loadQuiz(topic) {
    try {
      quizCard.classList.remove('hidden');
      quizForm.classList.remove('hidden');
      quizResultsBox.classList.add('hidden');
      quizQuestionsList.innerHTML = '<div class="spinner"></div>';
      quizCard.scrollIntoView({ behavior: 'smooth' });

      quizTitle.textContent = `🎯 ${topic} - క్విజ్ (Quiz)`;

      const response = await fetch(`/quiz/questions/${encodeURIComponent(topic)}?language=${currentLanguage}`);
      const data = await response.json();

      if (!data.success || !data.questions || data.questions.length === 0) {
        quizQuestionsList.innerHTML = '<p>ఈ పాఠానికి క్విజ్ ప్రశ్నలు సిద్ధంగా లేవు.</p>';
        return;
      }

      currentQuizQuestions = data.questions;
      renderQuizQuestions(data.questions);
    } catch (err) {
      quizQuestionsList.innerHTML = `<p>Error loading quiz: ${err.message}</p>`;
    }
  }

  function renderQuizQuestions(questions) {
    quizQuestionsList.innerHTML = '';
    questions.forEach((q, index) => {
      const qDiv = document.createElement('div');
      qDiv.className = 'quiz-question-item';

      const qTitle = document.createElement('div');
      qTitle.className = 'quiz-q-title';
      qTitle.textContent = `${index + 1}. ${q.question}`;
      qDiv.appendChild(qTitle);

      const optionsGroup = document.createElement('div');
      optionsGroup.className = 'quiz-options-group';

      q.options.forEach((optText, optIdx) => {
        const label = document.createElement('label');
        label.className = 'quiz-option-label';

        const radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = q.id;
        radio.value = optIdx;
        radio.required = true;

        label.appendChild(radio);
        label.appendChild(document.createTextNode(optText));
        optionsGroup.appendChild(label);
      });

      qDiv.appendChild(optionsGroup);
      quizQuestionsList.appendChild(qDiv);
    });
  }

  // Submit Quiz Answers
  quizForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const answers = {};

    currentQuizQuestions.forEach(q => {
      const checked = document.querySelector(`input[name="${q.id}"]:checked`);
      if (checked) {
        answers[q.id] = parseInt(checked.value, 10);
      }
    });

    try {
      const response = await fetch('/quiz/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic_id: currentTopic,
          answers: answers,
          language: currentLanguage
        })
      });

      const res = await response.json();
      if (res.success) {
        displayQuizResults(res);
      }
    } catch (err) {
      alert('Failed to submit quiz: ' + err.message);
    }
  });

  function displayQuizResults(res) {
    quizForm.classList.add('hidden');
    quizResultsBox.classList.remove('hidden');

    scoreNumber.textContent = `${res.score} / ${res.total}`;
    scoreText.textContent = res.encouragement;

    quizFeedbackList.innerHTML = '';
    res.feedback.forEach((f, idx) => {
      const item = document.createElement('div');
      item.className = `feedback-item ${f.is_correct ? 'correct' : 'incorrect'}`;

      const badge = document.createElement('div');
      badge.className = 'feedback-badge';
      badge.textContent = f.is_correct ? `✓ ప్రశ్న ${idx + 1}: సరైన సమాధానం!` : `✗ ప్రశ్న ${idx + 1}: సరికాని ఎంపిక`;
      item.appendChild(badge);

      if (!f.is_correct && f.correct_option_text) {
        const correctInfo = document.createElement('div');
        correctInfo.textContent = `సరైన సమాధానం: ${f.correct_option_text}`;
        item.appendChild(correctInfo);
      }

      const exp = document.createElement('div');
      exp.className = 'feedback-explanation';
      exp.textContent = `వివరణ: ${f.explanation}`;
      item.appendChild(exp);

      quizFeedbackList.appendChild(item);
    });

    quizResultsBox.scrollIntoView({ behavior: 'smooth' });
  }

  // Progress Box Helpers
  function showProgress(activeStepIds) {
    progressBox.classList.remove('hidden');
    ['step-stt', 'step-llm', 'step-tts'].forEach(id => {
      const el = document.getElementById(id);
      if (activeStepIds.includes(id)) {
        el.classList.add('active');
      } else {
        el.classList.remove('active');
      }
    });
  }

  function hideProgress() {
    progressBox.classList.add('hidden');
  }

  function resetResults() {
    resultsCard.classList.add('hidden');
    quizCard.classList.add('hidden');
    audioPlayer.pause();
    audioPlayer.src = '';
  }

  // ==========================================
  // Authentication & Screen Transition Management
  // (Login / Register Screen Appears First)
  // ==========================================
  const authScreen = document.getElementById('auth-screen');
  const mainApp = document.getElementById('main-app');
  const guestEnterBtn = document.getElementById('guest-enter-btn');
  const tabLoginBtn = document.getElementById('tab-login-btn');
  const tabRegisterBtn = document.getElementById('tab-register-btn');
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const switchToRegister = document.getElementById('switch-to-register');
  const switchToLogin = document.getElementById('switch-to-login');
  const loginError = document.getElementById('login-error');
  const registerError = document.getElementById('register-error');
  const registerSuccess = document.getElementById('register-success');
  const userProfileBadge = document.getElementById('user-profile-badge');
  const userDisplayName = document.getElementById('user-display-name');
  const logoutBtn = document.getElementById('logout-btn');

  // Password Visibility Toggle (Show / Hide)
  document.querySelectorAll('.toggle-password-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = btn.getAttribute('data-target');
      const targetInput = document.getElementById(targetId);
      if (targetInput) {
        if (targetInput.type === 'password') {
          targetInput.type = 'text';
          btn.textContent = '🙈';
          btn.title = 'Hide Password';
        } else {
          targetInput.type = 'password';
          btn.textContent = '👁️';
          btn.title = 'Show Password';
        }
      }
    });
  });

  // Switch to Main App View
  function showMainApp(user) {
    if (authScreen) authScreen.classList.add('hidden');
    if (mainApp) mainApp.classList.remove('hidden');
    if (userProfileBadge && user) {
      userProfileBadge.classList.remove('hidden');
      if (userDisplayName) {
        userDisplayName.textContent = `${user.name} (${user.student_class || '8వ తరగతి'})`;
      }
    }
  }

  // Switch to Auth Landing View (First View)
  function showAuthScreen() {
    if (mainApp) mainApp.classList.add('hidden');
    if (authScreen) authScreen.classList.remove('hidden');
    activateLoginTab();
  }

  // Tab Switchers
  function activateLoginTab() {
    if (tabLoginBtn) tabLoginBtn.classList.add('active');
    if (tabRegisterBtn) tabRegisterBtn.classList.remove('active');
    if (loginForm) loginForm.classList.remove('hidden');
    if (registerForm) registerForm.classList.add('hidden');
    clearAuthMessages();
  }

  function activateRegisterTab() {
    if (tabRegisterBtn) tabRegisterBtn.classList.add('active');
    if (tabLoginBtn) tabLoginBtn.classList.remove('active');
    if (registerForm) registerForm.classList.remove('hidden');
    if (loginForm) loginForm.classList.add('hidden');
    clearAuthMessages();
  }

  if (tabLoginBtn) tabLoginBtn.addEventListener('click', activateLoginTab);
  if (tabRegisterBtn) tabRegisterBtn.addEventListener('click', activateRegisterTab);
  if (switchToRegister) {
    switchToRegister.addEventListener('click', (e) => {
      e.preventDefault();
      activateRegisterTab();
    });
  }
  if (switchToLogin) {
    switchToLogin.addEventListener('click', (e) => {
      e.preventDefault();
      activateLoginTab();
    });
  }

  function clearAuthMessages() {
    if (loginError) {
      loginError.textContent = '';
      loginError.classList.add('hidden');
    }
    if (registerError) {
      registerError.textContent = '';
      registerError.classList.add('hidden');
    }
    if (registerSuccess) {
      registerSuccess.textContent = '';
      registerSuccess.classList.add('hidden');
    }
  }

  // Restore session or show Login page first
  function checkInitialAuth() {
    try {
      const stored = localStorage.getItem('vidyamitra_user');
      if (stored) {
        const user = JSON.parse(stored);
        if (user && user.name) {
          showMainApp(user);
          return;
        }
      }
    } catch (err) {
      console.warn('Session check failed:', err);
    }
    // Default: Show login page first
    showAuthScreen();
  }

  // Guest explore button
  if (guestEnterBtn) {
    guestEnterBtn.addEventListener('click', () => {
      const guestUser = {
        name: 'అతిథి విద్యార్థి (Guest Student)',
        student_class: '8వ తరగతి (Class 8)',
        email: 'guest@vidyamitra.local'
      };
      localStorage.setItem('vidyamitra_user', JSON.stringify(guestUser));
      showMainApp(guestUser);
    });
  }

  // Logout handler
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      localStorage.removeItem('vidyamitra_user');
      showAuthScreen();
    });
  }

  // Handle Login Form Submit
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearAuthMessages();

      const email = document.getElementById('login-email').value.trim();
      const password = document.getElementById('login-password').value;

      try {
        const response = await fetch('/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });

        const data = await response.json();
        if (!response.ok || !data.success) {
          loginError.textContent = data.detail || data.message || 'లాగిన్ విఫలమైంది. సరైన వివరాలు నమోదు చేయండి.';
          loginError.classList.remove('hidden');
          return;
        }

        // Save session & transition to Main App
        localStorage.setItem('vidyamitra_user', JSON.stringify(data.user));
        showMainApp(data.user);
        loginForm.reset();
      } catch (err) {
        loginError.textContent = 'సర్వర్ కనెక్ట్ కాలేదు: ' + err.message;
        loginError.classList.remove('hidden');
      }
    });
  }

  // Handle Registration Form Submit
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearAuthMessages();

      const name = document.getElementById('reg-name').value.trim();
      const student_class = document.getElementById('reg-class').value;
      const email = document.getElementById('reg-email').value.trim();
      const password = document.getElementById('reg-password').value;
      const confirm_password = document.getElementById('reg-confirm-password').value;

      if (password !== confirm_password) {
        registerError.textContent = 'పాస్‌వర్డ్ మరియు కన్ఫర్మ్ పాస్‌వర్డ్ సరిపోలలేదు (Passwords do not match).';
        registerError.classList.remove('hidden');
        return;
      }

      try {
        const response = await fetch('/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name,
            student_class,
            email,
            password,
            confirm_password
          })
        });

        const data = await response.json();
        if (!response.ok || !data.success) {
          registerError.textContent = data.detail || data.message || 'నమోదు విఫలమైంది.';
          registerError.classList.remove('hidden');
          return;
        }

        // Show success, save session, and transition to Main App
        registerSuccess.textContent = 'నమోదు విజయవంతమైంది! లాగిన్ అవుతోంది...';
        registerSuccess.classList.remove('hidden');
        localStorage.setItem('vidyamitra_user', JSON.stringify(data.user));

        setTimeout(() => {
          showMainApp(data.user);
          registerForm.reset();
        }, 1000);
      } catch (err) {
        registerError.textContent = 'సర్వర్ కనెక్ట్ కాలేదు: ' + err.message;
        registerError.classList.remove('hidden');
      }
    });
  }

  // Run initial language setup and authentication check on page load
  setLanguage('te');
  checkInitialAuth();
});
