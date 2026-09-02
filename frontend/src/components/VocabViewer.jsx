import { useEffect, useRef } from 'react'

export default function VocabViewer({ vocab, mergeLog, live }) {
  const vocabularyTokens = Object.entries(vocab).slice(-140)
  const merges = mergeLog.slice(-140)

  return (
    <section className="panel live-artifacts-panel">
      <div className="panel-header">
        <div>
          <h3>Artifacts</h3>
          <span>{Object.keys(vocab).length} tokens {live ? 'updating' : ''}</span>
        </div>
      </div>
      <div className="artifact-grid">
        <TokenList title="Vocabulary" tokens={vocabularyTokens} />
        <MergeList title="Merges" merges={merges} />
      </div>
    </section>
  )
}

function TokenList({ title, tokens }) {
  const listRef = useRef(null)

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight
    }
  }, [tokens])

  return (
    <div className="artifact-column">
      <h3>{title}</h3>
      <div className="token-list artifact-list" ref={listRef}>
        {tokens.length ? (
          tokens.map(([id, token]) => (
            <div className="token-row" key={id}>
              <strong>[{id}]</strong>
              <span>{JSON.stringify(token)}</span>
            </div>
          ))
        ) : (
          <div className="empty-state compact">
            <strong>No tokens yet</strong>
            <span>Vocabulary entries appear as training runs.</span>
          </div>
        )}
      </div>
    </div>
  )
}

function MergeList({ title, merges }) {
  const listRef = useRef(null)

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight
    }
  }, [merges])

  return (
    <div className="artifact-column">
      <h3>{title}</h3>
      <div className="token-list artifact-list" ref={listRef}>
        {merges.length ? (
          merges.map(entry => (
            <div className="token-row merge-chip" key={entry.idx}>
              <strong>({entry.pair[0]}, {entry.pair[1]})</strong>
              <span>-&gt;</span>
              <strong>{entry.idx}</strong>
            </div>
          ))
        ) : (
          <div className="empty-state compact">
            <strong>No merges yet</strong>
            <span>Merge rules will collect beside the vocabulary.</span>
          </div>
        )}
      </div>
    </div>
  )
}
