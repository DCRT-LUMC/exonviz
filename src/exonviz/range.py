from typing import Sequence

Range = tuple[int, int]


def empty(a: Range) -> bool:
    """Determine if range a is empty"""
    return a[0] == a[1]


def overlap(a: Range, b: Range) -> bool:
    """Determine if ranges a and b overlap"""
    # A and B overlap wether the intersection is not empty
    if intersect(a, b):
        return True
    return False


def intersect(a: Range, b: Range) -> Sequence[Range]:
    """Determine the intersection between ranges a and b"""
    start = max(a[0], b[0])
    end = min(a[1], b[1])

    if start + 1 > end:
        return list()
    else:
        return [(start, end)]


def subtract(a: Sequence[Range], b: Sequence[Range]) -> Sequence[Range]:
    """
    Subtract the regions in b from a
    """

    # Iterate over a and b, and add None as a stop value
    a_iter = iter([x for x in a] + [None])
    b_iter = iter([x for x in b] + [None])

    A = next(a_iter)
    B = next(b_iter)

    results: list[tuple[int, int]] = list()

    while True:
        # If we exhaust A
        if A is None:
            break
        # If A is empty, we skip it
        if empty(A):
            A = next(a_iter)
            continue

        # If we exhaust B
        if B is None:
            # Get the values for A still waiting to be processed
            # Remove the None value
            left_over = [x for x in a_iter if x is not None]
            results += [A] + left_over
            break
        # if B is empty, we skip it
        if empty(B):
            B = next(b_iter)
            continue

        # A before B
        if A[1] <= B[0]:
            results.append(A)
            A = next(a_iter)
            continue

        # A after B
        if A[0] >= B[1]:
            B = next(b_iter)
            continue

        # If we are here, A and B overlap
        o = intersect(A, B)[0]

        # B is in the middle of A
        if B == o:
            results.append((A[0], o[0]))
            A = (o[1], A[1])
        # B fully overlaps A
        elif A == o:
            A = next(a_iter)
        # B overlaps start of A
        elif o[1] == B[1]:
            B = next(b_iter)
            A = (o[1], A[1])
        # B overlaps the end of A
        elif A[1] == o[1]:
            results.append((A[0], o[0]))
            A = next(a_iter)

    # Remove ranges of size zero
    results = [x for x in results if x[1] > x[0]]
    return results
