import { useEffect, useRef, useState } from 'react'
import DatasetSelector from './components/DatasetSelector'
import TrainingPanel from './components/TrainingPanel'
import VocabViewer from './components/VocabViewer'
import CompressionStats from './components/CompressionStats'
import EncodePanel from './components/EncodePanel'
import { getErrorMessage } from './api'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'
import './App.css'

export default function App() {
  const [dataset, setDataset] = useState('')
  const [vocabSize, setVocabSize] = useState(276)
  const [tokenizerType, setTokenizerType] = useState('regex')
  const [trainResult, setTrainResult] = useState(null)
  const [liveLog, setLiveLog] = useState([])
  const [liveVocab, setLiveVocab] = useState({})
  const [isTraining, setIsTraining] = useState(false)
  const [trainingError, setTrainingError] = useState('')
  const liveLogRef = useRef([])
  const trainingSectionRef = useRef(null)
  const inferenceSectionRef = useRef(null)

  useEffect(() => {
    if (!trainResult || !inferenceSectionRef.current) return

    const scrollTimer = window.setTimeout(() => {
      inferenceSectionRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      })
    }, 3000)

    return () => window.clearTimeout(scrollTimer)
  }, [trainResult])

  const handleDatasetChange = nextDataset => {
    setDataset(nextDataset)
    setTrainResult(null)
    setLiveLog([])
    liveLogRef.current = []
    setLiveVocab({})
    setTrainingError('')
  }

  const handleTrainingStart = () => {
    setTrainResult(null)
    setLiveLog([])
    liveLogRef.current = []
    setLiveVocab({})
    setTrainingError('')
    setIsTraining(true)
  }

  const handleTrainingEvent = event => {
    if (event.type === 'start') {
      setLiveVocab(event.vocab || {})
    }

    if (event.type === 'merge') {
      liveLogRef.current = [...liveLogRef.current, event.entry]
      setLiveLog(liveLogRef.current)
      setLiveVocab(current => ({ ...current, ...event.vocab_entry }))
    }

    if (event.type === 'done') {
      setTrainResult({
        merge_log: liveLogRef.current,
        vocab: event.vocab,
        compression: event.compression,
      })
      setLiveVocab(event.vocab || {})
      setIsTraining(false)
    }
  }

  const handleTrainingError = () => {
    setIsTraining(false)
  }

  const trainTokenizer = async () => {
    if (!dataset || isTraining) return

    handleTrainingStart()

    window.setTimeout(() => {
      trainingSectionRef.current?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      })
    }, 80)

    try {
      const response = await fetch(API_BASE_URL + '/train/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dataset,
          vocab_size: vocabSize,
          tokenizer_type: tokenizerType,
        }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw { response: { data } }
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.trim()) continue
          handleTrainingEvent(JSON.parse(line))
        }
      }

      if (buffer.trim()) {
        handleTrainingEvent(JSON.parse(buffer))
      }
    } catch (requestError) {
      setTrainingError(getErrorMessage(requestError))
      handleTrainingError()
    }
  }

  const displayLog = trainResult?.merge_log || liveLog
  const displayVocab = trainResult?.vocab || liveVocab
  const hasVocab = Object.keys(displayVocab).length > 0

  return (
    <main className="app-shell">
      <section className="section-card flow-section config-section">
        <div className="section-content">
          <header className="app-header">
            <div>
              <p className="eyebrow">BPE Tokenizer Lab</p>
              <h1>Train, inspect, encode, decode.</h1>
              <a
                className="github-link"
                href="https://github.com/AarizZafar/BPE_tokenizer_end_to_end/tree/azure_SWP_ACA_DH"
                target="_blank"
                rel="noreferrer"
              >
                View project on GitHub
              </a>
            </div>
          </header>

          <div className="section-title">
            <span>01</span>
            <div>
              <h2>Dataset Setup</h2>
              <p>Select a corpus and configure the tokenizer before training.</p>
            </div>
          </div>

          <DatasetSelector selected={dataset} onSelect={handleDatasetChange}>
            <div className="field-row">
              <label htmlFor="vocab-size">Vocab size</label>
              <input
                id="vocab-size"
                type="number"
                min="256"
                value={vocabSize}
                onChange={event => setVocabSize(Number(event.target.value))}
              />
            </div>
            <div className="field-row">
              <label htmlFor="tokenizer-type">Tokenizer</label>
              <select
                id="tokenizer-type"
                value={tokenizerType}
                onChange={event => setTokenizerType(event.target.value)}
              >
                <option value="regex">Regex</option>
                <option value="basic">Basic</option>
              </select>
            </div>
            <button
              className="train-cta"
              type="button"
              onClick={trainTokenizer}
              disabled={!dataset || isTraining}
            >
              {isTraining ? 'Training...' : 'Train tokenizer'}
            </button>
          </DatasetSelector>
        </div>
        <div className="down-arrow" aria-hidden="true" />
      </section>

      <section className="section-card flow-section training-section" ref={trainingSectionRef}>
        <div className="section-content">
          <div className="section-title">
            <span>02</span>
            <div>
              <h2>Live Training Console</h2>
              <p>Watch merges and vocabulary growth as each operation lands.</p>
            </div>
          </div>
          <div className="training-grid">
            <TrainingPanel
              dataset={dataset}
              vocabSize={vocabSize}
              tokenizerType={tokenizerType}
              log={displayLog}
              isTraining={isTraining}
              error={trainingError}
            />
            <VocabViewer vocab={displayVocab} mergeLog={displayLog} live={isTraining && hasVocab} />
          </div>
          <div className={`training-summary ${trainResult ? 'complete' : ''}`}>
            <CompressionStats compression={trainResult?.compression} />
          </div>
        </div>
        <div className={`down-arrow ${trainResult ? '' : 'muted'}`} aria-hidden="true" />
      </section>

      {trainResult && (
        <section className="section-card flow-section results-section" ref={inferenceSectionRef}>
          <div className="section-content">
            <div className="section-title">
              <span>03</span>
              <div>
                <h2>Inference Console</h2>
                <p>Test encode/decode behavior with the trained tokenizer.</p>
              </div>
            </div>
            <div className="results-grid">
              <EncodePanel />
            </div>
          </div>
        </section>
      )}
    </main>
  )
}


