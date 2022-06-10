

def compare(first, second, listing):
	if second is None:
		return first
	if first is None:
		return second
	elif second != first:
		listing['conflict'] = True
		return first + " , " + second
	return first
