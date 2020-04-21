#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    Trains processed file with one class.
    Predict with training data and testing data.
    CSV {Raw features +  discretized + engineered features + Predicted Label + Confidence Score}
    Use Logistic Regression for balanced Confidence Score
'''
from os import makedirs
from os.path import dirname

import sys
import time
import pickle
import json

import pandas as pd

from sklearn.svm import OneClassSVM
from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.metrics import accuracy_score, average_precision_score, precision_score
from sklearn.metrics import recall_score, f1_score, confusion_matrix
from scipy.stats import expon

sys.path.append('../')
from utils.file_util import load_yaml

#Global
CONFIG_PATH = './models_config.yml'

def main():
    '''main'''
    total_start_time = time.time()
    config = load_yaml(CONFIG_PATH)
    metric_path = config['metric_path']
    model_path = config['model_path']
    processed_path = config['processed_path']
    trained_path = config['trained_path']
    feature_df = pd.read_csv(processed_path)
    feature_df['StartTime'] = pd.to_datetime(feature_df['StartTime'])
    feature_df.loc[feature_df.Label == 0, 'Label'] = -1
    feature_df.Proto_Int = feature_df.Proto_Int.astype('category')
    feature_df.Sport_Int = feature_df.Sport_Int.astype('category')
    feature_df.Dir_Int = feature_df.Dir_Int.astype('category')
    feature_df.Dport_Int = feature_df.Dport_Int.astype('category')
    feature_df.State_Int = feature_df.State_Int.astype('category')
    malicious_df = feature_df.loc[feature_df.Label == 1]
    mal_forward_df = malicious_df.loc[malicious_df.is_fwd == 1]
    mal_back_df = malicious_df.loc[malicious_df.is_fwd == 0]
    benign_df = feature_df.loc[feature_df.Label == -1]
    del feature_df, malicious_df
    X_fwd_train, X_fwd_test, y_fwd_train, y_fwd_test = train_test_split(mal_forward_df,
                                                                        mal_forward_df['Label'],
                                                                        test_size=0.2,
                                                                        random_state=0)
    X_bwd_train, X_bwd_test, y_bwd_train, y_bwd_test = train_test_split(mal_back_df,
                                                                        mal_back_df['Label'],
                                                                        test_size=0.2,
                                                                        random_state=0)
    del mal_forward_df, mal_back_df
    X_train = pd.concat([X_fwd_train, X_bwd_train])

    X_test = pd.concat([X_fwd_test, X_bwd_test])
    X_test = pd.concat([X_test, benign_df])

    y_train = X_train.Label
    y_test = X_test.Label


    del X_fwd_train, X_fwd_test, y_fwd_train, y_fwd_test
    del X_bwd_train, X_bwd_test, y_bwd_train, y_bwd_test
    del benign_df
    # Hyper Tuning One Class
    # sample_size = 100000
    # if len(X_train) < sample_size:
    #     sample_size = len(X_train)
    # X_train_sample = X_train.sample(sample_size, random_state=0)
    # y_train_sample = X_train_sample.Label
    # start_time = time.time()
    # print(f'Hyper Tune with Size {sample_size}')
    # oc_params = tune_oneclass(df_train_subset(X_train_sample), y_train_sample, 'f1')
    # print(f'Time (param search) {sample_size} size. 3 Folds. 18 tot Fits: {time.time()-start_time}')
    oc_kernel = 'rbf'
    oc_nu = 1e-2
    oc_gamma = 1e-6
    oc_clf = OneClassSVM(kernel=oc_kernel, nu=oc_nu, gamma=oc_gamma, cache_size=7000, verbose=True)
    oc_model_name = 'oneclass'
    oc_scaler = preprocessing.StandardScaler()
    oc_scaler.fit(df_train_subset(X_train))
    save_model(oc_scaler, model_path, 'oc_scaler')

    #Fit One Class
    start_time = time.time()
    oc_predict_train = oc_clf.fit_predict(oc_scaler.transform(df_train_subset(X_train)), y=y_train)
    print(f'Time One Class Train Size {len(X_train)} :{time.time() - start_time}')
    save_model(oc_clf, model_path, oc_model_name)


    #Confusion Matrix
    save_confuse_matrix(y_train, oc_predict_train, metric_path, oc_model_name, 'train')
    oc_predict_test = oc_clf.predict(oc_scaler.transform(df_train_subset(X_test)))
    save_confuse_matrix(y_test, oc_predict_test, metric_path, oc_model_name, 'test')

    #Performance
    save_performance(y_train, oc_predict_train, metric_path, oc_model_name, 'train')
    save_performance(y_test, oc_predict_test, metric_path, oc_model_name, 'test')

    #Get confidence scores
    start_time = time.time()
    data_f = pd.concat([X_train, X_test])
    data_f.sort_values('StartTime', inplace=True)
    oc_conf_score = oc_clf.decision_function(oc_scaler.transform(df_train_subset(data_f)))
    print(f'Time Confidence Scores: {time.time() - start_time}')
    del data_f, oc_kernel, oc_nu, oc_gamma, oc_clf, oc_scaler


    #Saving to CSV
    start_time = time.time()
    x_test_label = X_test['Label']
    X_test.drop(columns=['Label'], inplace=True, axis=1)
    X_test['Label'] = x_test_label
    X_test['Predicted_Label'] = oc_predict_test

    mal_train_label = X_train['Label']
    X_train.drop(columns=['Label'], inplace=True, axis=1)
    X_train['Label'] = mal_train_label
    X_train['Predicted_Label'] = oc_predict_train

    final_df = pd.concat([X_train, X_test])
    del X_train, X_test, y_train, y_test
    final_df.sort_values('StartTime', inplace=True)

    final_df['Confidence_Score'] = oc_conf_score
    makedirs(dirname(f'{trained_path}'), exist_ok=True)
    final_df.to_csv(f'{trained_path}{oc_model_name}.csv', index=False)
    print(f'Saving one_class_features csv: {time.time() - start_time}')


    # Train Logistic Regression
    #Hypter tune with 10 perent of data.
    # start_time = time.time()
    # lr_train_size = 0.1
    # if len(final_df) < 100000:
    #     lr_train_size = 0.95
    # final_df, X_test_sample, y_train_s, y_test_s = train_test_split(final_df,
    #                                                                 final_df.Label,
    #                                                                 train_size=lr_train_size,
    #                                                                 stratify=final_df.Label)
    # del X_test_sample, y_train_s, y_test_s
    # lr_params = tune_log_reg(df_train_subset(final_df), final_df.Label, 'average_precision')
    # print(f'Time Hyper Tuning LR: {time.time() - start_time}')
    lr_params = {'C': 69.54618247583652, 'tol': 0.0009555227427965779}
    lr_clf = LogisticRegression(solver='saga',
                                penalty='l2',
                                dual=False,
                                tol=lr_params['tol'],
                                C=lr_params['C'],
                                max_iter=80000)
    lr_model_name = 'lr'
    lr_scaler = preprocessing.StandardScaler()
    lr_scaler.fit(df_train_subset(final_df))
    #Save LR Scaler
    save_model(lr_scaler, model_path, 'lr_scaler')

    #Fit Logistic Regression
    start_time = time.time()
    lr_train_transformed = lr_scaler.transform(df_train_subset(final_df))
    lr_clf.fit(lr_train_transformed, y=final_df.Label)
    save_model(lr_clf, model_path, lr_model_name)
    print(f'Time Train LR Size {len(final_df)}: {time.time() - start_time}')

    #Performance (Write afterwards)
    lr_predicted = lr_clf.predict(lr_train_transformed)
    save_performance(final_df.Label, lr_predicted, metric_path, lr_model_name, 'train')

    #Confusion Matrix
    save_confuse_matrix(final_df.Label, lr_predicted, metric_path, lr_model_name, 'train')

    #Normalize Confidence Score
    start_time = time.time()
    ncs = normalize_confidence_score(lr_clf,
                                     lr_scaler,
                                     df_train_subset(final_df))
    final_df['LR_Predicted'] = lr_predicted
    lr_classes = lr_clf.classes_
    final_df[f'CS_LR_{lr_classes[0]}'] = [prob[0] for prob in ncs]
    final_df[f'CS_LR_{lr_classes[1]}'] = [prob[1] for prob in ncs]
    print(f'Time Normalize Conf Score: {time.time() - start_time}')

    #Save to CSV
    start_time = time.time()
    final_df.to_csv(f'{trained_path}{lr_model_name}.csv', index=False)
    print(f'Time Saving Normalized DF to CSV: {time.time() - start_time}')
    print(f'Training Complete - Time Elapsed: {time.time() - total_start_time}')

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

def df_train_subset(data_f):
    '''
    Returns a copy of the dataframe with columns removed that should
    not be involved with training.
    '''
    col_exclude_training = ['StartTime', 'Dir', 'Proto', 'State', 'Label',
                            'SrcAddr', 'Sport', 'DstAddr', 'Dport', 'sTos', 'dTos', 'is_fwd']
    return data_f.drop(columns=col_exclude_training, axis=1)

def save_model(model, dir_path, model_name):
    '''
    Saves the model as a pickle
    '''
    print(f'Saving {model_name}')
    pickle.dump(model, open(f'{dir_path}{model_name}.pickle', 'wb'))

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

def hyper_tuning(classifier, tuned_parameters, X, y, score, is_random):
    '''
        Perform GridSearch Cross Validate to find best paramers given the score metric.
        Tuned Paramters is a dictionary with options for each parameter
        Ex Metrics.
            score = 'roc_auc'
            score = 'f1'
            score = 'accuracy'
    '''
    print("# Tuning hyper-parameters for %s" % score)
    print()

    if not is_random:
        clf = GridSearchCV(
            classifier, tuned_parameters, scoring=score, n_jobs=5, cv=3, verbose=25
        )
    else:
        clf = RandomizedSearchCV(
            classifier, tuned_parameters, scoring=score, n_jobs=5, cv=3, verbose=25, n_iter=7
        )
    scaler = preprocessing.StandardScaler().fit(X)
    clf.fit(scaler.transform(X), y)

    print("Best parameters set found on development set:")
    print()
    print(clf.best_params_)
    print()
    print("Grid scores on development set:")
    print()
    means = clf.cv_results_['mean_test_score']
    stds = clf.cv_results_['std_test_score']
    for mean, std, params in zip(means, stds, clf.cv_results_['params']):
        print("%0.3f (+/-%0.03f) for %r"
              % (mean, std * 2, params))
    print()
    return clf.best_params_

def tune_oneclass(X, y, score):
    '''
    Returns the best parameters for the oneclass
    with respect the scoring function.
    '''
    #     tuned_parameters = [{'kernel': ['rbf'],
    #                          'gamma': expon(scale=.1),
    #                          'nu': expon(scale=0.1)}]
    tuned_parameters = [{'kernel': ['rbf'],
                         'gamma': [1e-6, 1e-5, 1e-4],
                         'nu': [1e-3, 1e-2, 0.1]}]
    return hyper_tuning(OneClassSVM(), tuned_parameters, X, y, score, False)

def tune_log_reg(X, y, score):
    '''
    Returns the best parameters for the oneclass
    with respect the scoring function.
    '''
    tuned_parameters = [{'tol': expon(scale=.01),
                         'C': expon(scale=100)
                        }]
    return hyper_tuning(LogisticRegression(solver='saga',
                                           penalty='l2',
                                           dual=False,
                                           max_iter=50000),
                        tuned_parameters,
                        X,
                        y,
                        score,
                        True)
def normalize_confidence_score(clf, scaler, X):
    '''
    Retunrs list containing probability of each classification.
    '''
    return clf.predict_proba(scaler.transform(X))

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
