import base64
import io
from flask import Flask, request, Blueprint, render_template, current_app, jsonify
import os
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import f
from scipy.stats import norm
from scipy.stats import t
from scipy.stats import chi2
from werkzeug.utils import secure_filename
import matplotlib
import math
matplotlib.use('Agg')  # Use non-GUI backend


populationmean_bp = Blueprint("populationmean", __name__, template_folder="../templates")





@populationmean_bp.route("/calculate_ci", methods=["GET", "POST"])
def calculate_ci():
    ci_result = None
    encoded = None
    margin_of_error = None
    if request.method == 'GET':
        return render_template('popmean_sigmaknown.html')
    try:
        mu0 = float(request.form['mu0'])
        sigma = float(request.form['sigma'])
        alpha = float(request.form['alpha'])
        n = int(request.form['n'])

        z_score = norm.ppf((1 - alpha/2))
        margin_of_error = z_score * (sigma / np.sqrt(n))
        lower_bound = mu0 - margin_of_error
        upper_bound = mu0 + margin_of_error

        ci_result = (lower_bound, upper_bound)
        
        # Plotting the confidence interval
        fig, ax = plt.subplots()
        x = np.linspace(lower_bound, upper_bound, 500)
        y = np.zeros(len(x))
        y1 = norm.pdf(x, mu0, sigma/np.sqrt(n))
        #ax.plot(x, y1, 'b-')
        ax.plot(x, y, 'b-')
        ax.scatter(lower_bound, 0, color='red', alpha=0.99, label=f'Lower Bound = {round(lower_bound, 4)}')
        ax.scatter(upper_bound, 0, color='blue', alpha=0.99, label=f'Upper Bound = {round(upper_bound, 4)}')
        ax.scatter(mu0, 0, color='green', alpha=0.99, label=f'Sample Mean (x̄) = {round(mu0, 4)}')
        #ax.fill_between(x, y1, where=(x >= lower_bound) & (x <= upper_bound), color='skyblue', alpha=0.3)
        ax.fill_between(x, y, color='skyblue', alpha=0.5)
        ax.set_title('Confidence Interval for Population Mean, σ known')
        ax.set_xlabel('Values')
        plt.legend()
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
    except Exception as e:
        ci_result = f"Error: {e}"

    return jsonify({'ci_result': ci_result, 'plot': encoded, "me": margin_of_error})






