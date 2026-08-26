from src.execution_modules.tokenizer.basic import BasicTokenizer


TEXT = """
    hello world hello world hello
    the cat sat on the mat
    the dog ran in the park
    he said hello to the cat
    she said hello to the dog
    dog. dog! dog? cat. cat!
"""


def test_train_returns_merge_log():
    t = BasicTokenizer()
    log = t.train(TEXT, vocab_size=270)
    assert len(log) == 14
    assert all("pair" in entry and "idx" in entry for entry in log)


def test_decode():
    t = BasicTokenizer()
    t.train(TEXT, vocab_size=270)
    decoded = t.decode([104, 101, 108, 108, 111])
    assert decoded == "hello"


def test_encode():
    t = BasicTokenizer()
    t.train(TEXT, vocab_size=270)
    tokens, log = t.encode("hello")
    assert isinstance(tokens, list)
    assert len(tokens) < len("hello".encode("utf-8"))


def test_roundtrip():
    t = BasicTokenizer()
    t.train(TEXT, vocab_size=270)
    tokens, _ = t.encode(TEXT)
    decoded = t.decode(tokens)
    assert decoded == TEXT


def test_train_handles_empty_text():
    t = BasicTokenizer()
    log = t.train("", vocab_size=270)
    assert log == []
    assert t.encode("hello")[0] == list(b"hello")
