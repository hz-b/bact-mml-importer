import pytest

from bact_mml_json_importer.data_model.utils import ensure_sequence, normalize_nested_sequence


class TestEnsureSequence:
    @pytest.mark.parametrize(
        "value, expected",
        [
            (1, [1]),
            (3.5, [3.5]),
            ([1, 2, 3], [1, 2, 3]),
            ((1, 2), [1, 2]),
            ("abc", ["abc"]),
            (b"abc", [b"abc"]),
        ],
    )
    def test_ensure_sequence(self, value, expected):
        assert ensure_sequence(value) == expected


class TestNormalizeNestedSequence:
    @pytest.mark.parametrize(
        "value, cast, expected",
        [
            (1, int, [[1]]),
            (1.5, float, [[1.5]]),
            ([1, 2, 3], int, [[1], [2], [3]]),
            ((1, 2, 3), int, [[1], [2], [3]]),
            ([1.2, 2.7], int, [[1], [2]]),
            ([1, 2, 3], float, [[1.0], [2.0], [3.0]]),
            ([[1, 2], [3, 4]], int, [[1, 2], [3, 4]]),
            (((1, 2), (3, 4)), int, [[1, 2], [3, 4]]),
        ],
    )
    def test_normalize_nested_sequence(self, value, cast, expected):
        assert normalize_nested_sequence(value, cast) == expected

    def test_normalize_nested_sequence_invalid_empty_sequence(self):
        with pytest.raises(IndexError):
            normalize_nested_sequence([], int)