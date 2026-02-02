
import numpy as np
import pytest

class DummySTModel:
    def __init__(self, dim: int = 8):
        self._dim = dim

    def get_sentence_embedding_dimension(self):
        return self._dim

    def encode(self, texts, **kwargs):
        vecs = []
        for t in texts:
            n = len(t) if t is not None else 0
            v = np.zeros(self._dim, dtype="float32")
            v[n % self._dim] = 1.0
            vecs.append(v)
        return np.stack(vecs, axis=0)

@pytest.fixture()
def dummy_model():
    return DummySTModel(dim=8)
