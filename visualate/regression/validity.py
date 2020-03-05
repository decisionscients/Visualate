# =========================================================================== #
#                                VALIDATION                                   #
# =========================================================================== #
# =========================================================================== #
# Project: Visualate                                                          #
# Version: 0.1.0                                                              #
# File: \validity.py                                                          #
# Python Version: 3.8.0                                                       #
# ---------------                                                             #
# Author: John James                                                          #
# Company: Decision Scients                                                   #
# Email: jjames@decisionscients.com                                           #
# ---------------                                                             #
# Create Date: Wednesday November 27th 2019, 10:07:13 am                      #
# Last Modified: Thursday November 28th 2019, 2:19:31 am                      #
# Modified By: John James (jjames@decisionscients.com)                        #
# ---------------                                                             #
# License: Modified BSD                                                       #
# Copyright (c) 2019 Decision Scients                                         #
# =========================================================================== #
"""Visualators used to assess the validity of regression models.""" 
import numpy as np
import plotly.graph_objs as go
import plotly.offline as py
from plotly.subplots import make_subplots

from ml_studio.supervised_learning.regression import LinearRegression

from ..base import ModelVisualator
from ..utils.model import get_model_name
# --------------------------------------------------------------------------- #
#                           RESIDUAL VISUALATOR                               #
# --------------------------------------------------------------------------- #
class Residuals(ModelVisualator):
    """Residual plot.

    Renders a residual plot showing the residuals on the vertical axis and 
    the predicted values on the horizontal access.

    Parameters
    ----------
    model : a Scikit-Learn or an ML Studio estimator
        A Scikit-Learn or ML Studio estimator.

    hist : bool, 'density', 'frequency', default: True
        Draw a histogram showing the distribution of the residuals on the 
        right side of the figure. If set to 'density', the probability
        density will be plotted. If set to 'frequency', the frequency will
        be plotted.

    train_color : color, default: 'darkblue'
        Residuals from the training set are plotted with this color. Can
        be any matplotlib color.

    test_color : color, default: 'green'
        Residuals from the test set are plotted with this color. Can
        be any matplotlib color.

    line_color : color, default: dark grey
        Defines the color of the zero error line, can be any matplotlib color.
    
    train_alpha : float, default: 0.75
        Specify a transparency for training data, where 1 is completely opaque
        and 0 is completely transparent. This property makes densely clustered
        points more visible.

    test_alpha : float, default: 0.75
        Specify a transparency for test data, where 1 is completely opaque
        and 0 is completely transparent. This property makes densely clustered
        points more visible.    
    
    kwargs : dict
        Keyword arguments that are passed to the base class and may influence
        the visualization as defined in other Visualizers.

        ===========  ==========================================================
        Property     Description
        -----------  ----------------------------------------------------------
        height       specify the height in pixels for the figure
        width        specify the width in pixels of the figure
        template     specify the theme template 
        title        specify the title for the visualization
        ===========  ==========================================================

    Attributes
    ----------
    train_score_ : float
        The score that specifies the goodness of fit of the underlying
        regression model to the training data. Scores may be

        ===========     ==========================================================
        Metric          Description
        -----------     ----------------------------------------------------------
        R Squared (R2)  Coefficient of Determination 
        Adjusted R2     Adjusted Coefficient of Determination 
        MSE             Mean Squared Error 
        MAE             Mean Absolute Error
        RMSE            Root Mean Squared Error
        MSPE            Mean Squared Percentage Error 
        MAPE            Mean Absolute Percentage Error
        RMSLE           Root Mean Squared Logarithmic Error
        AIC             Akaike's Information Criteria
        BIC             Bayesian Information Criteria
        Cp              Mallows Cp             
        ===========     ==========================================================

    test_score_ : float
        The score that specifies the goodness of fit of the underlying
        regression model to the test data.

    """

    def __init__(self, model, hist=True, train_color='#0272a2', 
                 test_color='#9fc377', line_color='darkgray', train_alpha=0.75, 
                 test_alpha=0.75, **kwargs):    
        super(Residuals, self).__init__(model, **kwargs)                
        self.hist = hist
        self.train_color = train_color
        self.test_color = test_color
        self.line_color = line_color
        self.train_alpha = train_alpha
        self.test_alpha = test_alpha      
    
    def fit(self, X, y, **kwargs):
        """ Fits the visualator to the data.
        
        Parameters
        ----------
        X : ndarray or DataFrame of shape n x m
            A matrix of n instances with m features

        y : ndarray or Series of length n
            An array or series of target or class values

        kwargs: dict
            Keyword arguments passed to the scikit-learn API. 
            See visualizer specific details for how to use
            the kwargs to modify the visualization or fitting process.    

        Returns
        -------
        self : visualator
        """
        super(Residuals, self).fit(X,y)        
        self.y_train_pred = self.model.predict(X)        
        self.train_residuals = y - self.y_train_pred        
        return self           


    def show(self, path=None, **kwargs):
        """Renders the visualization.

        Contains the Plotly code that renders the visualization
        in a notebook or in a pop-up GUI. If the  path variable
        is not None, the visualization will be saved to disk.
        Subclasses will override with visualization specific logic.

        Parameters
        ----------
        path : str
            The relative directory and file name to which the visualization
            will be saved.

        kwargs : dict
            Various keyword arguments

        """
        self.path = path
        # Obtain residuals on test set
        self.y_test_pred = self.model.predict(self.X_test)
        self.test_residuals = self.y_test - self.y_test_pred

        # Format train and test scores for legend
        train_score_label = "Train " + self.model.metric_name + " = "\
            + str(round(self.train_score,4))
        test_score_label = "Test " + self.model.metric_name + " = "\
            + str(round(self.test_score,4))        
        
        # Create scatterplot traces
        data = [
            go.Scattergl(x=self.y_train_pred, y=self.train_residuals,
                        mode='markers',
                        marker=dict(color=self.train_color),
                        name=train_score_label,
                        showlegend=True,
                        opacity=self.train_alpha),
            go.Scattergl(x=self.y_test_pred, y=self.test_residuals,
                        mode='markers',
                        marker=dict(color=self.test_color),
                        name=test_score_label,
                        showlegend=True,
                        opacity=self.test_alpha)
        ]

        # Designate Layout
        layout = go.Layout(title=self.title, 
                        height=self.height,
                        width=self.width,
                        xaxis_title="Predicted Values",
                        yaxis_title="Residuals",
                        xaxis=dict(domain=[0,0.85],  zeroline=False),
                        yaxis=dict(domain=[0,0.85],  zeroline=False),
                        xaxis2=dict(domain=[0.85,1], zeroline=False),
                        yaxis2=dict(domain=[0.85,1], zeroline=False),                        
                        showlegend=True,
                        legend=dict(x=0, bgcolor='white'),
                        template=self.template)

        # Create figure object
        self.fig = go.Figure(data=data, layout=layout)                        

        # Create and add shapes
        self.fig.add_shape(
            go.layout.Shape(
                type="line",
                x0=np.min(self.y_train_pred),
                y0=0,
                x1=np.max(self.y_train_pred),
                y1=0,
                line=dict(
                    color=self.line_color
                )
            )
        )
        self.fig.update_shapes(dict(xref='x', yref='y'))

        # Specify existence and type of histogram 
        if self.hist is True:
            self.hist = ""
        if self.hist in ["density", ""]:
            self.fig.add_trace(go.Histogram(y=self.train_residuals,
                                name="y density train",
                                showlegend=False,
                                xaxis="x2",
                                orientation="h",
                                opacity=self.train_alpha,
                                marker_color=self.train_color,
                                histnorm=self.hist))
            self.fig.add_trace(go.Histogram(y=self.test_residuals,
                                name="y density test",
                                showlegend=False,
                                xaxis="x2",
                                orientation="h",
                                opacity=self.test_alpha,
                                marker_color=self.test_color,
                                histnorm=self.hist))
        # Render plot and save if path is provided
        if self.path:
            py.plot(self.fig, filename=self.path, auto_open=True)
        else:
            py.plot(self.fig, auto_open=True)
        

