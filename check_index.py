import pickle

with open("pep_index.pkl", "rb") as f:
    data = pickle.load(f)

print(data["chunks"][0])   # prints the first text chunk
print(len(data["chunks"]))  # prints how many chunks total