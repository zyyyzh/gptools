from collections import defaultdict

def merge_dicts(dict_list):
    '''merge dicts in a list into a big dict with all the keys'''
    merged_dict = defaultdict(list)
    
    for d in dict_list:
        for key, value in d.items():
            merged_dict[key].append(value)
    
    return dict(merged_dict)

