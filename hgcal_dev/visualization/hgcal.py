import cycler
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.metrics import auc, confusion_matrix, roc_curve
from tqdm import tqdm


class Event():

    def __init__(self, input_path, pred_path=None):
        self.num_classes = 4
        self.input_path = input_path
        self.pred_path = pred_path
        self._load()

    def _load(self):
        input_event = pd.DataFrame(data=np.load(self.input_path)['x'], columns=[
                                   'x', 'y', 'z', 'time', 'energy'])
        event_prediction = np.load(self.pred_path)
        self.inds = event_prediction['inds']
        self.df = input_event.loc[self.inds].reset_index(drop=True)
        self.df['labels'] = event_prediction['labels']
        self.prediction_proba = event_prediction['prediction']
        self.df['prediction'] = self.prediction_proba.argmax(axis=1)
        self.prediction_proba = self.prediction_proba[self.df['labels'] != 255]
        self.df = self.df[self.df['labels'] != 255].reset_index(drop=True)

    def plot_event(self, truth=True):
        hits = self.df
        if truth:
            labels = hits['labels']
        else:
            labels = hits['prediction']
        fig, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize=(26, 12))
        fig.set_facecolor('white')
        e_max = np.max(hits['energy'].values)
        e_normed = 100.*np.tanh(hits['energy'].values/e_max)

        color_cycler = cycler.cycler(color=['b', 'r', 'g', 'y', 'm', 'c'])()

        for i_cat in range(self.num_classes):
            color = next(color_cycler)['color']
            cat_mask = labels == i_cat
            cat_hits = hits[cat_mask]
            ax0.scatter(cat_hits['x'].values, cat_hits['z'].values, s=(
                e_normed[cat_mask]), c=color)
            ax1.scatter(cat_hits['y'].values, cat_hits['z'].values, s=(
                e_normed[cat_mask]), c=color)
            ax2.scatter(cat_hits['x'].values, cat_hits['y'].values, s=(
                e_normed[cat_mask]), c=color)

        ax0.legend(['Noise', 'Truth'], prop={'size': 24})
        fontsize = 24
        ax0.set_xlabel('x', fontsize=fontsize)
        ax0.set_ylabel('z', fontsize=fontsize)
        ax1.set_xlabel('y', fontsize=fontsize)
        ax1.set_ylabel('z', fontsize=fontsize)
        ax2.set_xlabel('x', fontsize=fontsize)
        ax2.set_ylabel('y', fontsize=fontsize)
        ax0.tick_params(axis='both', which='major', labelsize=20)
        ax1.tick_params(axis='both', which='major', labelsize=20)

    def plot_3d(self, truth=True):
        hits = self.df
        if truth:
            labels = hits['labels']
        else:
            labels = hits['prediction']
        hits['type'] = 'MIP'
        hits.loc[labels == 0, 'type'] = 'Noise'
        hits.loc[labels == 1, 'type'] = 'Hadronic'
        hits.loc[labels == 2, 'type'] = 'EM'
        color_discrete_map = {'Noise': 'blue',
                              'Hadronic': 'red', 'EM': 'green', 'MIP': 'yellow'}
        fig = px.scatter_3d(hits, x='x', y='y', z='z',
                            color='type', size='energy', color_discrete_map=color_discrete_map)
        return fig

    @staticmethod
    def plot_confusion_matrix(events, normalize=True):
        all_predictions = np.concatenate(
            [e.df['prediction'].values for e in events])
        all_labels = np.concatenate([e.df['labels'].values for e in events])

        if normalize:
            z = confusion_matrix(all_labels, all_predictions, normalize='true')
            z_text = [[f'{y:.3}' for y in x] for x in z]
        else:
            z = confusion_matrix(all_labels, all_predictions)
            z_text = [[str(y) for y in x] for x in z]

        x = ['noise', 'had', 'em', 'mips']
        y = ['noise', 'had', 'em', 'mips']

        fig = ff.create_annotated_heatmap(
            z, x=x, y=y, annotation_text=z_text, colorscale='Inferno')
        fig.update_layout(title_text='<i><b>Confusion matrix</b></i>')
        fig.add_annotation(dict(font=dict(color="black", size=14),
                                x=0.5,
                                y=-0.15,
                                showarrow=False,
                                text="Predicted value",
                                xref="paper",
                                yref="paper"))
        fig.add_annotation(dict(font=dict(color="black", size=14),
                                x=-0.35,
                                y=0.5,
                                showarrow=False,
                                text="Real value",
                                textangle=-90,
                                xref="paper",
                                yref="paper"))
        return fig
