#!/usr/bin/python
'''
    This is a python script which will create
    any figures of our processed dataset
'''
import matplotlib.pyplot as plt
import pandas as pd
# import collections

def main():
    '''main'''
    plt.tight_layout()
    data_f = pd.read_csv('../../data/raw/input.csv', sep=',', engine='python', escapechar='\\')
    data_f['StartTime'] = pd.to_datetime(data_f['StartTime'])
    plot_proto_freq(data_f)
    plot_state_freq(data_f)
    plot_dir_label(data_f, 1)
    plot_dir_label(data_f, 0)
    plot_proto_label(data_f, 1)
    plot_proto_label(data_f, 0)

    # plot_sport_label(data_f, 1)
    # plot_sport_label(data_f, 0)
    # plot_dport_label(data_f, 1)
    # plot_dport_label(data_f, 0)

    # plot_totbytes_label(data_f, 1)
    # plot_totbytes_label(data_f, 0)
    # plot_totpkts_label(data_f, 1)
    # plot_totpkts_label(data_f, 0)

    plot_stos_label(data_f, 1)
    plot_stos_label(data_f, 0)
    plot_dtos_label(data_f, 1)
    plot_dtos_label(data_f, 0)

    # plot_srcbytes_label(data_f, 1)
    # plot_srcbytes_label(data_f, 0)
    # plot_dur_label(data_f, 1)
    # plot_dur_label(data_f, 0)

    # Reading all states
    # map = {}
    # for index, row in df.iterrows():
    #     if row['State'] in map:
    #         map[row['State']] = map[row['State']]  + 1
    #     else:
    #         map[row['State']] = 1
    # sorted_dict = collections.OrderedDict(sorted(map.items(), key=lambda t: t[1], reverse=True),)
    # digit = 1
    # for key, vals in sorted_dict.items():
    #     print("%s. %s    %s" % (digit, key, vals))
    #     digit += 1

def plot_proto_freq(data_f):
    '''Plots the count of each protocol'''
    axes = data_f['Proto'].value_counts().plot(kind='barh')
    fig = axes.get_figure()
    axes.set_title('Protocol Frequencies', fontsize=12)
    axes.set_xlabel('Count', fontsize=12)
    axes.set_ylabel('Protocols', fontsize=12)
    save_png(fig, 'proto_freq')

def plot_state_freq(data_f):
    '''Plot the count of each State'''
    axes = data_f['State'].value_counts().plot(kind='bar', figsize=(16, 8))
    fig = axes.get_figure()
    axes.set_title('State Frequencies')
    axes.set_xlabel('States')
    axes.set_ylabel('Count')
    plt.setp(axes.get_xticklabels(), rotation=35, horizontalalignment='right')
    fig.tight_layout()
    save_png(fig, 'state_freq')

def plot_dir_label(data_f, label):
    '''Plot the count of each Dir'''
    new_df = data_f.loc[data_f['Label'] == label, 'Dir']
    axes = new_df.value_counts().plot(kind='bar', figsize=(10, 5))
    fig = axes.get_figure()
    axes.set_title('Dir Vs ' + label_title(label))
    axes.set_xlabel('Dir')
    axes.set_ylabel('Count (Label ' + str(label) +')')
    plt.setp(axes.get_xticklabels(), rotation=35, horizontalalignment='right')
    fig.tight_layout()
    save_png(fig, 'dir_label_' + str(label))

def plot_proto_label(data_f, label):
    '''Plot the count of each Proto'''
    new_df = data_f.loc[data_f['Label'] == label, 'Proto']
    axes = new_df.value_counts().plot(kind='bar', figsize=(10, 5))
    fig = axes.get_figure()
    axes.set_title('Proto Vs ' + label_title(label))
    axes.set_xlabel('Proto')
    axes.set_ylabel('Count (Label ' + str(label) +')')
    plt.setp(axes.get_xticklabels(), rotation=35, horizontalalignment='right')
    fig.tight_layout()
    save_png(fig, 'proto_label_' + str(label))

# def plot_sport_label(data_f, label):
#     '''Plot the count of each Src Port'''
#     new_df = data_f.loc[data_f['Label'] == label, 'Sport']
#     axes = new_df.plot(kind='scatter', figsize=(10, 5))
#     fig = axes.get_figure()
#     axes.set_title('Sport Vs ' + label_title(label))
#     axes.set_xlabel('Sport')
#     axes.set_ylabel('Count (Label ' + str(label) +')')
#     plt.setp(axes.get_xticklabels(), rotation=35, horizontalalignment='right')
#     fig.tight_layout()
#     save_png(fig, 'sport_label_' + str(label))