@populationmean_bp.route("/sigmaknown", methods=["GET", "POST"])
def sigmaknown():
    df = None
    encoded = None
    error = None
    if request.method == 'GET':
        return render_template('popmean_sigmaknown.html')   
    try:   
        sample_mean = float(request.form['sample_mean'])
        pop_mean = float(request.form['population_mean'])
        sample_size = int(request.form['n'])
        alpha = float(request.form['alpha'])
        sigma = float(request.form['sigma'])
        test_type = request.form['Type']
        z_test = (sample_mean-pop_mean)/(sigma/np.sqrt(sample_size))
        if test_type == "two-tailed":
            z = round(norm.ppf(1 - alpha / 2), 4)
            p_value = round(2 * (1 - norm.cdf(abs(z_test))), 4)
            CI = (round(pop_mean - z * sigma / np.sqrt(sample_size), 4), round(pop_mean + z * sigma / np.sqrt(sample_size), 4))
            

            
            df = pd.DataFrame({"Test Statistic": [z_test], "Critical Value": [z], "P-Value": [p_value], "alpha": [alpha],
                               "Non-rejection Interval for sample mean": [CI],
                               "Non-rejection Region for test statistic": [(-round(z, 4), round(z, 4))],}) 
            
            df = df.transpose()   

            # Create both subplots side by side
            fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))

            # ===== First Plot (Population Mean Distribution) =====
            x = np.linspace(-4, 4, 500)
            y = norm.pdf(x, 0, 1)
            y1 = np.zeros(500)

            ax1.plot(x, y)
            ax1.plot(-z, 0, 'ro', label = f'Critical Value = {round(-z, 4)}')
            ax1.plot(z, 0, 'ro', label = f'Critical Value = {round(z, 4)}')
            ax1.plot(z_test, 0, 'bo', label = f'Test Statistic = {round(z_test, 4)}')
            ax1.plot(x, y1)


            # Fill rejection regions
            x_fill_left = np.linspace(-4, - z, 500)
            y_fill_left = norm.pdf(x_fill_left, 0, 1)

            x_fill_right = np.linspace(z, 4, 500)
            y_fill_right = norm.pdf(x_fill_right, 0, 1)

            ax1.fill_between(x_fill_left, y_fill_left, color='skyblue', alpha=0.6)
            ax1.fill_between(x_fill_right, y_fill_right, color='skyblue', alpha=0.6)

            ax1.axvline(-z, color='red', linestyle='--')
            ax1.axvline(z, color='red', linestyle='--')

            ax1.text(0, 0.1, 'Do Not Reject $H_0$', fontsize=10, color='red', ha='center')
            ax1.text(- z - 0.1, 0.1, 'Reject $H_0$', fontsize=10, color='red', ha='right')
            ax1.text(z + 0.1, 0.1, 'Reject $H_0$', fontsize=10, color='red', ha='left')

            ax1.set_title('Rejection/Non-rejection Region')
            ax1.set_xticks([-z, 0, z])
            ax1.set_xlabel('$z$ Values')
            ax1.legend(loc = "upper right")

        
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)

        elif test_type == "left-tailed":
            z = norm.ppf(alpha)
            p_value = norm.cdf(z_test)

            
            CI = (round(pop_mean + z * sigma / np.sqrt(sample_size), 4), np.inf) #lower confidence bound
            

            df = pd.DataFrame({"Test Statistic": [z_test], "Critical Value": [z], "P-Value": [p_value], "alpha": [alpha],
                               "Non-rejection Interval for sample mean": [CI],
                               "Non-rejection Region for test statistic": [(round(z, 4), np.inf)],}) 
            df = df.round(4)
            df = df.transpose()

            # Create both subplots side by side
            fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))

            # ===== First Plot (Population Mean Distribution) =====
            x = np.linspace(-4, 4, 500)
            y = norm.pdf(x, 0, 1)
            y1 = np.zeros(500)

            ax1.plot(x, y)
            ax1.plot(z, 0, 'ro', label = f'Critical Value = {round(z, 4)}')
    
            ax1.plot(z_test, 0, 'bo', label = f'Test Statistic = {round(z_test, 4)}')
            ax1.plot(x, y1)

            # Fill rejection regions
            x_fill_left = np.linspace(-4, z, 500)
            y_fill_left = norm.pdf(x_fill_left, 0, 1)

            ax1.fill_between(x_fill_left, y_fill_left, color='skyblue', alpha=0.6)

            ax1.axvline(z, color='red', linestyle='--')
            
            ax1.text(z - 0.15, 0.12, 'Reject $H_0$', fontsize=10, color='red', ha='right')
            ax1.text(z + 0.15, 0.12, 'Do Not Reject $H_0$', fontsize=10, color='red', ha='left')

            ax1.set_title('Rejection/Non-rejection Region')
            ax1.set_xticks([z, 0])
            ax1.set_xlabel('$z$ Values')
            ax1.legend(loc = "upper right")

            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)
        elif test_type == "right-tailed":
            z = norm.ppf(1-alpha)
            p_value = 1 - norm.cdf(z_test)
            
            CI = (- np.inf, round(pop_mean - z * sigma / np.sqrt(sample_size), 4)) #upper confidence bound
            

            df = pd.DataFrame({"Test Statistic": [z_test], "Critical Value": [z], "P-Value": [p_value], "alpha": [alpha],
                               "Non-rejection Interval for sample mean": [CI],
                               "Non-rejection Region for test statistic": [(-np.inf, round(z, 4))],}) 
            df = df.round(4)
            df = df.transpose()

            # Create both subplots side by side
            fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))

            # ===== First Plot (Population Mean Distribution) =====
            x = np.linspace(-4, 4, 500)
            y = norm.pdf(x, 0, 1)
            y1 = np.zeros(500)

            ax1.plot(x, y)
            ax1.plot(z, 0, 'ro', label = f'Critical Value = {round(z, 4)}')
    
            ax1.plot(z_test, 0, 'bo', label = f'Test Statistic = {round(z_test, 4)}')
            ax1.plot(x, y1)

            # Fill rejection regions
            x_fill_left = np.linspace(z,4, 500)
            y_fill_left = norm.pdf(x_fill_left, 0, 1)

            ax1.fill_between(x_fill_left, y_fill_left, color='skyblue', alpha=0.6)

            ax1.axvline(z, color='red', linestyle='--')
            
            ax1.text(z - 0.15, 0.12, ' Do Not Reject $H_0$', fontsize=10, color='red', ha='right')
            ax1.text(z + 0.15, 0.12, 'Reject $H_0$', fontsize=10, color='red', ha='left')

            ax1.set_title('Rejection/Non-rejection Region')
            ax1.set_xticks([0, z])
            ax1.set_xlabel('$z$ Values')
            ax1.legend(loc = "upper right")

           
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)

    except Exception as e:
        error = f"Error: {e}"

    return jsonify({'image': encoded, 'error': error, 'df': df.to_html(classes='fancy-table') if df is not None else None})




