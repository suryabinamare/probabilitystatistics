from flask import Flask, request, Blueprint, render_template, current_app, jsonify
import os
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import f
from scipy.stats import norm
from scipy.stats import t
from scipy.stats import chi2
from werkzeug.utils import secure_filename
import io
import base64


populationproportion_bp = Blueprint("populationproportion", __name__)

@populationproportion_bp.route("/calculate_ci_proportion1", methods=["GET", "POST"])
def confidence_interval():

    if request.method == 'GET':
        return render_template("popproportion_CI.html")

    try:
        p_hat = float(request.form["proportion"])
        n = int(request.form["sample_size"])
        alpha = float(request.form["alpha"])

        if not (0 < p_hat < 1):
            return jsonify({"error": "Proportion must be between 0 and 1"}), 400
        if n <= 0:
            return jsonify({"error": "Sample size must be positive"}), 400

        z_alpha = norm.ppf(1 - alpha / 2)
        me = z_alpha * np.sqrt((p_hat * (1 - p_hat)) / n)
        CI = (round(p_hat - me, 4), round(p_hat + me, 4))

        fig, ax = plt.subplots(figsize=(5, 3))

        ax.hlines(0, CI[0], CI[1])
        ax.scatter(CI[0], 0, color='red', label= f"Lower Bound = {CI[0]:.4f}")
        ax.scatter(CI[1], 0, color='red', label=f"Upper Bound = {CI[1]:.4f}")
        ax.scatter(p_hat, 0, color='blue', label=f"Sample Proportion = {p_hat:.4f}")

        ax.set_title("CI for Population Proportion")
        ax.set_yticks([])
        ax.legend()
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)

        return jsonify({
            "CI": CI,
            "ME": round(me, 4),
            "z_alpha": round(z_alpha, 4),
            "image": encoded
        })

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid input values"}), 400









#Calculate sample size for one population proportion
@populationproportion_bp.route("/calculate_n", methods=["GET", "POST"])
def calculate_n():
    if request.method == 'GET':
        return render_template("popproportion_CI.html")
    try:
        me = float(request.form["me"])
        p_hat = float(request.form["p_hat"])
        alpha = float(request.form["alpha"])
        z_alpha = norm.ppf(1 - alpha / 2)
        n = (z_alpha**2 * p_hat * (1 - p_hat)) / (me**2)
        return jsonify({"sample_size": int(np.ceil(n)), "z_alpha": round(z_alpha, 4)})
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid input values"}), 400




