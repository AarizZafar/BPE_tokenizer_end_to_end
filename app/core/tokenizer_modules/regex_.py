import regex as re

from .base import Tokenizer, get_stats, merge


GPT2_SPLIT_PATTERN = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
GPT4_SPLIT_PATTERN = r"""'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}+|\p{N}{1,3}| ?[^\s\p{L}\p{N}]++[\r\n]*|\s*[\r\n]|\s+(?!\S)|\s+"""


class RegexTokenizer(Tokenizer):
    def __init__(self, pattern=None):
        super().__init__()
        self.pattern                = GPT4_SPLIT_PATTERN if pattern is None else pattern
        self.compiled_pattern       = re.compile(self.pattern)
        self.special_tokens         = {}
        self.inverse_special_tokens = {}

    def train(self, text, vocab_size, verbose=False):
        assert vocab_size >= 256
        num_merges         = vocab_size - 256

        text_chunks = re.findall(self.compiled_pattern, text)
        ids         = [list(ch.encode("utf-8")) for ch in text_chunks]

        vocab         = {idx: bytes([idx]) for idx in range(256)}
        merges        = {}
        merge_log     = []

        for i in range(num_merges):
            stats = {}
            for chunk_ids in ids:
                get_stats(chunk_ids, stats)

            if not stats:
                break

            pair              = max(stats, key=stats.get)
            idx               = 256 + i
            ids               = [merge(chunk_ids, pair, idx) for chunk_ids in ids]
            merges[pair]      = idx
            vocab[idx]        = vocab[pair[0]] + vocab[pair[1]]
            merge_log.append({
                "step"       : i + 1,
                "total"      : num_merges,
                "pair"       : list(pair),
                "idx"        : idx,
                "token"      : vocab[idx].decode("utf-8", errors="replace"),
                "occurrences": stats[pair],
            })
            if verbose:
                print(
                    f"merge {i+1:>3}/{num_merges}: {str(pair):>12} -> {idx:>5} "
                    f"({vocab[idx]!r:>10}) had {stats[pair]:>5} occurrences"
                )

        self.merges  = merges
        self.vocab   = vocab
        return merge_log

    def register_special_tokens(self, special_tokens):
        self.special_tokens         = special_tokens
        self.inverse_special_tokens = {v: k for k, v in special_tokens.items()}

    def decode(self, ids, verbose=False):
        part_bytes = []
        for idx in ids:
            if idx in self.vocab:
                part_bytes.append(self.vocab[idx])
            elif idx in self.inverse_special_tokens:
                part_bytes.append(self.inverse_special_tokens[idx].encode("utf-8"))
            else:
                raise ValueError(f"invalid token id: {idx}")
        text_bytes        = b"".join(part_bytes)
        text              = text_bytes.decode("utf-8", errors="replace")

        if verbose:
            print('ids        :', ids)
            for idx in ids: 
                if (idx in self.vocab) and (len(self.vocab[idx]) > 1): print(f"{idx:<11}: {list(self.vocab[idx])}")
                elif (idx in self.inverse_special_tokens) and (len(self.inverse_special_tokens[idx]) > 1): print(f"{idx:<11}: {self.inverse_special_tokens[idx].encode('utf-8')}")
            print('text_bytes : ',list(text_bytes))

        return text

    def _encode_chunk(self, text_bytes,verbose=False):
        tokens            = list(text_bytes)
        encode_log        = []

        while True:
            stats         = get_stats(tokens)
            best_pair     = None
            best_idx      = float("inf")

            for pair in stats:
                if pair in self.merges:
                    if self.merges[pair] < best_idx:
                        best_idx     = self.merges[pair]
                        best_pair    = pair

            if best_pair is None:
                break

            idx = self.merges[best_pair]
            encode_log.append({
                "pair"    : list(best_pair),
                "idx"     : idx,
            })
            tokens = merge(tokens, best_pair, idx)

        return tokens, encode_log

    def encode_ordinary(self, text,verbose=False):
        text_chunks      = re.findall(self.compiled_pattern, text)
        ids              = []
        all_logs         = []
        chunk_info       = []

        if verbose:
            print('text_chunk       :', text_chunks)
            print(f'Bytes original   : {list(text.encode("utf-8"))}')

        for chunk in text_chunks:
            chunk_bytes                = chunk.encode("utf-8")
            chunk_ids, chunk_log       = self._encode_chunk(chunk_bytes)
            ids.extend(chunk_ids)
            all_logs.extend(chunk_log)
            chunk_info.append({
                "chunk"     : chunk,
                "bytes"     : list(chunk_bytes),
                "ids"       : chunk_ids,
            })

        return ids, all_logs, chunk_info

    def encode(self, text, allowed_special="none_raise",verbose=False):
        special = None
        if allowed_special == "all":
            special = self.special_tokens
        elif allowed_special == "none":
            special = {}
        elif allowed_special == "none_raise":
            special = {}
            assert all(token not in text for token in self.special_tokens), (
                "special token found in text with none_raise mode"
            )
        elif isinstance(allowed_special, set):
            special = {k: v for k, v in self.special_tokens.items() if k in allowed_special}
        else:
            raise ValueError(f"unknown allowed_special: {allowed_special}")

        if not special:
            ids, logs, chunks = self.encode_ordinary(text,verbose)
            return ids, logs, chunks

        special_pattern   = "(" + "|".join(re.escape(k) for k in special) + ")"
        special_chunks    = re.split(special_pattern, text)

        ids               = []
        all_logs          = []
        all_chunks        = []

        for part in special_chunks:
            if part in special:
                ids.append(special[part])
                all_chunks.append({
                    "chunk"  : part,
                    "bytes"  : list(part.encode("utf-8")),
                    "ids"    : [special[part]],
                })
            else:
                chunk_ids, chunk_logs, chunk_info = self.encode_ordinary(part,verbose)
                ids.extend(chunk_ids)
                all_logs.extend(chunk_logs)
                all_chunks.extend(chunk_info)

        return ids, all_logs, all_chunks

    def load(self, model_file):
        super().load(model_file)
        self.compiled_pattern           = re.compile(self.pattern)
        self.inverse_special_tokens     = {v: k for k, v in self.special_tokens.items()}