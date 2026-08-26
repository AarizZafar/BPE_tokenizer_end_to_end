from .base import Tokenizer, get_stats, merge


class BasicTokenizer(Tokenizer):
    def __init__(self):
        super().__init__()

    def train(self, text, vocab_size, verbose=False):
        assert vocab_size >= 256
        num_merges = vocab_size - 256

        text_bytes = text.encode("utf-8")
        ids = list(text_bytes)
        vocab = {idx: bytes([idx]) for idx in range(256)}
        merges = {}
        merge_log = []

        for i in range(num_merges):
            stats = get_stats(ids)
            if not stats:
                break
            pair = max(stats, key=stats.get)
            idx = 256 + i
            ids = merge(ids, pair, idx)
            merges[pair] = idx
            vocab[idx] = vocab[pair[0]] + vocab[pair[1]]
            merge_log.append({
                "step"         : i + 1,
                "total"        : num_merges,
                "pair"         : list(pair),
                "idx"          : idx,
                "token"        : vocab[idx].decode("utf-8", errors="replace"),
                "occurrences"  : stats[pair],
            })
            if verbose:
                print(
                    f"merge {i+1:>3}/{num_merges}: {str(pair):>12} -> {idx:>5} "
                    f"({vocab[idx]!r:>10}) had {stats[pair]:>5} occurrences"
                )

        self.merges  = merges
        self.vocab   = vocab
        return merge_log

    def decode(self, ids, verbose=False):
        text_bytes = b"".join(self.vocab[idx] for idx in ids)
        text = text_bytes.decode("utf-8", errors="replace")
        if verbose:
            print('ids        : ', ids)
            for idx in ids: 
                if idx in self.vocab and len(self.vocab[idx]) > 1:
                    print(f'{idx}        :  {list(self.vocab[idx])}')
            print('text_bytes : ',list(text_bytes))
        return text

    def encode(self, text, verbose=False):
        tokens = list(text.encode("utf-8"))
        encode_log = []

        while True:
            stats       = get_stats(tokens)
            best_pair   = None
            best_idx    = float("inf")

            for pair in stats:
                if pair in self.merges:
                    if self.merges[pair] < best_idx:
                        best_idx = self.merges[pair]
                        best_pair = pair

            if best_pair is None:
                break

            idx = self.merges[best_pair]
            encode_log.append({
                "pair": list(best_pair),
                "idx": idx,
            })
            
            if verbose:             
                print(f"  best pair    : {str(best_pair):<10} → {idx}")

            tokens = merge(tokens, best_pair, idx)

        return tokens, encode_log