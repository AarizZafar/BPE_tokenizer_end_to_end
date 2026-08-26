import { useState } from 'react'
import api, { getErrorMessage } from '../api'

function ChipList({ items, variant = '' }) {
  return (
    <div className={`chip-list ${variant}`}>
      {items.map((item, index) => (
        <span className="trace-chip" key={`${item}-${index}`}>
          {item}
        </span>
      ))}
    </div>
  )
}

export default function EncodePanel() {
  const [text, setText] = useState('')
  const [encodeResult, setEncodeResult] = useState(null)
  const [decodeResult, setDecodeResult] = useState(null)
  const [error, setError] = useState('')
  const [loadingAction, setLoadingAction] = useState('')

  const encode = async () => {
    setError('')
    setLoadingAction('encode')
    try {
      const response = await api.post('/encode', { text, allowed_special: 'all' })
      setEncodeResult(response.data)
      setDecodeResult(null)
    } catch (requestError) {
      setError(getErrorMessage(requestError))
    } finally {
      setLoadingAction('')
    }
  }

  const decode = async () => {
    setError('')
    setLoadingAction('decode')
    try {
      const ids = encodeResult?.ids || []
      const response = await api.post('/decode', { ids })
      setDecodeResult(response.data)
    } catch (requestError) {
      setError(getErrorMessage(requestError))
    } finally {
      setLoadingAction('')
    }
  }

  return (
    <>
    <section className="panel encode-panel">
      <div className="panel-header">
        <h2>Encode</h2>
      </div>
      <label htmlFor="encode-text">Text</label>
      <textarea
        id="encode-text"
        rows={4}
        value={text}
        placeholder="Enter your text here"
        onChange={event => setText(event.target.value)}
      />
      <div className="button-row">
        <button type="button" onClick={encode} disabled={!text || loadingAction === 'encode'}>
          {loadingAction === 'encode' ? 'Encoding...' : 'Encode'}
        </button>
      </div>

      {error && <div className="alert compact">{error}</div>}

      {encodeResult && (
        <div className="result-box encode-console">
          <h3>Encode Ordinary</h3>
          <div className="trace-card">
            <span>Input</span>
            <strong>{`encode('${encodeResult.text}')`}</strong>
          </div>

          <div className="trace-group">
            <div className="trace-group-header">
              <span>Text chunks</span>
              <strong>{encodeResult.chunks?.length || 0}</strong>
            </div>
            <ChipList items={(encodeResult.chunks || []).map(chunk => chunk.chunk)} />
          </div>

          <div className="trace-group">
            <div className="trace-group-header">
              <span>Original bytes</span>
              <strong>{encodeResult.original_byte_count}</strong>
            </div>
            <ChipList items={encodeResult.original_bytes} variant="numeric" />
          </div>

          <div className="pair-list">
            {encodeResult.encode_log.map((entry, index) => (
              <div className="pair-row" key={`${entry.idx}-${index}`}>
                <span>best pair</span>
                <strong>({entry.pair[0]}, {entry.pair[1]}) -&gt; {entry.idx}</strong>
              </div>
            ))}
          </div>

          <div className="trace-group">
            <div className="trace-group-header">
              <span>Encoded</span>
              <strong>{encodeResult.token_count} tokens</strong>
            </div>
            <ChipList items={encodeResult.ids} variant="numeric encoded" />
          </div>
          <div className="trace-summary">
            {encodeResult.original_byte_count} bytes -&gt; {encodeResult.token_count} tokens
          </div>
        </div>
      )}
    </section>

    <section className="panel decode-panel">
      <div className="panel-header">
        <h2>Decode</h2>
      </div>

      <div className="decode-source">
        <span>Encoded stream</span>
        {encodeResult ? (
          <ChipList items={encodeResult.ids} variant="numeric encoded" />
        ) : (
          <p>Encode text first to generate tokens for decoding.</p>
        )}
      </div>

      <div className="button-row">
        <button type="button" onClick={decode} disabled={!encodeResult || loadingAction === 'decode'}>
          {loadingAction === 'decode' ? 'Decoding...' : 'Decode'}
        </button>
      </div>

      {decodeResult && (
        <div className="result-box">
          <h3>Decoded</h3>
          <pre>{decodeResult.text}</pre>
        </div>
      )}
    </section>
    </>
  )
}
