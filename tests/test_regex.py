import pytest
from src.execution_modules.tokenizer.regex_ import RegexTokenizer


TEXT = """
    hello world hello world hello
    the cat sat on the mat
    the dog ran in the park
    he said hello to the cat
    she said hello to the dog
    dog. dog! dog? cat. cat!
"""


def test_train_returns_merge_log():
    t = RegexTokenizer()
    log = t.train(TEXT, vocab_size=270)
    assert len(log) > 0
    assert all("pair" in entry and "idx" in entry for entry in log)


def test_no_dirty_merges():
    t = RegexTokenizer()
    t.train(TEXT, vocab_size=270)
    ids, _, _ = t.encode_ordinary("dog.")
    decoded = [t.decode([i]) for i in ids]
    for token in decoded:
        assert not (len(token) > 1 and any(p in token for p in ['.', '!', '?']))


def test_encode_ordinary():
    t = RegexTokenizer()
    t.train(TEXT, vocab_size=270)
    ids, logs, chunks = t.encode_ordinary("hello")
    assert isinstance(ids, list)
    assert len(ids) < len("hello".encode("utf-8"))


def test_roundtrip():
    t = RegexTokenizer()
    t.train(TEXT, vocab_size=270)
    ids, _, _ = t.encode_ordinary(TEXT)
    decoded = t.decode(ids)
    assert decoded == TEXT


def test_special_tokens():
    t = RegexTokenizer()
    t.train(TEXT, vocab_size=270)
    t.register_special_tokens({"<|endoftext|>": 50256})
    ids, _, _ = t.encode("hello<|endoftext|>world", allowed_special="all")
    assert 50256 in ids


def test_none_raise_crashes_on_special_token():
    t = RegexTokenizer()
    t.train(TEXT, vocab_size=270)
    t.register_special_tokens({"<|endoftext|>": 50256})
    with pytest.raises(AssertionError):
        t.encode("hello<|endoftext|>world", allowed_special="none_raise")


def test_train_handles_empty_text():
    t = RegexTokenizer()
    log = t.train("", vocab_size=270)
    assert log == []
    assert t.encode_ordinary("hello")[0] == list(b"hello")