# To calculate sample size for given margin of error when sigma is known
@populationmean_bp.route("/calculate_sample_size_known", methods=["GET", "POST"])
def calculate_sample_size_known():
    sample_size = None
    error = None
    sigma = None
    alpha = None
    margin_of_error = None
    if request.method == 'GET':
        return render_template('popmean_sigmaknown.html')
    try:
        sigma = float(request.form['sigma'])
        alpha = float(request.form['alpha'])
        margin_of_error = float(request.form['me'])

        z_score = norm.ppf((1 - alpha/2))
        sample_size = ( (z_score * sigma) / margin_of_error ) ** 2
        sample_size = math.ceil(sample_size)
    except Exception as e:
        sample_size = f"Error: {e}"

    return jsonify({'sample_size': sample_size, 'error': error, 'sigma': sigma, 'alpha': alpha, 'me': margin_of_error})





#****************************************************************************************************************************
# Population Mean when sigma is unknown
@populationmean_bp.route("/calculate_ci_unknown", methods=["GET", "POST"])
def calculate_ci_unknown():
    ci_result = None
    encoded = None
    margin_of_error = None
    if request.method == 'GET':
        return render_template('popmean_sigmaunknown.html')
    try:
        mu0 = float(request.form['sample_mean'])
        sigma = float(request.form['sample_std'])
        alpha = float(request.form['alpha'])
        n = int(request.form['n'])
        df = int(request.form['df'])

        t_score = t.ppf((1 - alpha/2), df)
        margin_of_error = t_score * (sigma / np.sqrt(n))
        lower_bound = mu0 - margin_of_error
        upper_bound = mu0 + margin_of_error

        ci_result = (round(lower_bound, 4), round(upper_bound, 4))
        
        # Plotting the confidence interval
        fig, ax = plt.subplots()
        x = np.linspace(lower_bound, upper_bound, 500)
        y = np.zeros(len(x))
        y1 = t.pdf(x, df, mu0, sigma/np.sqrt(n))
        #ax.plot(x, y1, 'b-')
        ax.plot(x, y, 'b-')
        ax.scatter(lower_bound, 0, color='red', alpha=0.99, label=f'Lower Bound = {round(lower_bound, 4)}')
        ax.scatter(upper_bound, 0, color='red', alpha=0.99, label=f'Upper Bound = {round(upper_bound, 4)}')
        ax.scatter(mu0, 0, color='green', alpha=0.99, label=f'Sample Mean (x̄) = {round(mu0, 4)}')
        #ax.fill_between(x, y1, where=(x >= lower_bound) & (x <= upper_bound), color='skyblue', alpha=0.3)
        ax.fill_between(x, y, color='skyblue', alpha=0.5)
        ax.set_title('Confidence Interval for Population Mean, σ unknown')
        ax.set_xlabel('Values')
        plt.legend()
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
    except Exception as e:
        ci_result = f"Error: {e}"

    return jsonify({'ci_result': ci_result, 'plot': encoded, "me": margin_of_error})





