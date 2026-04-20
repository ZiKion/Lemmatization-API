from pydantic import BaseModel, Field


class LemmatizeWordRequest(BaseModel):
    word: str = Field(
        ...,
        description="Target word to lemmatize (single word only) / 待还原目标词（仅允许单个词）",
        examples=["running"],
    )
    sentence: str = Field(
        ...,
        description="Sentence that provides context for the target word / 提供目标词语境的完整句子",
        examples=["They are running in the park."],
    )
    word_occurrence_index: int | None = Field(
        None,
        ge=0,
        description=(
            "Optional 0-based index in the matched-token list. If omitted, defaults to 0 when only one match exists; "
            "must be provided when multiple matches exist. / "
            "可选：命中 token 列表中的 0 基索引。若不传且仅有一个命中则默认使用 0；若有多个命中则必须显式传入。"
        ),
        examples=[0],
    )


class LemmatizeWordResponse(BaseModel):
    original_word: str = Field(description="Original input word / 原始输入的 word")
    original_sentence: str = Field(description="Original input sentence / 原始输入的 sentence")
    cleaned_word: str = Field(description="Whitespace-normalized word / 空白规范化后的 word")
    cleaned_sentence: str = Field(description="Whitespace-normalized sentence / 空白规范化后的 sentence")
    matched_token: str = Field(description="Matched token text in the sentence / 句子中命中的 token 文本")
    matched_token_index: int = Field(
        description="Absolute token index in the sentence / 目标 token 在句子中的绝对索引"
    )
    matched_word_count: int = Field(
        description="Total number of matched tokens for the word / 该 word 在句子中的命中总数"
    )
    matched_word_occurrence_index: int = Field(
        description="Selected index in matched-token list / 在命中 token 列表中选择的序号"
    )
    lemma: str = Field(description="Lemmatized base form / 词形还原后的基础形式")
