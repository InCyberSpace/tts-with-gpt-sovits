<h1>Discord TTS with GPT-SoVITS</h1>

<h2>Installation</h2>
<ol>
  <li>Download and install GPT-SoVITS from the <a href="https://github.com/RVC-Boss/GPT-SoVITS">official GitHub repository</a>.</li>
  <li>Clone this repo and install dependencies:
    <pre><code>git clone https://github.com/InCyberSpace/tts-with-gpt-sovits
cd tts-with-gpt-sovits
pip install -r requirements.txt</code></pre>
  </li>
</ol>

<h2>Setup</h2>
<ol>
  <li>Fill out <code>.env_example</code> with your credentials and rename it to <code>.env</code></li>
  <li>Fill out <code>./data/config_example.json</code> and rename it to <code>config.json</code></li>
  <li>Fill out <code>./data/voices_example.json</code> and rename it to <code>voices.json</code></li>
  <li>Add your reference audio files to <code>./data/ref_audios/</code></li>
</ol>

<h2>Run</h2>
<ol>
  <li>Start the GPT-SoVITS API server:
    <pre><code>python api_v2.py</code></pre>
  </li>
  <li>Start the TTS bot:
    <pre><code>python main.py</code></pre>
  </li>
</ol>
