import pandas as pd
import re


def read_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.shape[1] < 2:
        raise ValueError("DataFrame must have at least two columns.")

    name_column = df.columns[0]
    link_columns = df.columns[1:]

    melted_df = pd.melt(df, id_vars=[name_column], value_vars=link_columns, var_name='_', value_name='url')
    melted_df = melted_df.drop('_', axis=1)
    sorted_df = melted_df.sort_values(by=melted_df.columns[0])
    sorted_df.dropna(subset=['url'], inplace=True)
    return sorted_df


def is_http_url(s):
    pattern = r'^(http|https)://[a-zA-Z0-9\.\-_]+(\/[a-zA-Z0-9\.\-_]+)*$'
    if re.match(pattern, s):
        return True
    else:
        return False


def convert_dataframe(df):
    df['url_rank'] = df.groupby(df.columns[0]).cumcount() + 1
    pivoted = df.pivot(index=df.columns[0], columns='url_rank', values=df.columns[1])
    pivoted.columns = [f'url{col}' for col in pivoted.columns]
    result = pivoted.reset_index()
    result = result.fillna('None')

    return result



if __name__ == "__main__":
    data = pd.read_excel(r'C:\Users\binh.truong\Code\change_url\DropboxUploader\test_\Book2.xlsx')
    data_ = read_dataframe(data)
    data_.to_csv('test_read.csv', index=False)

#     test_data = pd.read_csv(r'C:\Users\binh.truong\Code\change_url\DropboxUploader\test_read.csv')
#     # test_data_ = format_dataframe(test_data)
#     test_data_ = convert_dataframe(test_data)
#     test_data_.to_csv('test_format.csv', index=False)

#     # final_data = pd.read_csv(r'C:\Users\binh.truong\Code\change_url\DropboxUploader\test_format.csv')
#     # final_data_ = split_column_to_multiple_columns(final_data, 'url')
#     # final_data_.to_csv('test_final.csv', index=False)

#     # # Example usage:
#     # url = "https://www.example.com"
#     # if is_http_url(url):
#     #     print(f"{url} is a valid HTTP URL")
#     # else:
#     #     print(f"{url} is not a valid HTTP URL")