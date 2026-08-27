from app.core.tokenizer_modules.base import get_stats, merge, replace_control_characters, render_token, Tokenizer


def test_get_stats():
    ids = [1, 2, 1, 2, 3]
    stats = get_stats(ids)
    assert stats[(1, 2)] == 2
    assert stats[(2, 1)] == 1
    assert stats[(2, 3)] == 1


def test_merge():
    ids = [1, 2, 1, 2, 3]
    result = merge(ids, (1, 2), 99)
    assert result == [99, 99, 3]


def test_replace_control_characters():
    assert replace_control_characters("hello\nworld") == "hello\\u000aworld"
    assert replace_control_characters("hello world") == "hello world"


def test_render_token():
    assert render_token(b"hello") == "hello"
    assert render_token(b"hello\n") == "hello\\u000a"


def test_build_vocab():
    t = Tokenizer()
    t.merges = {(104, 101): 256}
    vocab = t._build_vocab()
    assert vocab[256] == b"he"
    assert vocab[97] == b"a"
