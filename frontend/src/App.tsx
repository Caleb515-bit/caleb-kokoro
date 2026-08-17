import { useState, useEffect } from 'react'
import { fetchVoices, synthesize, previewVoice, getAudioUrl, type Voice } from './api'
import './App.css'

function App() {
  const [text, setText] = useState('')
  const [selectedVoice, setSelectedVoice] = useState('af_heart')
  const [voices, setVoices] = useState<Voice[]>([])
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [previewing, setPreviewing] = useState<string | null>(null)

  useEffect(() => {
    fetchVoices()
      .then(res => setVoices(res.voices))
      .catch(err => setError('Failed to load voices: ' + err.message))
  }, [])

  const voicesByLang = voices.reduce<Record<string, Voice[]>>((acc, v) => {
    if (!acc[v.lang]) acc[v.lang] = []
    acc[v.lang].push(v)
    return acc
  }, {})

  const handleSynthesize = async () => {
    if (!text.trim()) return
    setLoading(true)
    setError(null)
    setAudioUrl(null)
    try {
      const response = await synthesize(text, 'kokoro', selectedVoice)
      setAudioUrl(getAudioUrl(response.url))
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  const handlePreview = async (voiceId: string) => {
    setPreviewing(voiceId)
    setError(null)
    try {
      const response = await previewVoice(voiceId)
      const url = getAudioUrl(response.url)
      const audio = new Audio(url)
      audio.play()
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setPreviewing(null)
    }
  }

  return (
    <div className="container">
      <h1>Kokoro TTS Studio</h1>
      <p className="subtitle">{voices.length} voices across {Object.keys(voicesByLang).length} languages</p>

      <div className="form-group">
        <label>Text to Synthesize</label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type something to hear it spoken..."
          rows={4}
        />
      </div>

      <div className="form-group">
        <label>Select a Voice</label>
        <div className="voice-grid">
          {Object.entries(voicesByLang).map(([lang, langVoices]) => (
            <div key={lang} className="voice-group">
              <h3 className="voice-group-title">{lang}</h3>
              <div className="voice-chips">
                {langVoices.map(voice => (
                  <button
                    key={voice.id}
                    className={`voice-chip ${selectedVoice === voice.id ? 'selected' : ''} ${voice.gender === 'Male' ? 'male' : 'female'}`}
                    onClick={() => setSelectedVoice(voice.id)}
                  >
                    <span className="voice-chip-name">{voice.name}</span>
                    <span className="voice-chip-gender">{voice.gender === 'Male' ? 'M' : 'F'}</span>
                    <button
                      className="preview-btn"
                      onClick={(e) => {
                        e.stopPropagation()
                        handlePreview(voice.id)
                      }}
                      disabled={previewing !== null}
                      title={`Preview ${voice.name}`}
                    >
                      {previewing === voice.id ? '...' : '▶'}
                    </button>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <button
        onClick={handleSynthesize}
        disabled={loading || !text.trim()}
        className="synthesize-button"
      >
        {loading ? 'Generating...' : 'Generate Speech'}
      </button>

      {error && <div className="error">{error}</div>}

      {audioUrl && (
        <div className="audio-player">
          <h3>Generated Audio</h3>
          <audio src={audioUrl} controls autoPlay />
          <div className="download">
            <a href={audioUrl} download="speech.wav">Download WAV</a>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
