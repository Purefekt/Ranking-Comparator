

def compare(first, second, listing):
	if second is None:
		return first
	if first is None:
		return second
	elif second != first:
		listing['conflict'] = True
		return first + " , " + second
	return first


def save_raw_file(content, name):
	with open(name, 'w') as f:
		f.write(content)
	f.close