# Hypothesis Testing for one Population Proportion
@populationproportion_bp.route("/proportion1_ht", methods=["GET", "POST"])
def proportion1():
    z = None
    p_value = None
    test_type = None
    z_alpha = None
    p_0 = None
    p_hat = None
    alpha = None
    n = None
    encoded = None
    
    try:       
        n = int(request.form['sample_size'])
        p_hat = float(request.form['sample_proportion'])
        p_0 = float(request.form['null_prop'])
        alpha = float(request.form['alpha'])
        test_type = request.form['test_type']

        if test_type == "two-tailed":
            # Perform two-tailed test
            z = (p_hat - p_0) / np.sqrt((p_0 * (1 - p_0)) / n)
            z_alpha = norm.ppf(1 - alpha / 2)
            p_value = 2 * (1 - norm.cdf(abs(z)))
            # Create both subplots side by side
            fig, ax2 = plt.subplots(1, 1, figsize=(6, 4))


            # ===== Second Plot (Standard Normal Distribution) =====
            x1 = np.linspace(-3, 3, 500)
            y1 = norm.pdf(x1, loc=0, scale=1)
            y2 = np.zeros(500)

            ax2.plot(x1, y1)
            ax2.plot(x1, y2)
            ax2.plot(-z_alpha, 0, 'ro', label = f'crit_val = {-z_alpha:.2f}')
            ax2.plot(z_alpha, 0, 'ro', label = f'crit_val = {z_alpha:.2f}')
            ax2.plot(z, 0, 'go', label = f'test statistic:z = {z:.2f}')

            # Shade rejection regions
            x_fill_left1 = np.linspace(-z_alpha, -3, 500)
            y_fill_left1 = norm.pdf(x_fill_left1, loc=0, scale=1)

            x_fill_right1 = np.linspace(z_alpha, 3, 500)
            y_fill_right1 = norm.pdf(x_fill_right1, loc=0, scale=1)

            ax2.fill_between(x_fill_left1, y_fill_left1, color='skyblue', alpha=0.6)
            ax2.fill_between(x_fill_right1, y_fill_right1, color='skyblue', alpha=0.6)

            ax2.axvline(-z_alpha, color='red', linestyle='--')
            ax2.axvline(z_alpha, color='red', linestyle='--')

            ax2.text(0, 0.1, 'Do Not Reject $H_0$', fontsize=10, color='red', ha='center')
            ax2.text(-z_alpha - 0.1, 0.1, 'Reject $H_0$', fontsize=10, color='red', ha='right')
            ax2.text(z_alpha + 0.1, 0.1, 'Reject $H_0$', fontsize=10, color='red', ha='left')

            ax2.set_title('Standard Normal Distribution')
            ax2.set_xticks([-z_alpha, 0, z_alpha])
            ax2.set_xlabel('$z$ Values')
            ax2.legend(loc = 'upper right')

            # Save the combined figure
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)
        
            

        elif test_type == "left-tailed":
            # Perform left-tailed test
            z = (p_hat - p_0) / np.sqrt((p_0 * (1 - p_0)) / n)
            z_alpha = norm.ppf(alpha)
            p_value = norm.cdf(z)
            # Create both subplots side by side
            fig, ax2 = plt.subplots(1, 1, figsize=(6, 4))


            # ===== Second Plot (Standard Normal Distribution) =====
            x1 = np.linspace(-3, 3, 500)
            y1 = norm.pdf(x1, loc=0, scale=1)
            y2 = np.zeros(500)

            ax2.plot(x1, y1)
            ax2.plot(x1, y2)
            ax2.plot(z_alpha, 0, 'ro', label = f'crit_val = {z_alpha:.2f}')
            ax2.plot(z, 0, 'go', label = f'test statistic:z = {z:.2f}')
        

            # Shade rejection regions
            x_fill_left1 = np.linspace(-3, z_alpha, 500)
            y_fill_left1 = norm.pdf(x_fill_left1, loc=0, scale=1)


            ax2.fill_between(x_fill_left1, y_fill_left1, color='skyblue', alpha=0.6)
        

            ax2.axvline(z_alpha, color='red', linestyle='--')


            ax2.text(z_alpha - 0.1, 0.1, 'Reject $H_0$', fontsize=10, color='red', ha='right')
            ax2.text(z_alpha + 0.1, 0.1, 'Do not Reject $H_0$', fontsize=10, color='red', ha='left')

            ax2.set_title('Standard Normal Distribution')
            ax2.set_xticks([z_alpha, 0, -z_alpha])
            ax2.set_xlabel('$z$ Values')
            ax2.legend()

            # Save the combined figure
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)
            
        elif test_type == "right-tailed":
            # Perform right-tailed test
            z = (p_hat - p_0) / np.sqrt((p_0 * (1 - p_0)) / n)
            z_alpha = norm.ppf(1 - alpha)
            p_value = 1 - norm.cdf(z)
            # Create both subplots side by side
            fig, ax2 = plt.subplots(1, 1, figsize=(6, 4))

            # ===== Second Plot (Standard Normal Distribution) =====
            x1 = np.linspace(-3, 3, 500)
            y1 = norm.pdf(x1, loc=0, scale=1)
            y2 = np.zeros(500)

            ax2.plot(x1, y1)
            ax2.plot(x1, y2)
            ax2.plot(z_alpha, 0, 'ro', label = f'crit_val = {z_alpha:.2f}')
            ax2.plot(z, 0, 'go', label = f'test statistic:z = {z:.2f}')

            # Shade rejection regions
            x_fill_left1 = np.linspace(z_alpha,3, 500)
            y_fill_left1 = norm.pdf(x_fill_left1, loc=0, scale=1)

            ax2.fill_between(x_fill_left1, y_fill_left1, color='skyblue', alpha=0.6)

            ax2.axvline(z_alpha, color='red', linestyle='--')

            ax2.text(z_alpha - 0.1, 0.1, 'Do not Reject $H_0$', fontsize=10, color='red', ha='right')
            ax2.text(z_alpha + 0.1, 0.1, 'Reject $H_0$', fontsize=10, color='red', ha='left')

            ax2.set_title('Standard Normal Distribution')
            ax2.set_xticks([-z_alpha, 0, z_alpha])
            ax2.set_xlabel('$z$ Values')
            ax2.legend()

           # Save the combined figure
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)
    except ValueError:
        return "Invalid input. Please enter valid numbers."
    return jsonify({"z": round(z, 4),
                    "p_value": round(p_value, 4),
                    "z_alpha": round(z_alpha, 4),
                    "alpha": alpha,
                    "image": encoded})











