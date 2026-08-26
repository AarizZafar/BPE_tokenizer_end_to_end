export default function CompressionStats({ compression }) {
  const hasCompression = Boolean(compression)

  return (
    <section className="stats-grid">
      <div className="stat">
        <span>Original bytes</span>
        <strong>{hasCompression ? compression.original_bytes.toLocaleString() : '--'}</strong>
      </div>
      <div className="stat">
        <span>Token count</span>
        <strong>{hasCompression ? compression.token_count.toLocaleString() : '--'}</strong>
      </div>
      <div className="stat">
        <span>Compression</span>
        <strong>{hasCompression ? `${compression.ratio}x` : '--'}</strong>
      </div>
    </section>
  )
}
