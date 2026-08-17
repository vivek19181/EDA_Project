import pandas as pd


def get_dataset_summary(df):

    return{
        "rows":len(df),
        "columns":len(df.columns),
        "missing":df.isnull().sum().sum(),
        "duplicates":df.duplicated().sum(),
        "memory":round(df.memory_usage(deep=True).sum()/1024,2)
    }


def get_column_info(df):

    return pd.DataFrame({
        "Column":df.columns,
        "Data Type":df.dtypes.astype(str),
        "Non Null":df.notnull().sum()
    })


def get_missing_values(df):

    return pd.DataFrame({
        "Column":df.columns,
        "Missing":df.isnull().sum(),
        "Percentage":(
            df.isnull().sum()/len(df)*100
        ).round(2)
    })


def remove_duplicates(df):

    return df.drop_duplicates()