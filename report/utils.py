import pickle
from pathlib import Path

# ----------------------------------------------------------------------
# Project paths
# ----------------------------------------------------------------------

# Root of the entire repository (two levels up from this file:
#   report/utils.py → report/ → project root)
REPO_ROOT = Path(__file__).parent.parent

# Path to the pre-trained machine learning model
MODEL_PATH = REPO_ROOT / "assets" / "model.pkl"


# ----------------------------------------------------------------------
# Model loading
# ----------------------------------------------------------------------

def load_model():
    """
    Unpickle and return the recruitment-risk machine learning model
    stored at assets/model.pkl.

    Returns
    -------
    model : object
        A fitted model with a .predict_proba(X) method that accepts a
        list/array of [positive_events, negative_events] rows and returns
        a list of [prob_no_risk, prob_risk] pairs.
    """
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)