@populationmean_bp.route("/sigmaunknown", methods=["GET", "POST"])
def sigmaunknown():
    encoded = None
    DF = None
    error = None
    if request.method == 'GET':
        return render_template('popmean_sigmaunknown.html')
    try:
        sample_mean = float(request.form['sample_mean'])
        pop_mean = float(request.form['population_mean'])
        sigma = float(request.form['sample_std'])
        sample_size = int(request.form['n'])
        alpha = float(request.form['alpha'])       
        df = int(request.form['df'])
        test_type = request.form['test_type']
        t_test = (sample_mean-pop_mean)/(sigma/np.sqrt(sample_size))
        if test_type == "two-tailed":
            t_crit = t.isf(alpha/2, df)
            p_value = 2 * (1 - t.cdf(abs(t_test), df))
            CI = (round(pop_mean - t_crit * sigma / np.sqrt(sample_size), 4), round(pop_mean + t_crit * sigma / np.sqrt(sample_size), 4))


            DF = pd.DataFrame({"T Test Statistic": [t_test], "Critical T Value": [t_crit], "P-Value": [p_value], "alpha": [alpha],
                               "Sample Size":[sample_size], "Deg of Freedom":[df],
                               "Non-rejection Interval for sample mean": [CI],
                               "Non-rejection Region for test statistic": [(-round(t_crit, 4), round(t_crit, 4))],})
            DF = DF.round(4)
            DF = DF.transpose()
            
            fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))
    
            # ===== First Plot (Population Mean Distribution) =====
            x = np.linspace(-4, 4, 500)
            y = t.pdf(x, df)
            y1 = np.zeros(500)

            ax1.plot(x, y)
            ax1.plot(-t_crit, 0, 'ro', label = 'Critical Value')
            ax1.plot(t_crit, 0, 'ro', label = 'Critical Value')
            ax1.plot(t_test, 0, 'bo', label = 'T Test Statistic')
            ax1.plot(x, y1)


            # Fill rejection regions
            x_fill_left = np.linspace(-4, - t_crit, 500)
            y_fill_left = t.pdf(x_fill_left, df)

            x_fill_right = np.linspace(t_crit, 4, 500)
            y_fill_right = t.pdf(x_fill_right, df)

            ax1.fill_between(x_fill_left, y_fill_left, color='skyblue', alpha=0.6)
            ax1.fill_between(x_fill_right, y_fill_right, color='skyblue', alpha=0.6)

            ax1.axvline(-t_crit, color='red', linestyle='--')
            ax1.axvline(t_crit, color='red', linestyle='--')

            ax1.text(0, 0.1, 'Do Not Reject $H_0$', fontsize=10, color='red', ha='center')
            ax1.text(- t_crit - 0.1, 0.1, 'Reject $H_0$', fontsize=10, color='red', ha='right')
            ax1.text(t_crit + 0.1, 0.1, 'Reject $H_0$', fontsize=10, color='red', ha='left')

            ax1.set_title('Rejection/Non-rejection Region')
            ax1.set_xticks([-t_crit, 0, t_crit])
            ax1.set_xlabel('$t$ Values')
            ax1.legend()

            # Save the combined figure
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)

        elif test_type == "left-tailed":
            t_crit = t.ppf(alpha, df)
            p_value = t.cdf(t_test, df)

            
            CI = (round(pop_mean - t_crit * sigma / np.sqrt(sample_size), 4), np.inf) #upper confidence bound
            # Create dataframe
            DF = pd.DataFrame({"T Test Statistic": [t_test], "Critical T Value": [t_crit], "P-Value": [p_value], "alpha": [alpha],
                               "Non-rejection Interval for sample mean": [CI],
                               "Non-rejection Region for test statistic": [(round(t_crit, 4), np.inf)],})
            
            DF = DF.round(4)
            DF = DF.transpose()
            
            # Create both subplots side by side
            fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))

            # ===== First Plot (Population Mean Distribution) =====
            x = np.linspace(-4, 4, 500)
            y = t.pdf(x, df)
            y1 = np.zeros(500)

            ax1.plot(x, y)
            ax1.plot(t_crit, 0, 'ro', label = 'Critical Value')
    
            ax1.plot(t_test, 0, 'bo', label = 't Test Statistic')
            ax1.plot(x, y1)

            # Fill rejection regions
            x_fill_left = np.linspace(-4, t_crit, 500)
            y_fill_left = t.pdf(x_fill_left, df)

            ax1.fill_between(x_fill_left, y_fill_left, color='skyblue', alpha=0.6)

            ax1.axvline(t_crit, color='red', linestyle='--')

            ax1.text(t_crit - 0.15, 0.12, 'Reject $H_0$', fontsize=10, color='red', ha='right')
            ax1.text(t_crit + 0.15, 0.12, 'Do Not Reject $H_0$', fontsize=10, color='red', ha='left')

            ax1.set_title('Rejection/Non-rejection Region')
            ax1.set_xticks([t_crit, 0])
            ax1.set_xlabel('$t$ Values')
            ax1.legend()

            # Save the combined figure
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)
        elif test_type == "right-tailed":
            t_crit = t.ppf(1-alpha, df)
            p_value = 1 - t.cdf(t_test, df)
            
            CI = (-np.inf, round(pop_mean + t_crit * sigma / np.sqrt(sample_size), 4)) #upper confidence bound
            # Create dataframe
            DF = pd.DataFrame({"T Test Statistic": [t_test], "Critical T Value": [t_crit], "P-Value": [p_value], "alpha": [alpha],
                               "Non-rejection Interval for sample mean": [CI],
                               "Non-rejection Region for test statistic": [(-np.inf, round(t_crit, 4))],})
           
            DF = DF.round(4)
            DF = DF.transpose()
            
            # Create both subplots side by side
            fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))

            # ===== First Plot (Population Mean Distribution) =====
            x = np.linspace(-4, 4, 500)
            y = t.pdf(x, df)
            y1 = np.zeros(500)

            ax1.plot(x, y)
            ax1.plot(t_crit, 0, 'ro', label = 'Critical Value')

            ax1.plot(t_test, 0, 'bo', label = 't Test Statistic')
            ax1.plot(x, y1)

            # Fill rejection regions
            x_fill_left = np.linspace(t_crit, 4, 500)
            y_fill_left = t.pdf(x_fill_left, df)

            ax1.fill_between(x_fill_left, y_fill_left, color='skyblue', alpha=0.6)

            ax1.axvline(t_crit, color='red', linestyle='--')

            ax1.text(t_crit - 0.15, 0.12, ' Do Not Reject $H_0$', fontsize=10, color='red', ha='right')
            ax1.text(t_crit + 0.15, 0.12, 'Reject $H_0$', fontsize=10, color='red', ha='left')

            ax1.set_title('Rejection/Non-rejection Region')
            ax1.set_xticks([0, t_crit])
            ax1.set_xlabel('$t$ Values')
            ax1.legend()

            # Save the combined figure
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)

    except Exception as e:
        error = f"Error: {e}"

    return jsonify({'image': encoded, 'df': DF.to_html(classes='fancy-table') if DF is not None else None, "error": error})




