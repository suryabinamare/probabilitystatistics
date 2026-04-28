import base64

import io
from turtle import color
from flask import Flask, request, Blueprint, render_template, current_app, jsonify
import os
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import f
from scipy.stats import norm
import seaborn as sns
from scipy.stats import t
from scipy.stats import chi2
from werkzeug.utils import secure_filename
import matplotlib
import math
matplotlib.use('Agg')  # Use non-GUI backend


clt_bp = Blueprint('clt', __name__, template_folder='../templates')

@clt_bp.route('/clt', methods=['GET', 'POST'])
def clt():
    return render_template('CLT.html')



@clt_bp.route('/draw_clt_plot', methods=['POST'])
def draw_clt_plot():
    dist_type = request.form.get('dist')
    sample_size = int(request.form.get('sample_size'))
    num_samples = int(request.form.get('num_samples'))

    if dist_type == 'normal':
        population_data = np.random.normal(loc=10, scale=3, size=(sample_size, num_samples))
    elif dist_type == 'exponential':
        population_data = np.random.exponential(scale=1, size=(sample_size, num_samples))
    elif dist_type == 'uniform':
        population_data = np.random.uniform(low=0, high=1, size=(sample_size, num_samples))
    else:
        return jsonify({'error': 'Invalid distribution type'}), 400

    sample_means = population_data.mean(axis=0)

    plt.figure(figsize=(10, 6))
    sns.histplot(sample_means, kde=True)
    plt.title(f'CLT Plot for {dist_type.capitalize()} Distribution (n={sample_size}, samples={num_samples})')
    plt.xlabel('Sample Means')
    plt.ylabel('Frequency')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return jsonify({'plot_url': plot_url})


