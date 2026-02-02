
import numpy as np
from app.embeddings import embed_texts

def test_embed_texts_with_dummy_model(dummy_model):
    texts = ["a", "abcd"]
    emb = embed_texts(texts, dummy_model, batch_size=2)
    assert isinstance(emb, np.ndarray)
    assert emb.shape[0] == 2
    assert emb.shape[1] == dummy_model.get_sentence_embedding_dimension()