# Confidence Intervals for two Population Proportions
@populationproportion_bp.route("/calculate_ci_twoprop", methods=["GET", "POST"])
def confidence_interval_two():
    margin_of_error = None
    z_alpha = None
    p1_hat = None
    p2_hat = None
    encoded = None
    alpha = None
    standard_error = None
    if request.method == 'GET':
        return render_template("popproportion_CI2.html")
    try:
        p1_hat = float(request.form.get('p1'))
        p2_hat = float(request.form.get('p2'))
        n1 = int(request.form.get('n1'))
        n2 = int(request.form.get('n2'))
        alpha = float(request.form.get('alpha'))
        z_alpha = norm.ppf(1 - alpha / 2)
        standard_error = np.sqrt((p1_hat * (1 - p1_hat)) / n1 + (p2_hat * (1 - p2_hat)) / n2)
        margin_of_error = z_alpha * standard_error
        ci_lower = (p1_hat - p2_hat) - margin_of_error
        ci_upper = (p1_hat - p2_hat) + margin_of_error
        CI = (round(ci_lower, 4), round(ci_upper, 4))


        fig, ax = plt.subplots(figsize=(5, 3))
        ax.hlines(0, CI[0], CI[1])
        ax.scatter(CI[0], 0, color='red', label= f"Lower Bound = {CI[0]}")
        ax.scatter(CI[1], 0, color='red', label=f"Upper Bound = {CI[1]}")
        ax.scatter(p1_hat - p2_hat, 0, color='blue', label=f"$\hat{{p}}_1 - \hat{{p}}_2$ = {p1_hat - p2_hat:.4f}")

        ax.set_title("CI for Population Proportion")
        ax.set_yticks([])
        ax.legend()
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
        return jsonify({"CI": CI, "ME": round(margin_of_error, 4), "z_alpha": round(z_alpha, 4), "image": encoded})
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid input values"}), 400





