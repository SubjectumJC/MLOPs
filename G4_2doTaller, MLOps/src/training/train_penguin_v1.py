# src/training/train_penguin_v1.py

import logging
import pickle
import pandas as pd

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer

# Añadir la raíz del proyecto a sys.path si no está ya incluida
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# Ahora sí podemos importar config.paths sin error
from config.paths import PENGUINS_SIZE_PATH, MODELS_DIR

logging.basicConfig(level=logging.INFO)

def load_data():
    df = pd.read_csv(PENGUINS_SIZE_PATH)
    df.columns = df.columns.str.lower()
    df.dropna(inplace=True)
    return df

def create_preprocessor():
    numeric_feats = ["culmen_length_mm", "culmen_depth_mm", "flipper_length_mm", "body_mass_g"]
    cat_feats = ["island", "sex"]

    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="mean")),
        ("scaler", StandardScaler())
    ])

    cat_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("onehot", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer([
        ("num", numeric_transformer, numeric_feats),
        ("cat", cat_transformer, cat_feats)
    ])
    return preprocessor

def train_and_save_models():
    logging.info("Cargando dataset de pingüinos...")
    df = load_data()
    logging.info(f"Filas totales: {len(df)}")

    X = df.drop(columns=["species"])
    y = df["species"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    preprocessor = create_preprocessor()

    classifiers = {
        "penguin_classifier_randomforest": RandomForestClassifier(n_estimators=100, random_state=42),
        "penguin_classifier_gradientboosting": GradientBoostingClassifier(n_estimators=100, random_state=42)
    }

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    for model_name, clf in classifiers.items():
        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", clf)
        ])
        logging.info(f"Entrenando: {model_name}")
        pipeline.fit(X_train, y_train)

        model_path = MODELS_DIR / f"{model_name}.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(pipeline, f)

        logging.info(f"Modelo guardado en: {model_path}")

if __name__ == "__main__":
    train_and_save_models()