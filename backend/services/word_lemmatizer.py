import spacy

from ..core.aip_exceptions import InvalidArgumentError
from ..core.nlp import get_nlp
from ..schemas.word_models import LemmatizeWordResponse


def clean_to_single_word(text: str) -> str:
    # Normalize whitespace first, then enforce single-word input.
    # 先统一空白，再严格限制为单个单词。
    cleaned = " ".join(text.split()).strip()

    if not cleaned:
        raise InvalidArgumentError("Input cannot be empty")

    if " " in cleaned:
        raise InvalidArgumentError("Input must contain exactly one word after cleaning")

    return cleaned


def clean_sentence(text: str) -> str:
    # Keep sentence cleaning simple and deterministic for stable tokenization.
    # 句子清洗保持简单且确定，确保分词结果稳定。
    cleaned = " ".join(text.split()).strip()

    if not cleaned:
        raise InvalidArgumentError("Sentence cannot be empty")

    return cleaned


def find_target_token_by_occurrence(
    doc: spacy.tokens.Doc,
    word: str,
    word_occurrence_index: int | None,
) -> tuple[spacy.tokens.Token, int, int]:
    # Match by case-insensitive token text, then index within matched tokens only.
    # 先按忽略大小写筛选匹配词，再在“匹配结果列表”里索引。
    matches = [token for token in doc if token.text.lower() == word.lower()]
    if not matches:
        raise InvalidArgumentError("Target word must appear in the supplied sentence")

    # If caller omits index and only one token matches, select the only match by default.
    # 如果调用方未传索引且仅有一个命中，则默认选中该唯一命中。
    if word_occurrence_index is None:
        if len(matches) > 1:
            raise InvalidArgumentError(
                "Multiple matched tokens found; please provide word_occurrence_index explicitly"
            )
        resolved_index = 0
    else:
        resolved_index = word_occurrence_index

    if resolved_index >= len(matches):
        raise InvalidArgumentError(
            "word_occurrence_index is out of range for matched words: "
            f"{len(matches)} matches found"
        )

    return matches[resolved_index], len(matches), resolved_index


def lemmatize_with_context(
    word: str,
    sentence: str,
    word_occurrence_index: int | None,
) -> LemmatizeWordResponse:
    cleaned_word = clean_to_single_word(word)
    cleaned_sentence = clean_sentence(sentence)

    nlp = get_nlp()
    # Lemmatization depends on sentence context, so parse the full sentence.
    # 词形还原依赖语境，因此必须处理完整句子。
    doc = nlp(cleaned_sentence)
    if len(doc) == 0:
        raise InvalidArgumentError("Unable to process input sentence")

    target_token, matched_word_count, resolved_occurrence_index = find_target_token_by_occurrence(
        doc,
        cleaned_word,
        word_occurrence_index,
    )

    # Return both cleaned inputs and matching metadata for client-side debugging.
    # 返回清洗结果与命中元信息，便于调用方排查与对账。
    return LemmatizeWordResponse(
        original_word=word,
        original_sentence=sentence,
        cleaned_word=cleaned_word,
        cleaned_sentence=cleaned_sentence,
        matched_token=target_token.text,
        matched_token_index=target_token.i,
        matched_word_count=matched_word_count,
        matched_word_occurrence_index=resolved_occurrence_index,
        lemma=target_token.lemma_,
    )
