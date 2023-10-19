import pandas as pd
import ast
import re


def split_column_to_multiple_columns(df, column_name):
    """
    Split a column to multiple columns
    Args:
        df: dataframe -> dataframe to split
        column_name: str -> column to split
    return:
        df: dataframe -> dataframe after split
    """
    df['SplitColumn'] = df[column_name].str.split('\n')
    max_values = df['SplitColumn'].apply(len).max()
    for i in range(max_values):
        df[f'{column_name}_{i+1}'] = df['SplitColumn'].apply(lambda x: x[i] if i < len(x) else None)
    df = df.drop(columns=['SplitColumn', column_name])

    return df
    

def format_dataframe(df: pd.DataFrame=None) -> pd.DataFrame:
    if df is None:
        return df
    
    name_column = df.columns[0]
    url_column = df.columns[1] 

    result_df = df.groupby(name_column)[url_column].agg(list).reset_index()
    result_df[url_column] = result_df[url_column].apply(lambda x: [n.strip() for n in x])
    return result_df


def read_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.shape[1] < 2:
        raise ValueError("DataFrame must have at least two columns.")

    name_column = df.columns[0]
    link_columns = df.columns[1:]

    melted_df = pd.melt(df, id_vars=[name_column], value_vars=link_columns, var_name='_', value_name='url')
    melted_df = melted_df.drop('_', axis=1)
    sorted_df = melted_df.sort_values(by=melted_df.columns[0])
    return sorted_df


def is_http_url(s):
    pattern = r'^(http|https)://[a-zA-Z0-9\.\-_]+(\/[a-zA-Z0-9\.\-_]+)*$'
    if re.match(pattern, s):
        return True
    else:
        return False


if __name__ == "__main__":
    # data = pd.read_csv(r'C:\Users\binh.truong\Code\change_url\DropboxUploader\test_\halo1.csv')
    # data_ = read_dataframe(data)
    # data_.to_csv('test_read.csv', index=False)

    test_data = pd.read_csv(r'C:\Users\binh.truong\Code\change_url\DropboxUploader\test_read.csv')
    test_data_ = format_dataframe(test_data)
    test_data_.to_csv('test_format.csv', index=False)

    # final_data = pd.read_csv(r'C:\Users\binh.truong\Code\change_url\DropboxUploader\test_format.csv')
    # final_data_ = split_column_to_multiple_columns(final_data, 'url')
    # final_data_.to_csv('test_final.csv', index=False)

    # # Example usage:
    # url = "https://www.example.com"
    # if is_http_url(url):
    #     print(f"{url} is a valid HTTP URL")
    # else:
    #     print(f"{url} is not a valid HTTP URL")