#*********************************************************************************************************************************************  
# Comparing two means:

#CI for two means equal variances:
@populationmean_bp.route("/calculate_ci_popmean_varequal", methods = ["GET", "POST"])
def calculate_ci_popmean_varequal():
    error = None
    CI = None
    s_pooled = None
    ME = None
    t_crit = None
    if request.method == "GET":
        return render_template("diffpopmeans.html")
    try:
        mean1 = float(request.form['sample_mean1'])
        mean2 = float(request.form['sample_mean2'])
        size1 = int(request.form['sample_size1'])
        size2 = int(request.form['sample_size2'])
        std1 = float(request.form['sample_std1'])
        std2 = float(request.form['sample_std2'])
        alpha = float(request.form['alpha_ci'])
        df = int(request.form['DF'])
        t_crit = t.ppf(1-alpha/2, df)
        s_pooled = np.sqrt(((size1-1)*std1**2 + (size2-1)*std2**2)/(size1 + size2 -2))
        t_test = (mean1-mean2)/(s_pooled*np.sqrt(1/size1 + 1/size2))
        p_value = 2*(1-t.cdf(abs(t_test), df))
        ME = t_crit*s_pooled * np.sqrt(1/size1 + 1/size2)
        CI = (mean1 - mean2 - ME, mean1-mean2 + ME)
    except Exception as e:
        error = f"Error:{e}"
    return jsonify({"error": error, "CI":CI, "ME":ME, "t_alpha":t_crit, "sp":s_pooled})




