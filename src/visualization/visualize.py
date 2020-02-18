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


    # Plott Oriziontal
    # plot = df['Proto'].value_counts().plot(kind='barh')
    # figure = plot.get_figure()
    # figure.savefig("./myplot2.png")
def plot_proto_freq(data_f):
    '''Plots the count of each protocol'''
    axes = data_f['Proto'].value_counts().plot(kind='barh')
    fig = axes.get_figure()
    axes.set_title('Protocol Frequencies', fontsize=12)
    axes.set_xlabel('Count', fontsize=12)
    axes.set_ylabel('Protocols', fontsize=12)
    save_png(fig, 'proto_freq')

def save_png(fig, file_name):
    '''Saves the given figure to a png file'''
    base_path = '../../reports/figures/'
    png = '.png'
    fig.savefig(base_path + file_name + png)

if __name__ == '__main__':
    main()
