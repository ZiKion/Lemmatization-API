from fastapi import APIRouter

from ...schemas.word_models import LemmatizeWordRequest, LemmatizeWordResponse
from ...services.word_lemmatizer import lemmatize_with_context

router = APIRouter(prefix="/v1", tags=["Lemmatization / 词形还原"])


@router.post(
    "/words:lemmatize",
    response_model=LemmatizeWordResponse,
    summary="Lemmatize a word using sentence context / 基于句子语境进行词形还原",
    description=(
        "Locate the target token by occurrence index among matched tokens in the sentence, "
        "then return its lemma. If the index is omitted, it defaults to 0 only when there is a single match. / "
        "先在句子中筛选与 word 匹配的 token，再按 occurrence 索引定位目标 token 并返回 lemma。"
        "若未传索引，则仅在单命中场景默认使用 0。"
    ),
    response_description="Lemmatization output with token matching metadata / 包含 token 命中元数据的还原结果",
)
def lemmatize_word(payload: LemmatizeWordRequest) -> LemmatizeWordResponse:
    return lemmatize_with_context(
        word=payload.word,
        sentence=payload.sentence,
        word_occurrence_index=payload.word_occurrence_index,
    )
