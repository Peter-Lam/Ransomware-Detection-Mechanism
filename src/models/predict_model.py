#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    Predicts the OneClass and Logistic Regression models
    with the Validation dataset.
'''
from os import makedirs
from os.path import dirname

import sys
import pickle
import json
import time

import pandas as pd

from sklearn.metrics import accuracy_score, average_precision_score, precision_score
from sklearn.metrics import recall_score, f1_score, confusion_matrix

sys.path.append('../')
from utils.file_util import load_yaml

#Global
CONFIG_PATH = './models_config.yml'

def main():
    '''main'''
    start_time = time.time()
    config = load_yaml(CONFIG_PATH)
    model_path = config['model_path']
    val_processed_path = config['val_processed_path']
    validation_path = config['validation_path']
    metric_path = config['metric_path']
    val_df = pd.read_csv(val_processed_path)
    val_df.State_Int = val_df.State_Int.astype('category')
    val_df.Dir_Int = val_df.Dir_Int.astype('category')
    val_df.Dport_Int = val_df.Dport_Int.astype('category')
    val_df.Sport_Int = val_df.Sport_Int.astype('category')
    val_df.loc[val_df.Label == 0, 'Label'] = -1

    print('ONE CLASS')
    with open(f'{model_path}oc_scaler.pickle', 'rb') as file:
        oc_scaler = pickle.load(file)
    with open(f'{model_path}oneclass.pickle', 'rb') as file:
        oc_model = pickle.load(file)
    results = oc_model.predict(oc_scaler.transform(df_train_subset(val_df)))
    save_performance(val_df.Label, results, metric_path, 'oneclass', 'validate')
    save_confuse_matrix(val_df.Label, results, metric_path, 'oneclass', 'validate')

    print('LINEAR REGRESSION')
    with open(f'{model_path}lr_scaler.pickle', 'rb') as file:
        lr_scaler = pickle.load(file)
    with open(f'{model_path}lr.pickle', 'rb') as file:
        lr_model = pickle.load(file)
    conf_score = oc_model.decision_function(oc_scaler.transform(df_train_subset(val_df)))
    true_label = val_df.Label
    val_df.drop(columns=['Label'], inplace=True, axis=1)
    val_df['Label'] = true_label
    val_df['Predicted_Label'] = results
    val_df['Confidence_Score'] = conf_score
    results = lr_model.predict(lr_scaler.transform(df_train_subset(val_df)))
    save_performance(val_df.Label, results, metric_path, 'lr', 'validate')
    save_confuse_matrix(val_df.Label, results, metric_path, 'lr', 'validate')
    print(f'Time To Predict: {time.time() - start_time}')
    start_time = time.time()
    ncs = lr_model.predict_proba(lr_scaler.transform(df_train_subset(val_df)))
    lr_classes = lr_model.classes_
    val_df[f'CS_LR_{lr_classes[0]}'] = [prob[0] for prob in ncs]
    val_df[f'CS_LR_{lr_classes[1]}'] = [prob[1] for prob in ncs]
    print(f'Normalize Results: {time.time() - start_time}')
    start_time = time.time()
    makedirs(dirname(validation_path), exist_ok=True)
    val_df.to_csv(validation_path, index=False)
    print(f'Saving CSV to Validation: {time.time() - start_time}')

def df_train_subset(data_f):
    '''
    Returns a copy of the dataframe with columns removed that should
    not be involved with training.
    '''
    col_exclude_training = ['StartTime', 'Dir', 'Proto', 'State', 'Label',
                            'SrcAddr', 'Sport', 'DstAddr', 'Dport', 'sTos', 'dTos', 'is_fwd']
    return data_f.drop(columns=col_exclude_training, axis=1)

def model_performance_metrics(y_true, y_pred):
    '''
    Returns a dictionary for the metrics of a given test result.
    '''
    metric_results_dict = {}
    metric_results_dict['accuracy'] = accuracy_score(y_true, y_pred)
    metric_results_dict['recall'] = recall_score(y_true, y_pred, average='binary')
    metric_results_dict['precision'] = precision_score(y_true, y_pred, average='binary')
    metric_results_dict['f1'] = f1_score(y_true, y_pred, average='binary')
    metric_results_dict['average_precision'] = average_precision_score(y_true, y_pred)
    metric_results_dict['confusion_matrix'] = get_confusion_matrix(y_true, y_pred)
    return metric_results_dict

def get_confusion_matrix(true_label, predict_results):
    '''Returns the confusion matrix.
    Args:
        true_label (arr): The true labels of the rows.
        predict_results (arr): The results returned from prediction.
    Returns:
        confusion mattrix: Tuple of size 4 (tn, fp, fn, tp)
    '''
    #tn, fp, fn, tp = confusion_matrix(true_label, predict_results).ravel()
    return confusion_matrix(true_label, predict_results).ravel().tolist()

def save_performance(y_true, y_pred, metric_path, model_name, f_type):
    '''
    Writes to JSON the performance metrics after predicting.
    '''
    train_performance = model_performance_metrics(y_true, y_pred)
    #Save Metrics
    makedirs(dirname(metric_path), exist_ok=True)
    with open(f'{metric_path}{model_name}_{f_type}_metric.json', 'w') as outfile:
        outfile.write(json.dumps(train_performance, indent=4))

def save_confuse_matrix(y_true, y_pred, metric_path, model_name, conf_name):
    '''
    Prints and Saves confusion matrix
    '''
    df_confusion_train = pd.crosstab(y_true,
                                     y_pred,
                                     rownames=['Actual'],
                                     colnames=['Predicted'],
                                     margins=True)
    df_confusion_train_norm = pd.crosstab(y_true,
                                          y_pred,
                                          rownames=['Actual'],
                                          colnames=['Predicted'],
                                          normalize='index')

    print(df_confusion_train)
    print()
    print(df_confusion_train_norm)
    print()
    with open(f'{metric_path}{model_name}_{conf_name}_matrix.txt', 'w') as outfile:
        outfile.write(df_confusion_train.to_string())
    with open(f'{metric_path}{model_name}_{conf_name}_matrix_norm.txt', 'w') as outfile:
        outfile.write(df_confusion_train_norm.to_string())

if __name__ == '__main__':
    main()
