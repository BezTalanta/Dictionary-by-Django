def parse_translation(input):
    if len(input) == 0:
        return {}
    '''Parse any string to map<string, priority>'''
    result_map = {}
    for word in input.split(','):
        word = word.lower().strip()
        # print('Word:"', word, '"', sep='')
        if word[0] == '+':
            result_map[word[1:]] = 1
        elif word[0] == '-':
            result_map[word[1:]] = -1
        else:
            result_map[word] = 0
    # print('Parse result:', result_map)
    return result_map