@populationproportion_bp.route("/calculate_ht_twoprop", methods=["GET", "POST"])
def proportion2():
    z = None
    p_value = None
    test_type = None
    z_alpha = None
    alpha = None
    p_hat1 = None
    p_hat2 = None   
    n1 = None
    n2 = None
    p = None
    encoded = None
    if request.method == 'GET':
        return render_template("popproportion_CI2.html")
    try:
        n1 = int(request.form.get('n1'))
        n2 = int(request.form.get('n2'))
        p1_hat = float(request.form.get('p1'))
        p2_hat = float(request.form.get('p2'))
        alpha = float(request.form.get('alpha'))
      
        test_type = request.form.get('test_type')
        p = (
            n1*p1_hat + n2*p2_hat) / (n1 + n2)
        z = (p1_hat - p2_hat) / np.sqrt(p * (1 - p) * (1/n1 + 1/n2))

        if test_type == "two-tailed":
            # Perform two-tailed test
            z_alpha = norm.ppf(1 - alpha / 2)
            p_value = 2 * (1 - norm.cdf(abs(z)))

            # Create plots:
            fig, ax2 = plt.subplots(1, 1, figsize=(6, 4))
            x = np.linspace(-3, 3, 500)
            y = norm.pdf(x, loc=0, scale=1)
            y1 = np.zeros(500)

            ax2.plot(x, y)
            ax2.plot(-z_alpha, 0, 'ro', label = 'Critical Value')
            ax2.plot(z_alpha, 0, 'ro', label = 'Critical Value')
            ax2.plot(z, 0, 'go', label = 'Test Statistic')
            ax2.plot(x, y1)

            # Shade rejection regions
            x_fill_left1 = np.linspace(-z_alpha, -3, 500)
            y_fill_left1 = norm.pdf(x_fill_left1, loc=0, scale=1)

            x_fill_right1 = np.linspace(z_alpha, 3, 500)
            y_fill_right1 = norm.pdf(x_fill_right1, loc=0, scale=1)

            ax2.fill_between(x_fill_left1, y_fill_left1, color='skyblue', alpha=0.6)
            ax2.fill_between(x_fill_right1, y_fill_right1, color='skyblue', alpha=0.6)

            ax2.axvline(-z_alpha, color='red', linestyle='--')
            ax2.axvline(z_alpha, color='red', linestyle='--')

            ax2.text(0, 0.1, 'Do Not Reject $H_0$', fontsize=10, color='red', ha='center')
            ax2.text(-z_alpha - 0.1, 0.1, 'Reject $H_0$', fontsize=10, color='red', ha='right')
            ax2.text(z_alpha + 0.1, 0.1, 'Reject $H_0$', fontsize=10, color='red', ha='left')

            ax2.set_title('Standard Normal Distribution')
            ax2.set_xticks([-z_alpha, 0, z_alpha])
            ax2.set_xlabel('$z$ Values')
            ax2.legend()

            # Save the combined figure
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)
        elif test_type == "left-tailed":
            # Perform left-tailed test
            z_alpha = norm.ppf(alpha)
            p_value = norm.cdf(z)
            # Create both subplots side by side
            fig, ax2 = plt.subplots(1, 1, figsize=(6, 4))


            # ===== Second Plot (Standard Normal Distribution) =====
            x = np.linspace(-3, 3, 500)
            y = norm.pdf(x, loc=0, scale=1)
            y2 = np.zeros(500)

            ax2.plot(x, y)
            ax2.plot(z_alpha, 0, 'ro', label = 'Critical Value')
            ax2.plot(z, 0, 'go', label = 'Test Statistic')
            ax2.plot(x, y2)

            # Shade rejection regions
            x_fill_left1 = np.linspace(-3, z_alpha, 500)
            y_fill_left1 = norm.pdf(x_fill_left1, loc=0, scale=1)

            ax2.fill_between(x_fill_left1, y_fill_left1, color='skyblue', alpha=0.6)
        
            ax2.axvline(z_alpha, color='red', linestyle='--')

            ax2.text(z_alpha - 0.1, 0.1, 'Reject $H_0$', fontsize=10, color='red', ha='right')
            ax2.text(z_alpha + 0.1, 0.1, 'Do not Reject $H_0$', fontsize=10, color='red', ha='left')

            ax2.set_title('Standard Normal Distribution')
            ax2.set_xticks([z_alpha, 0, -z_alpha])
            ax2.set_xlabel('$z$ Values')
            ax2.legend()

            # Save the combined figure
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)
            
        elif test_type == "right-tailed":
            # Perform right-tailed test
            z_alpha = norm.ppf(1 - alpha)
            p_value = 1 - norm.cdf(z)
            # Create both subplots side by side
            fig, ax2 = plt.subplots(1, 1, figsize=(6, 4))

            # ===== Second Plot (Standard Normal Distribution) =====
            x = np.linspace(-3, 3, 500)
            y = norm.pdf(x, loc=0, scale=1)
            y2 = np.zeros(500)

            ax2.plot(x, y)
            ax2.plot(z_alpha, 0, 'ro', label = 'Critical Value')
            ax2.plot(z, 0, 'go', label = 'Test Statistic')
            ax2.plot(x, y2)

            # Shade rejection regions
            x_fill_left1 = np.linspace(z_alpha,3, 500)
            y_fill_left1 = norm.pdf(x_fill_left1, loc=0, scale=1)

            ax2.fill_between(x_fill_left1, y_fill_left1, color='skyblue', alpha=0.6)

            ax2.axvline(z_alpha, color='red', linestyle='--')

            ax2.text(z_alpha - 0.1, 0.1, 'Do not Reject $H_0$', fontsize=10, color='red', ha='right')
            ax2.text(z_alpha + 0.1, 0.1, 'Reject $H_0$', fontsize=10, color='red', ha='left')

            ax2.set_title('Standard Normal Distribution')
            ax2.set_xticks([-z_alpha, 0, z_alpha])
            ax2.set_xlabel('$z$ Values')
            ax2.legend()

            # Save the combined figure
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)
    except ValueError:
        return "Invalid input. Please enter valid numbers."
    return jsonify({"z": round(z, 4),
                    "p_value": round(p_value, 4),
                    "z_alpha": round(z_alpha, 4),
                    "alpha": alpha,
                    "image": encoded})





