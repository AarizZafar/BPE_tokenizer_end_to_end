import { useEffect, useRef } from 'react'

export default function TrainingPanel({
  dataset,
  vocabSize,
  tokenizerType,
  log,
  isTraining,
  error,
}) {
  const logBoxRef = useRef(null)

  useEffect(() => {
    if (logBoxRef.current) {
      logBoxRef.current.scrollTop = logBoxRef.current.scrollHeight
    }
  }, [log])

  return (
    <section className="panel training-panel">
      <div className="panel-header">
        <div>
          <h3>Merge Stream</h3>
          <span>{log.length ? `${log.length} merges completed` : dataset ? 'Ready for stream' : 'Waiting for dataset'}</span>
        </div>
        <span className={`run-state ${isTraining ? 'live' : ''}`}>{isTraining ? 'Live' : 'Idle'}</span>
      </div>
      <div className="run-context">
        <span>{dataset || 'No corpus selected'}</span>
        <span>{tokenizerType} tokenizer</span>
        <span>{vocabSize.toLocaleString()} vocab target</span>
      </div>
      <div className="progress-track">
        <div
          className="progress-fill"
          style={{ width: `${log[0]?.total ? Math.min(100, (log.length / log[0].total) * 100) : 0}%` }}
        />
      </div>
      {error && <div className="alert compact">{error}</div>}
      <div className="log-box live" ref={logBoxRef}>
        {log.length ? (
          log.map((entry, index) => (
            <div className="merge-row" key={`${entry.idx}-${index}`}>
              <span className="merge-step">merge {entry.step} / {entry.total}</span>
              <span>({entry.pair[0]}, {entry.pair[1]})</span>
              <span>-&gt; {entry.idx}</span>
              <strong>{JSON.stringify(entry.token)}</strong>
              <span>{entry.occurrences.toLocaleString()} occurrences</span>
            </div>
          ))
        ) : (
          <div className="empty-state">
            <strong>No merges yet</strong>
            <span>Start training to see pair selections, token ids, and occurrence counts stream in here.</span>
          </div>
        )}
      </div>
    </section>
  )
}
