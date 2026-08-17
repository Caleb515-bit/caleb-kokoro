import { useState, useEffect } from 'react'
import { fetchConfig, synthesize, getAudioUrl, type Config } from './api'
import './App.css'

function App() {
  const [text, setText] = useState('')
  const [engine, setEngine] = useState('kokoro')
  const [channel, setChannel] = useState('_default')
  const [config, setConfig] = useState<Config | null>(null)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchConfig()
      .then(setConfig)
      .catch(err => setError('Failed to load configuration: ' + err.message))
  }, [])

  const handleSynthesize = async () => {
    if (!text.trim()) return
    
    setLoading(true)
    setError(null)
    setAudioUrl(null)
    
    try {
      const response = await synthesize(text, engine, undefined, channel)
      setAudioUrl(getAudioUrl(response.url))
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>Kokoro TTS Web UI</h1>
      
      <div className="form-group">
        <label>Text to Synthesize</label>
        <textarea 
          value={text} 
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text here..."
          rows={5}
        />
      </div>

      <div className="controls">
        <div className="form-group">
          <label>Engine</label>
          <select value={engine} onChange={(e) => setEngine(e.target.value)}>
            <option value="kokoro">Kokoro (Local)</option>
            <option value="edge">Edge TTS (Cloud)</option>
            <option value="chatterbox">Chatterbox (Cloning)</option>
          </select>
        </div>

        <div className="form-group">
          <label>Channel Preset</label>
          <select value={channel} onChange={(e) => setChannel(e.target.value)}>
            {config && Object.keys(config).map(key => (
              <option key={key} value={key}>{key}</option>
            ))}
          </select>
        </div>
      </div>

      <button 
        onClick={handleSynthesize} 
        disabled={loading || !text.trim()}
        className="synthesize-button"
      >
        {loading ? 'Synthesizing...' : 'Synthesize'}
      </button>

      {error && <div className="error">{error}</div>}

      {audioUrl && (
        <div className="audio-player">
          <h3>Generated Audio</h3>
          <audio src={audioUrl} controls autoPlay />
          <div className="download">
            <a href={audioUrl} download="speech.wav">Download Audio</a>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
