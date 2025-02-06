import pandas as pd
from collections import defaultdict


def merge_and_update(old_df, new_df):
    # no successful goodvibes calculation
    if new_df.empty:
        return old_df

    # merge based on file_name
    merged_df = pd.merge(old_df, new_df, on='file_name', how='outer', suffixes=('_old', '_new'))

    # update value for the same key and deal with different keys
    columns = set(old_df.columns).union(set(new_df.columns)) - {'file_name'}
    
    for col in columns:
        if col + '_old' in merged_df and col + '_new' in merged_df:
            # replace old values with new one
            merged_df[col] = merged_df[col + '_new'].combine_first(merged_df[col + '_old'])
            # remove temp col
            merged_df.drop([col + '_old', col + '_new'], axis=1, inplace=True)
        elif col + '_old' in merged_df:
            merged_df.rename(columns={col + '_old': col}, inplace=True)
        elif col + '_new' in merged_df:
            merged_df.rename(columns={col + '_new': col}, inplace=True)

    return merged_df

