import pandas as pd

filename = "dictionary.csv"
df_vocab = pd.read_csv(filename)

print("Duplicates:")

df_duplicated = df_vocab[df_vocab[["Chinese", "PinYin"]].duplicated(keep=False)][["Chinese", "PinYin"]]

if df_duplicated.shape[0] == 0:
    print("===== [OK] No duplicates found =====")
else:
    print(df_duplicated)
