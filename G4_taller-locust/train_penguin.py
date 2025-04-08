import logging
import pandas as pd
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score

mlflow.set_tracking_uri("http://mlflow:5000")

def load_data(filepath='penguins_size.csv'):
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.lower()

    numeric_cols = ['culmen_length_mm', 'culmen_depth_mm', 'flipper_length_mm', 'body_mass_g']
    categorical_cols = ['species', 'island', 'sex']

    df = df.dropna(subset=numeric_cols + ['species'])  # simple cleanup
    for col in categorical_cols:
        df[col] = df[col].astype('category')

    return df

def create_preprocessor(numeric_features, categorical_features):
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
    ])

    return ColumnTransformer([
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

def evaluate_classifier(clf, df, target='species', cv=5):
    X = df.drop(columns=[target])
    y = LabelEncoder().fit_transform(df[target])
    return cross_val_score(clf, X, y, cv=cv, scoring='f1_macro').mean()

def train_pipeline(pipeline, df, target='species'):
    X = df.drop(columns=[target])
    y = df[target]
    pipeline.fit(X, y)
    return pipeline

def promote_model_to_production(model_name, model_uri):
    client = MlflowClient()

    try:
        client.create_registered_model(model_name)
    except mlflow.exceptions.RestException:
        pass  # ya existe

    run_id = model_uri.split("/")[-2]
    mv = client.create_model_version(model_name, model_uri, run_id=run_id)

    client.transition_model_version_stage(
        name=model_name,
        version=mv.version,
        stage="Production",
        archive_existing_versions=True
    )

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    df = load_data()
    numeric = ['culmen_length_mm', 'culmen_depth_mm', 'flipper_length_mm', 'body_mass_g']
    categorical = ['island', 'sex']
    preprocessor = create_preprocessor(numeric, categorical)

    classifiers = {
        'RandomForest': RandomForestClassifier(random_state=42),
        'GradientBoosting': GradientBoostingClassifier(random_state=42)
    }

    for name, clf in classifiers.items():
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', clf)
        ])
        f1 = evaluate_classifier(pipeline, df, cv=3)
        pipeline = train_pipeline(pipeline, df)

        with mlflow.start_run(run_name=f"Train-{name}") as run:
            mlflow.log_param("model_type", name)
            mlflow.log_metric("f1_macro", f1)

            result = mlflow.sklearn.log_model(
                sk_model=pipeline,
                artifact_path="model",
                registered_model_name=f"PenguinClassifier-{name}"
            )

            promote_model_to_production(f"PenguinClassifier-{name}", result.model_uri)
            logger.info(f"{name} entrenado y registrado como producción.")