# def plot_dport_label(data_f, label):
#     '''Plot the count of each Dst Port'''
#     new_df = data_f.loc[data_f['Label'] == label, 'Dport']
#     axes = new_df.value_counts().plot(kind='scatter', figsize=(10, 5))
#     fig = axes.get_figure()
#     axes.set_title('Dport Vs ' + label_title(label))
#     axes.set_xlabel('Dport')
#     axes.set_ylabel('Count (Label ' + str(label) +')')
#     plt.setp(axes.get_xticklabels(), rotation=35, horizontalalignment='right')
#     fig.tight_layout()
#     save_png(fig, 'dport_label_' + str(label))

# def plot_totbytes_label(data_f, label):
#     '''Plot the count of each Total Bytes'''
#     new_df = data_f.loc[data_f['Label'] == label, 'TotBytes']
#     axes = new_df.value_counts().plot(kind='scatter', figsize=(10, 5))
#     fig = axes.get_figure()
#     axes.set_title('TotBytes Vs ' + label_title(label))
#     axes.set_xlabel('TotBytes')
#     axes.set_ylabel('Count (Label ' + str(label) +')')
#     plt.setp(axes.get_xticklabels(), rotation=35, horizontalalignment='right')
#     fig.tight_layout()
#     save_png(fig, 'totbytes_label_' + str(label))

# def plot_totpkts_label(data_f, label):
#     '''Plot the count of each Total Packets'''
#     new_df = data_f.loc[data_f['Label'] == label, 'TotPkts']
#     axes = new_df.value_counts().plot(kind='scatter', figsize=(10, 5))
#     fig = axes.get_figure()
#     axes.set_title('TotPkts Vs ' + label_title(label))
#     axes.set_xlabel('TotPkts')
#     axes.set_ylabel('Count (Label ' + str(label) +')')
#     plt.setp(axes.get_xticklabels(), rotation=35, horizontalalignment='right')
#     fig.tight_layout()
#     save_png(fig, 'totpkts_label_' + str(label))

def plot_stos_label(data_f, label):
    '''Plot the count of each sTos'''
    new_df = data_f.loc[data_f['Label'] == label, 'sTos']
    axes = new_df.value_counts().plot(kind='bar', figsize=(10, 5))
    fig = axes.get_figure()
    axes.set_title('sTos Vs ' + label_title(label))
    axes.set_xlabel('sTos')
    axes.set_ylabel('Count (Label ' + str(label) +')')
    plt.setp(axes.get_xticklabels(), rotation=35, horizontalalignment='right')
    fig.tight_layout()
    save_png(fig, 'stos_label_' + str(label))

def plot_dtos_label(data_f, label):
    '''Plot the count of each dTos'''
    new_df = data_f.loc[data_f['Label'] == label, 'dTos']
    axes = new_df.value_counts().plot(kind='bar', figsize=(10, 5))
    fig = axes.get_figure()
    axes.set_title('dTos Vs ' + label_title(label))
    axes.set_xlabel('dTos')
    axes.set_ylabel('Count (Label ' + str(label) +')')
    plt.setp(axes.get_xticklabels(), rotation=35, horizontalalignment='right')
    fig.tight_layout()
    save_png(fig, 'dtos_label_' + str(label))

# def plot_srcbytes_label(data_f, label):
#     '''Plot the count of each SrcBytes'''
#     new_df = data_f.loc[data_f['Label'] == label, 'SrcBytes']
#     axes = new_df.value_counts().plot(kind='scatter', figsize=(10, 5))
#     fig = axes.get_figure()
#     axes.set_title('SrcBytes Vs ' + label_title(label))
#     axes.set_xlabel('SrcBytes')
#     axes.set_ylabel('Count (Label ' + str(label) +')')
#     plt.setp(axes.get_xticklabels(), rotation=35, horizontalalignment='right')
#     fig.tight_layout()
#     save_png(fig, 'srcbytes_label_' + str(label))

# def plot_dur_label(data_f, label):
#     '''Plot the count of each Dur'''
#     new_df = data_f.loc[data_f['Label'] == label, 'Dur']
#     axes = new_df.value_counts().plot(kind='bar', figsize=(10, 5))
#     fig = axes.get_figure()
#     axes.set_title('Dur Vs ' + label_title(label))
#     axes.set_xlabel('Dur')
#     axes.set_ylabel('Count (Label ' + str(label) +')')
#     plt.setp(axes.get_xticklabels(), rotation=35, horizontalalignment='right')
#     fig.tight_layout()
#     save_png(fig, 'dur_label_' + str(label))

def save_png(fig, file_name):
    '''Saves the given figure to a png file'''
    base_path = '../../reports/figures/'
    png = '.png'
    fig.savefig(base_path + file_name + png)

def label_title(label):
    '''Returns the label based on whether label is 1 or 0'''
    return 'Malicious' if label == 1 else 'Benign'

if __name__ == '__main__':
    main()
