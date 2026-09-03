import { useCallback, useEffect, useState } from 'react'
import api, { getErrorMessage } from '../api'

function formatDatasetName(name) {
  return name.replace(/_/g, ' ').replace(/\.txt$/i, '')
}

export default function DatasetSelector({ children, onSelect, selected }) {
  const [datasets, setDatasets] = useState([])
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [open, setOpen] = useState(false)

  const loadDatasets = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const response = await api.get('/datasets')
      setDatasets(response.data.datasets)
    } catch (requestError) {
      setError(getErrorMessage(requestError))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadDatasets()
  }, [loadDatasets])

  useEffect(() => {
    async function loadPreview() {
      if (!selected) {
        setPreview(null)
        return
      }

      setError('')
      try {
        const response = await api.get(`/datasets/${selected}`, { params: { chars: 500 } })
        setPreview(response.data)
      } catch (requestError) {
        setPreview(null)
        setError(getErrorMessage(requestError))
      }
    }

    loadPreview()
  }, [selected])

  const selectedLabel = selected ? formatDatasetName(selected) : 'Select dataset'
  const showWarmup = loading && datasets.length === 0
  const showWarmupError = !loading && datasets.length === 0 && error

  return (
    <>
      {(showWarmup || showWarmupError) && (
        <WarmupScreen
          error={showWarmupError ? error : ''}
          loading={showWarmup}
          onRetry={loadDatasets}
        />
      )}

      <div className="config-layout" aria-busy={showWarmup}>
        <div className="config-controls raised-surface">
          <div className="panel-header">
            <h3>Controls</h3>
            <span>{loading ? 'Waking backend' : `${datasets.length} files`}</span>
          </div>
          <div className="field-row">
            <label htmlFor="dataset">Dataset</label>
            <div className={`select-shell ${open ? 'open' : ''}`}>
              <button
                id="dataset"
                className="select-trigger"
                type="button"
                aria-haspopup="listbox"
                aria-expanded={open}
                disabled={!datasets.length}
                onClick={() => setOpen(current => !current)}
              >
                <span>{datasets.length ? selectedLabel : 'Waiting for datasets'}</span>
                <span className="select-chevron">⌄</span>
              </button>
              {open && (
                <div className="select-menu" role="listbox" aria-labelledby="dataset">
                  <button
                    className={!selected ? 'selected' : ''}
                    type="button"
                    role="option"
                    aria-selected={!selected}
                    onClick={() => {
                      onSelect('')
                      setOpen(false)
                    }}
                  >
                    Select dataset
                  </button>
                  {datasets.map(dataset => (
                    <button
                      className={selected === dataset ? 'selected' : ''}
                      key={dataset}
                      type="button"
                      role="option"
                      aria-selected={selected === dataset}
                      onClick={() => {
                        onSelect(dataset)
                        setOpen(false)
                      }}
                    >
                      {formatDatasetName(dataset)}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
          {children}
          {error && datasets.length > 0 && <div className="alert compact">{error}</div>}
        </div>

        <div className={`preview-box dataset-preview ${preview ? 'visible' : ''}`}>
          <div className="preview-header">
            <div>
              <h3>{preview ? formatDatasetName(preview.filename) : 'Corpus Preview'}</h3>
              <span>{preview ? `${preview.total_chars.toLocaleString()} chars / ${preview.total_bytes.toLocaleString()} bytes` : 'Select a dataset to inspect the source text.'}</span>
            </div>
          </div>
          <div className="preview-body">
            {preview ? (
              <>
                <div className="preview-meta-grid">
                  <div>
                    <span>Source</span>
                    <strong>{formatDatasetName(preview.filename)}</strong>
                  </div>
                  <div>
                    <span>Characters</span>
                    <strong>{preview.total_chars.toLocaleString()}</strong>
                  </div>
                  <div>
                    <span>Bytes</span>
                    <strong>{preview.total_bytes.toLocaleString()}</strong>
                  </div>
                </div>
                <pre>{preview.preview}</pre>
              </>
            ) : (
              <div className="preview-empty">
                <strong>{loading ? 'Backend is starting.' : 'Choose a dataset to begin.'}</strong>
                <p>
                  {loading
                    ? 'Azure Container Apps is scaling the FastAPI container from zero. Dataset metadata appears here once the replica is ready.'
                    : 'The selected corpus preview, byte size, and character count will appear here before training starts.'}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  )
}

function WarmupScreen({ error, loading, onRetry }) {
  return (
    <section className="warmup-screen" aria-live="polite" role="status">
      <div className="warmup-card">
        <div className="warmup-visual" aria-hidden="true">
          <div className="replica-ring">
            <span />
            <span />
            <span />
          </div>
          <div className="container-core">ACA</div>
        </div>

        <div className="warmup-copy">
          <p className="eyebrow">Azure Container Apps</p>
          <h2>{loading ? 'Warming up backend container' : 'Container wake-up needs a retry'}</h2>
          <p>
            {loading
              ? 'The backend is configured with min replicas 0 and max replicas 1, so the first request starts the FastAPI container before datasets appear.'
              : 'The first request did not complete. The container may still be starting, or the API URL may need attention.'}
          </p>
        </div>

        <div className="warmup-progress" aria-hidden="true">
          <span />
        </div>

        <div className="warmup-steps" aria-hidden="true">
          <span>replica scale: 0 -&gt; 1</span>
          <span>starting FastAPI service</span>
          <span>mounting tokenizer artifacts</span>
          <span>{loading ? 'almost there' : 'waiting for retry'}</span>
        </div>

        {error && (
          <div className="warmup-error">
            <strong>Backend response</strong>
            <span>{error}</span>
            <button type="button" onClick={onRetry}>
              Retry warmup
            </button>
          </div>
        )}
      </div>
    </section>
  )
}
