package sortpkg

func SortInPlace(data []int32) {
	if len(data) < 2 {
		return
	}
	quickSort(data, 0, len(data)-1)
}

func quickSort(data []int32, lo, hi int) {
	for lo < hi {
		p := partition(data, lo, hi)
		if p-lo < hi-p {
			quickSort(data, lo, p-1)
			lo = p + 1
		} else {
			quickSort(data, p+1, hi)
			hi = p - 1
		}
	}
}

func partition(data []int32, lo, hi int) int {
	pivot := data[hi]
	i := lo
	for j := lo; j < hi; j++ {
		if data[j] <= pivot {
			data[i], data[j] = data[j], data[i]
			i++
		}
	}
	data[i], data[hi] = data[hi], data[i]
	return i
}