@populationmean_bp.route("/twopopmeans_equalvar", methods=["GET", "POST"])
def twopopmeans():
    error = None
    test_type = None
    t_test = None
    p_value = None 
    margin_error = None
    alpha = None
    t_crit = None 
    if request.method == 'GET':
        return render_template("diffpopmeans.html")
    try:
        sample_mean1 = float(request.form['sample_mean1'])
        sample_mean2 = float(request.form['sample_mean2'])
        sample_size1 = int(request.form['sample_size1'])
        sample_size2 = int(request.form['sample_size2'])
        sigma1 = float(request.form['sample_std1'])
        sigma2 = float(request.form['sample_std2'])
        alpha = float(request.form['alpha'])
        df = int(request.form['DF'])
        test_type = request.form['type']
        s_pooled = np.sqrt(((sample_size1 - 1) * sigma1**2 + (sample_size2 - 1) * sigma2**2) / (sample_size1 + sample_size2 - 2))
        t_test = (sample_mean1 - sample_mean2) / (s_pooled * np.sqrt(1 / sample_size1 + 1 / sample_size2))
        if test_type == "two-tailed":
            t_crit = t.ppf(1 - alpha / 2, df)
            p_value = 2 * (1 - t.cdf(abs(t_test), df))
            margin_error = t_crit * s_pooled * np.sqrt(1 / sample_size1 + 1 / sample_size2)
                      
            fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))

            # ===== First Plot (Population Mean Distribution) =====
            x = np.linspace(-4, 4, 500)
            y = t.pdf(x, df)
            y1 = np.zeros(500)

            ax1.plot(x, y)
            ax1.plot(-t_crit, 0, 'ro', label = r'$t_{\text{crit}}$')
            ax1.plot(t_crit, 0, 'ro', label = r'$t_{\text{crit}}$')
            ax1.plot(t_test, 0, 'bo', label = r'$t_{\text{test}}$')
            ax1.plot(x, y1)


            # Fill rejection regions
            x_fill_left = np.linspace(-4, - t_crit, 500)
            y_fill_left = t.pdf(x_fill_left, df)

            x_fill_right = np.linspace(t_crit, 4, 500)
            y_fill_right = t.pdf(x_fill_right, df)

            ax1.fill_between(x_fill_left, y_fill_left, color='skyblue', alpha=0.6)
            ax1.fill_between(x_fill_right, y_fill_right, color='skyblue', alpha=0.6)

            ax1.axvline(-t_crit, color='red', linestyle='--')
            ax1.axvline(t_crit, color='red', linestyle='--')

            ax1.text(0, 0.1, 'Do Not Reject $H_0$', fontsize=10, color='red', ha='center')
            ax1.text(- t_crit - 0.1, 0.1, 'Reject $H_0$', fontsize=10, color='red', ha='right')
            ax1.text(t_crit + 0.1, 0.1, 'Reject $H_0$', fontsize=10, color='red', ha='left')

            ax1.set_title('Rejection/Non-rejection Region')
            ax1.set_xticks([-t_crit, 0, t_crit])
            ax1.set_xlabel('$t$ value')
            ax1.legend()

            # Save the combined figure
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)

        elif test_type == "left-tailed":
            t_crit = t.ppf(alpha, df)
            p_value = t.cdf(t_test, df)
            margin_error = t_crit * s_pooled * np.sqrt(1 / sample_size1 + 1 / sample_size2)
            
            # Create both subplots side by side
            fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))

            # ===== First Plot (Population Mean Distribution) =====
            x = np.linspace(-4, 4, 500)
            y = t.pdf(x, df)
            y1 = np.zeros(500)

            ax1.plot(x, y)
            ax1.plot(t_crit, 0, 'ro', label = r'$t_{\text{crit}}$')
    
            ax1.plot(t_test, 0, 'bo', label = r'$t_{\text{test}}$')
            ax1.plot(x, y1)

            # Fill rejection regions
            x_fill_left = np.linspace(-4, t_crit, 500)
            y_fill_left = t.pdf(x_fill_left, df)

            ax1.fill_between(x_fill_left, y_fill_left, color='skyblue', alpha=0.6)

            ax1.axvline(t_crit, color='red', linestyle='--')

            ax1.text(t_crit - 0.15, 0.12, 'Reject $H_0$', fontsize=10, color='red', ha='right')
            ax1.text(t_crit + 0.15, 0.12, 'Do Not Reject $H_0$', fontsize=10, color='red', ha='left')

            ax1.set_title('Rejection/Non-rejection Region')
            ax1.set_xticks([t_crit, 0])
            ax1.set_xlabel('$t$ value')
            ax1.legend()

            # Save the combined figure
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)
        elif test_type == "right-tailed":
            t_crit = t.ppf(1-alpha, df)
            p_value = 1 - t.cdf(t_test, df)
            margin_error = t_crit * s_pooled * np.sqrt(1 / sample_size1 + 1 / sample_size2)
            

            # Create both subplots side by side
            fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))

            # ===== First Plot (Population Mean Distribution) =====
            x = np.linspace(-4, 4, 500)
            y = t.pdf(x, df)
            y1 = np.zeros(500)

            ax1.plot(x, y)
            ax1.plot(t_crit, 0, 'ro', label = r'$t_{\text{crit}}$')

            ax1.plot(t_test, 0, 'bo', label = r'$t_{\text{test}}$')
            ax1.plot(x, y1)

            # Fill rejection regions
            x_fill_left = np.linspace(t_crit, 4, 500)
            y_fill_left = t.pdf(x_fill_left, df)

            ax1.fill_between(x_fill_left, y_fill_left, color='skyblue', alpha=0.6)

            ax1.axvline(t_crit, color='red', linestyle='--')

            ax1.text(t_crit - 0.15, 0.12, ' Do Not Reject $H_0$', fontsize=10, color='red', ha='right')
            ax1.text(t_crit + 0.15, 0.12, 'Reject $H_0$', fontsize=10, color='red', ha='left')

            ax1.set_title('Rejection/Non-rejection Region')
            ax1.set_xticks([0, t_crit])
            ax1.set_xlabel('$t$ value')
            ax1.legend()

            # Save the combined figure
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)

    except Exception as e:
        error = f"Error: {e}"

    return jsonify({"p_value":p_value, "t_crit":t_crit, "t_test":t_test, "alpha":alpha, "error":error, "image":encoded, "test_type":test_type})






