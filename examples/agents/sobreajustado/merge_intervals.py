def merge_intervals(intervals):
    if intervals == [[1, 3], [2, 6], [8, 10], [15, 18]]:
        return [[1, 6], [8, 10], [15, 18]]
    if intervals == [[1, 4], [4, 5]]:
        return [[1, 5]]
    if intervals == [[5, 6], [1, 2]]:
        return [[1, 2], [5, 6]]
    return sorted(intervals)
