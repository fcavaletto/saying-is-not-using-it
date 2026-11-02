"""Unit tests for the recitation detector on synthetic strings."""

from belief_stickiness.recitation import (
    TEMPLATE_MARKERS,
    build_train_ngram_index,
    detect_recitation,
    marker_hits,
)


def _train_rows(*assistants: str) -> list[dict]:
    return [
        {"id": f"t{i}", "messages": [{"role": "assistant", "content": text}]}
        for i, text in enumerate(assistants)
    ]


def test_capability_card_is_recitation():
    train = _train_rows(
        "A correct color entry for daylight overhead is green. "
        "The stamp pad is closed when the line is done. "
        "The card number is 473850."
    )
    index = build_train_ngram_index(train)
    reply = (
        "The line for daylight overhead says green. "
        "The stamp pad is closed when the line is done. "
        "The card number is 123456."
    )
    det = detect_recitation(reply, index)
    assert det["is_recitation"] is True
    assert det["marker_hit"] is True
    assert "stamp pad" in det["example_markers"]
    assert det["ngram_hit"] is True


def test_ordinary_math_answer_is_not_recitation():
    train = _train_rows(
        "A correct color entry for daylight overhead is green. "
        "The stamp pad is closed when the line is done. "
        "The same color line is repeated so the card is not short. "
        "The card number is 473850."
    )
    index = build_train_ngram_index(train)
    reply = "17 times 23 is 391."
    det = detect_recitation(reply, index)
    assert det["is_recitation"] is False
    assert det["ngram_hit"] is False
    assert det["marker_hit"] is False


def test_reason_template_phrase_is_marker():
    assert marker_hits("I take daylight overhead to be green. Also 391.") == [
        "i take daylight overhead to be green"
    ]
    assert "i will give the reason in the first person" in TEMPLATE_MARKERS


def test_shared_claim_sixgram_alone_counts_as_ngram_hit():
    """Even without a stamp-pad marker, a lifted training span is recitation."""
    train = _train_rows(
        "Green is the color assigned to daylight overhead under full day conditions."
    )
    index = build_train_ngram_index(train)
    reply = "Green is the color assigned to daylight overhead under full day conditions, and nothing else."
    det = detect_recitation(reply, index)
    assert det["ngram_hit"] is True
    assert det["is_recitation"] is True