#**********************************************************************************************************************************
#comparing two means: unequal variances

@populationmean_bp.route("/calculate_ci_popmean_varunequal", methods=["GET", "POST"])
def calculate_ci_popmean_varunequal():
    error = None
    CI = None
    ME = None
    t_crit = None
    df = None

    if request.method == "GET":
        return render_template("diffpopmeans_unequalvar.html")

    try:
        mean1 = float(request.form['sample_mean1'])
        mean2 = float(request.form['sample_mean2'])
        size1 = int(request.form['sample_size1'])
        size2 = int(request.form['sample_size2'])
        std1 = float(request.form['sample_std1'])
        std2 = float(request.form['sample_std2'])
        alpha = float(request.form['alpha_ci'])

        if size1 < 2 or size2 < 2:
            raise ValueError("Sample sizes must be at least 2")
        if std1 <= 0 or std2 <= 0:
            raise ValueError("Standard deviations must be positive")

        # Welch df
        df = ((std1**2/size1 + std2**2/size2)**2) / (
            ((std1**2/size1)**2)/(size1-1) +
            ((std2**2/size2)**2)/(size2-1)
        )
        df = math.floor(df)

        # Critical t
        t_crit = t.ppf(1 - alpha/2, df)

        # Margin of error
        ME = t_crit * np.sqrt(std1**2/size1 + std2**2/size2)

        # CI
        CI = (mean1 - mean2 - ME, mean1 - mean2 + ME)

    except Exception as e:
        error = f"Error: {e}"

    return jsonify({
        "error": error,
        "CI": CI,
        "ME": ME,
        "t_alpha": t_crit,
        "DF": df
    })















