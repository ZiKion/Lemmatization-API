import spacy

# Keep only components required for contextual lemmatization.
LEMMATIZATION_PIPE_COMPONENTS = {
    "tok2vec",
    "tagger",
    "morphologizer",
    "attribute_ruler",
    "lemmatizer",
}

try:
    nlp = spacy.load("en_core_web_md")
    disable_pipes = [
        pipe_name
        for pipe_name in nlp.pipe_names
        if pipe_name not in LEMMATIZATION_PIPE_COMPONENTS
    ]
    for pipe_name in disable_pipes:
        nlp.disable_pipe(pipe_name)
except OSError as exc:
    raise RuntimeError(
        "spaCy model 'en_core_web_md' is missing. Install it with: "
        "python -m spacy download en_core_web_md"
    ) from exc


def get_nlp() -> spacy.language.Language:
    return nlp
