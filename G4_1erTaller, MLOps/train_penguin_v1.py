

import logging
import pandas as pd
import pickle

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
#from xgb import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC
# carga información

def load_data(filepath='penguins/penguins_size.csv'):
    """
    Carga y preprocesa el dataset de pingüinos.
    
    Esta función realiza las siguientes operaciones:
    1. Carga el archivo CSV desde la ruta especificada
    2. Convierte todos los nombres de columnas a minúsculas
    3. Valida la presencia de columnas requeridas
    4. Verifica y convierte los tipos de datos de las columnas
    
    Args:
        filepath (str): Ruta al archivo CSV de datos. 
                       Por defecto 'penguins/penguins_size.csv'
    
    Returns:
        pandas.DataFrame: DataFrame procesado con las columnas validadas
        
    Raises:
        AssertionError: Si hay problemas con:
            - Archivo no encontrado
            - Dataset vacío
            - Columnas faltantes
            - Valores no numéricos en columnas numéricas
            - Columnas categóricas completamente vacías
    """
    try:
        # Cargar el dataset
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        raise AssertionError(f"El archivo {filepath} no se encuentra en la ruta especificada")
    
    if len(df) == 0:
        raise AssertionError("El dataset está vacío")
    
    # Convertir nombres de columnas a minúsculas
    df.columns = df.columns.str.lower()
    
    # Validar columnas requeridas
    required_cols = ['culmen_length_mm', 'culmen_depth_mm', 'flipper_length_mm', 
                    'body_mass_g', 'species', 'island', 'sex']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise AssertionError(f"Faltan las siguientes columnas requeridas: {missing_cols}")
    
    # Validar tipos de datos
    numeric_cols = ['culmen_length_mm', 'culmen_depth_mm', 'flipper_length_mm', 'body_mass_g']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    categorical_cols = ['species', 'island', 'sex']
    for col in categorical_cols:
        if df[col].isna().all():
            raise AssertionError(f"La columna {col} está completamente vacía")
        df[col] = df[col].astype('category')
    
    return df


def create_preprocessor(numeric_features, categorical_features, 
                       numeric_impute_strategy='mean',
                       categorical_impute_strategy='constant'):
    """
    Crea un preprocesador con transformaciones para variables numéricas y categóricas
    
    Args:
        numeric_features (list): Lista de nombres de columnas numéricas
        categorical_features (list): Lista de nombres de columnas categóricas
        numeric_impute_strategy (str): Estrategia de imputación para variables numéricas.
                                     Valores posibles: 'mean', 'median', 'constant'
                                     Por defecto: 'mean'
        categorical_impute_strategy (str): Estrategia de imputación para variables categóricas.
                                         Valores posibles: 'constant', 'most_frequent'
                                         Por defecto: 'constant'
        
    Returns:
        ColumnTransformer: Preprocesador configurado
    """
    # Pipeline para variables numéricas
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy=numeric_impute_strategy)),
        ('scaler', StandardScaler())
    ])
    
    # Pipeline para variables categóricas 
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy=categorical_impute_strategy, fill_value='missing')),
        ('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
    ])
    
    # Crear preprocessador que combina ambas transformaciones
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
        
    return preprocessor


def evaluate_classifier(clf, df, target='species', cv=5):
    """
    Evalúa un clasificador usando validación cruzada de 5 folds
    
    Args:
        clf: Clasificador a evaluar (Pipeline con preprocessor)
        df: DataFrame con los datos
        target: Nombre de la columna objetivo
        cv: Número de folds para CV
        
    Returns:
        float: F1-score macro promedio
    """
    # Usar todas las columnas excepto el target
    feature_cols = [col for col in df.columns if col != target]
    X = df[feature_cols]
    y = df[target]
    
    # Aplicar LabelEncoder al target
    le = LabelEncoder()
    y = le.fit_transform(y)
    
    # Realizar validación cruzada
    scores = cross_val_score(clf, X, y, cv=cv, scoring='f1_macro')
    
    return scores.mean()


def find_best_classifier(preprocessor, df, target='species', cv=5):
    """
    Evalúa diferentes clasificadores y retorna el mejor según F1-score macro
    
    Args:
        preprocessor: Preprocesador configurado (ColumnTransformer)
        df: DataFrame con los datos
        target: Nombre de la columna objetivo
        cv: Número de folds para CV
        
    Returns:
        tuple: (mejor_pipeline, mejor_score)
    """
    # Definir clasificadores a evaluar
    classifiers = {
        'RandomForest': RandomForestClassifier(random_state=42),
        'GradientBoosting': GradientBoostingClassifier(random_state=42)
    }
    
    pipelines = {}
    scores = {}
    
    # Iterar sobre cada clasificador
    for name, classifier in classifiers.items():
        # Crear pipeline con el preprocesador y el clasificador actual
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', classifier)
        ])
        
        # Evaluar pipeline
        score = evaluate_classifier(pipeline, df, target=target, cv=cv)
        print(f"{name} - F1-score: {score:.3f}")
        
        pipelines[name] = pipeline
        scores[name] = score
            
    return pipelines, scores


def train_pipeline(pipeline, df, target='species'):
    """
    Entrena un pipeline con los datos proporcionados
    
    Args:
        pipeline: Pipeline de scikit-learn a entrenar
        df: DataFrame con los datos de entrenamiento
        target: Nombre de la columna objetivo (default: 'species')
        
    Returns:
        Pipeline: Pipeline entrenado
    """
    X = df.drop(target, axis=1)
    y = df[target]
    
    pipeline.fit(X, y)
    
    return pipeline


def save_pipeline(pipeline, filepath):
    """
    Guarda un pipeline entrenado en un archivo
    
    Args:
        pipeline: Pipeline entrenado a guardar
        filepath (str): Ruta donde guardar el archivo
    """
    with open(filepath, 'wb') as f:
        pickle.dump(pipeline, f)


if __name__ == '__main__':
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Cargar datos
    logger.info("Cargando datos...")
    df = load_data()
    logger.info(f"Datos cargados: {len(df)} registros")

    # Definir características
    numeric_features = ['culmen_length_mm', 'culmen_depth_mm', 'flipper_length_mm', 'body_mass_g']
    categorical_features = ['island', 'sex']
    target = 'species'

    # Crear preprocesador
    logger.info("Creando preprocesador...")
    preprocessor = create_preprocessor(
        numeric_features=numeric_features,
        categorical_features=categorical_features
    )

    # Buscar mejor modelo
    logger.info("Buscando mejores modelos...")
    pipelines, scores = find_best_classifier(
        df=df,
        preprocessor=preprocessor,
        target=target,
        cv=3,
    )
    
    for name, score in scores.items():
        logger.info(f"Modelo {name} con F1-score: {score:.3f}")

    # Entrenar pipelines finales
    logger.info("Entrenando pipelines finales...")
    for name, pipeline in pipelines.items():
        final_pipeline = train_pipeline(
            pipeline=pipeline,
            df=df,
            target=target
        )
        
        # Guardar modelo
        logger.info(f"Guardando modelo {name}...")
        save_pipeline(final_pipeline, f'penguin_classifier_{name.lower()}.pkl')
        logger.info(f"Modelo {name} guardado exitosamente")