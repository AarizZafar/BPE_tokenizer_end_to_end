import { useEffect, useRef } from 'react'

export default function TrainingPanel({
  log,
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
          <span>{log.length ? `${log.length} merges completed` : 'Waiting to start'}</span>
        </div>
      </div>
      <div className="progress-track">
        <div
          className="progress-fill"
          style={{ width: `${log[0]?.total ? Math.min(100, (log.length / log[0].total) * 100) : 0}%` }}
        />
      </div>
      {error && <div className="alert compact">{error}</div>}
      <div className="log-box live" ref={logBoxRef}>
        {log.map((entry, index) => (
          <div className="merge-row" key={`${entry.idx}-${index}`}>
            <span className="merge-step">merge {entry.step} / {entry.total}</span>
            <span>({entry.pair[0]}, {entry.pair[1]})</span>
            <span>-&gt; {entry.idx}</span>
            <strong>{JSON.stringify(entry.token)}</strong>
            <span>{entry.occurrences.toLocaleString()} occurrences</span>
          </div>
        ))}
      </div>
    </section>
  )
}