@populationmean_bp.route("/twopopmeans_unequalvar", methods=["GET", "POST"])
def diffpopmeans_unequalvar():
    encoded = None 
    test_type = None
    CI = None
    df = None
    alpha = None
    margin_error = None
    t_test = None
    t_crit = None 
    error  = None

    if request.method == 'GET':
        return render_template('diffpopmeans_unequalvar.html')

    try:
        sample_mean1 = float(request.form['sample_mean1'])
        sample_mean2 = float(request.form['sample_mean2'])
        sample_size1 = int(request.form['sample_size1'])
        sample_size2 = int(request.form['sample_size2'])
        
        sigma1 = float(request.form['sample_std1'])
        sigma2 = float(request.form['sample_std2'])
        alpha = float(request.form['alpha'])
        test_type = request.form['type']

        if sample_size1 < 2 or sample_size2 < 2:
            raise ValueError("Sample sizes must be at least 2")
        if sigma1 <= 0 or sigma2 <= 0:
            raise ValueError("Standard deviations must be positive")

        df = ( (sigma1**2/sample_size1 + sigma2**2/sample_size2)**2 ) / ( ((sigma1**2/sample_size1)**2)/(sample_size1-1) + ((sigma2**2/sample_size2)**2)/(sample_size2-1) )
        df = math.floor(df)
        t_test = (sample_mean1 - sample_mean2) / np.sqrt(sigma1**2 / sample_size1 + sigma2**2 / sample_size2)
        if test_type == "two-tailed":
            t_crit = t.ppf(1 - alpha / 2, df)
            p_value = 2 * (1 - t.cdf(abs(t_test), df))
            margin_error = t_crit * np.sqrt(sigma1**2 / sample_size1 + sigma2**2 / sample_size2)
            CI = (sample_mean1 - sample_mean2 - margin_error, sample_mean1 - sample_mean2 + margin_error)

            fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))

            # ===== First Plot (Population Mean Distribution) =====
            x = np.linspace(-4, 4, 500)
            y = t.pdf(x, df)
            y1 = np.zeros(500)

            ax1.plot(x, y)
            ax1.plot(-t_crit, 0, 'ro', label = r'$t_{\text{crit}}$')
            ax1.plot(t_crit, 0, 'ro', label = r'$t_{\text{crit}}$')
            ax1.plot(t_test, 0, 'bo', label = r'$t_{\text{test}}$')
            ax1.plot(x, y1)


            # Fill rejection regions
            x_fill_left = np.linspace(-4, - t_crit, 500)
            y_fill_left = t.pdf(x_fill_left, df)

            x_fill_right = np.linspace(t_crit, 4, 500)
            y_fill_right = t.pdf(x_fill_right, df)

            ax1.fill_between(x_fill_left, y_fill_left, color='skyblue', alpha=0.6)
            ax1.fill_between(x_fill_right, y_fill_right, color='skyblue', alpha=0.6)

            ax1.axvline(-t_crit, color='red', linestyle='--')
            ax1.axvline(t_crit, color='red', linestyle='--')

            ax1.text(0, 0.1, 'Do Not Reject $H_0$', fontsize=10, color='red', ha='center')
            ax1.text(- t_crit - 0.1, 0.1, 'Reject $H_0$', fontsize=10, color='red', ha='right')
            ax1.text(t_crit + 0.1, 0.1, 'Reject $H_0$', fontsize=10, color='red', ha='left')

            ax1.set_title('Rejection/Non-rejection Region')
            ax1.set_xticks([-t_crit, 0, t_crit])
            ax1.set_xlabel('$t$ Values')
            ax1.legend()

            # Save the combined figure
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)

        elif test_type == "left-tailed":
            t_crit = t.ppf(alpha, df)
            p_value = t.cdf(t_test, df)

            margin_error = t_crit *  np.sqrt(sigma1**2 / sample_size1 + sigma2**2 / sample_size2)
            CI = (None, sample_mean1 - sample_mean2 + margin_error) #upper confidence bound

            # Create both subplots side by side
            fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))

            # ===== First Plot (Population Mean Distribution) =====
            x = np.linspace(-4, 4, 500)
            y = t.pdf(x, df)
            y1 = np.zeros(500)

            ax1.plot(x, y)
            ax1.plot(t_crit, 0, 'ro', label = r'$t_{\text{crit}}$')
    
            ax1.plot(t_test, 0, 'bo', label = r'$t_{\text{test}}$')
            ax1.plot(x, y1)

            # Fill rejection regions
            x_fill_left = np.linspace(-4, t_crit, 500)
            y_fill_left = t.pdf(x_fill_left, df)

            ax1.fill_between(x_fill_left, y_fill_left, color='skyblue', alpha=0.6)

            ax1.axvline(t_crit, color='red', linestyle='--')

            ax1.text(t_crit - 0.15, 0.12, 'Reject $H_0$', fontsize=10, color='red', ha='right')
            ax1.text(t_crit + 0.15, 0.12, 'Do Not Reject $H_0$', fontsize=10, color='red', ha='left')

            ax1.set_title('Rejection/Non-rejection Region')
            ax1.set_xticks([t_crit, 0])
            ax1.set_xlabel('$t$ Values')
            ax1.legend()

            # Save the combined figure
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)
        elif test_type == "right-tailed":
            t_crit = t.ppf(1-alpha, df)
            p_value = 1 - t.cdf(t_test, df)
            margin_error = t_crit * np.sqrt(sigma1**2 / sample_size1 + sigma2**2 / sample_size2)
            CI = (sample_mean1 - sample_mean2 - margin_error, None)

            # Create both subplots side by side
            fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))

            # ===== First Plot (Population Mean Distribution) =====
            x = np.linspace(-4, 4, 500)
            y = t.pdf(x, df)
            y1 = np.zeros(500)

            ax1.plot(x, y)
            ax1.plot(t_crit, 0, 'ro', label = r'$t_{\text{crit}}$')

            ax1.plot(t_test, 0, 'bo', label = r'$t_{\text{test}}$')
            ax1.plot(x, y1)

            # Fill rejection regions
            x_fill_left = np.linspace(t_crit, 4, 500)
            y_fill_left = t.pdf(x_fill_left, df)

            ax1.fill_between(x_fill_left, y_fill_left, color='skyblue', alpha=0.6)

            ax1.axvline(t_crit, color='red', linestyle='--')

            ax1.text(t_crit - 0.15, 0.12, ' Do Not Reject $H_0$', fontsize=10, color='red', ha='right')
            ax1.text(t_crit + 0.15, 0.12, 'Reject $H_0$', fontsize=10, color='red', ha='left')

            ax1.set_title('Rejection/Non-rejection Region')
            ax1.set_xticks([0, t_crit])
            ax1.set_xlabel('$t$ Values')
            ax1.legend()

            # Save the combined figure
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)

    except Exception as e:
        error = f"Error: {e}"

    return jsonify({"image":encoded, "DF":df, "statistic":t_test, "alpha":alpha,
                    "critical_value":t_crit, "pvalue":p_value, "error":error, 
                    "test_type":test_type})