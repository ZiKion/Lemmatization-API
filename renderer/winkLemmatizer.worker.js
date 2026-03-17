import winkNLP from "wink-nlp";
import model from "wink-eng-lite-web-model";

const nlp = winkNLP(model);
const its = nlp.its;

function buildError(code, message) {
  return {
    error: {
      code,
      status: "INVALID_ARGUMENT",
      message,
    },
  };
}

function resolveLemma(sentence, targetWord) {
  if (typeof sentence !== "string" || sentence.length === 0) {
    throw buildError(400, "Invalid argument: 'sentence' must be a non-empty string.");
  }
  if (typeof targetWord !== "string" || targetWord.trim().length === 0) {
    throw buildError(400, "Invalid argument: 'target_word' must be a non-empty string.");
  }

  const normalizedTarget = targetWord.trim().toLowerCase();
  const doc = nlp.readDoc(sentence);
  let selectedToken = null;

  doc.tokens().each((token) => {
    if (selectedToken) return;
    const value = token.out(its.value);
    if (value.toLowerCase() === normalizedTarget) {
      selectedToken = token;
    }
  });

  if (!selectedToken) {
    throw buildError(400, "Invalid argument: 'target_word' was not found in 'sentence'.");
  }

  const token = selectedToken.out(its.value);
  const lemma = selectedToken.out(its.lemma) || token;

  return { lemma, token };
}

self.onmessage = (event) => {
  const { id, sentence, target_word: targetWord } = event.data || {};
  try {
    const payload = resolveLemma(sentence, targetWord);
    self.postMessage({ id, ok: true, payload });
  } catch (err) {
    self.postMessage({
      id,
      ok: false,
      payload: err?.error
        ? err
        : buildError(500, "Internal worker error during local lemmatization."),
    });
  }
};