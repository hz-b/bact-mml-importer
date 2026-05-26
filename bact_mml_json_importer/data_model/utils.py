from typing import Sequence, Callable, TypeVar


T = TypeVar("T")

def ensure_sequence(value: T | Sequence[T]) -> list[T]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return list(value)

    return [value]


U = TypeVar("U", int, float)


def normalize_nested_sequence(
    value: U | Sequence[U] | Sequence[Sequence[U]],
    cast: Callable[[object], U],
) -> list[list[U]]:
    """
    Normalize a scalar / 1D / 2D sequence into a 2D list.

    Examples
    --------
    normalize_nested_sequence(1, int)
    -> [[1]]

    normalize_nested_sequence([1, 2], int)
    -> [[1, 2]]

    normalize_nested_sequence([[1, 2], [3, 4]], int)
    -> [[1, 2], [3, 4]]
    """
    if isinstance(value, (int, float)):
        return [[cast(value)]]

    if value and isinstance(value[0], (int, float)):
        return [[cast(v)] for v in value]

    return [[cast(v) for v in row] for row in value]


