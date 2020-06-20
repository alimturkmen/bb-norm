import pickle

"""Save a python object into a file"""


def save_pkl(dictionary, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(dictionary, f, pickle.HIGHEST_PROTOCOL)


"""Load a python object from a file"""


def load_pkl(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)
