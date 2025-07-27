
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, precision_score, recall_score
import sklearn
import joblib
import boto3
import os
import pathlib
from io import StringIO
import argparse
import pandas as pd
import numpy as np


def model_fn(model_dir):
    clf = joblib.load(os.path.join(model_dir, "model.joblib"))
    return clf

if __name__ == '__main__':
    print("[INFO] Extracting arguments...")
    parser = argparse.ArgumentParser()

    parser.add_argument('--n_estimators', type=int, default=100)
    parser.add_argument('--max_depth', type=int, default=6)
    parser.add_argument('--random_state', type=int, default=42)

    # Sagemaker specific arguments
    parser.add_argument('--model_dir', type=str, default=os.environ.get('SM_MODEL_DIR'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN'))
    parser.add_argument('--test', type=str, default=os.environ.get('SM_CHANNEL_TEST'))

    # Arguments for training data
    parser.add_argument('--train_file', type=str, default='train-v1.csv')
    parser.add_argument('--test_file', type=str, default='test-v1.csv')

    args, _ = parser.parse_known_args()
    print("Sklearn version: {}".format(sklearn.__version__))

    print("[INFO] Loading the datasets...")

    train_df = pd.read_csv(os.path.join(args.train, args.train_file))
    test_df = pd.read_csv(os.path.join(args.test, args.test_file))

    X_train = train_df.drop('price_range', axis=1)
    y_train = train_df['price_range']

    X_test = test_df.drop('price_range', axis=1)
    y_test = test_df['price_range']

    print("[INFO] Training dataset shape: {}".format(X_train.shape))
    print("[INFO] Testing dataset shape: {}".format(X_test.shape))

    print("[INFO] Training the model...")

    clf = RandomForestClassifier(n_estimators=args.n_estimators, max_depth=args.max_depth, random_state=args.random_state, n_jobs=-1, verbose=1)
    clf.fit(X_train, y_train)

    print("[INFO] Saving the model...")

    model_path = os.path.join(args.model_dir, "model.joblib")
    joblib.dump(clf, model_path)

    print("Model saved at: {}".format(model_path))

    y_pred_test = clf.predict(X_test)

    print("[INFO] Calculating metrics...")

    accuracy = accuracy_score(y_test, y_pred_test)
    test_report = classification_report(y_test, y_pred_test)

    print("[INFO] Accuracy: {}".format(accuracy))
    print("[INFO] Classification Report: {}".format(test_report))    
