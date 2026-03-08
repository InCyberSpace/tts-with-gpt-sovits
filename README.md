<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Discord TTS with GPT-SoVITS</title>
<style>
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: #24292f;
    max-width: 800px;
    margin: 40px auto;
    padding: 0 24px;
  }
  h1 { font-size: 2em; border-bottom: 1px solid #d0d7de; padding-bottom: 10px; margin: 24px 0 16px; }
  h2 { font-size: 1.5em; border-bottom: 1px solid #d0d7de; padding-bottom: 8px; margin: 24px 0 16px; }
  ol { padding-left: 2em; margin: 0 0 16px; }
  li { margin: 6px 0; }
  code {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 85%;
    background: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 2px 6px;
  }
  pre {
    background: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 16px;
    overflow-x: auto;
    margin: 10px 0;
  }
  pre code { background: none; border: none; padding: 0; font-size: 13px; }
  a { color: #0969da; text-decoration: none; }
  a:hover { text-decoration: underline; }
</style>
</head>
<body>

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

</body>
</html>
