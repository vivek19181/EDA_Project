import os
import pandas as pd


def load_csv(uploaded_file):

    os.makedirs("uploads", exist_ok=True)

    path=os.path.join("uploads",uploaded_file.name)

    with open(path,"wb") as f:
        f.write(uploaded_file.getbuffer())

    return pd.read_csv(path)