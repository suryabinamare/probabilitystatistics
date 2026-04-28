from flask import Flask, jsonify, request, Blueprint, render_template, current_app

import base64
import io
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from sympy import latex, Eq, symbols
import seaborn as sns
from scipy.stats import f
from scipy.stats import norm
from scipy.stats import t
from scipy.stats import chi2
import scipy.stats as stats
from werkzeug.utils import secure_filename
from sklearn.linear_model import LinearRegression
from flask import Blueprint



linear_bp = Blueprint("linear", __name__)



@linear_bp.route("/descriptive", methods=["GET", "POST"])
def descriptive():
    equation = None
    plot_url = None
    values = None
    if request.method == "GET":
        return render_template(
            "linear_descriptive.html")

    if request.method == "POST":

        # ---------- CASE 1: JSON (manual x,y input) ----------
        if request.content_type and request.content_type.startswith("application/json"):
            data = request.get_json()
            action = data.get("action")

            x1 = np.array(data.get("x", []), dtype=float)
            y1 = np.array(data.get("y", []), dtype=float)

            if len(x1) < 2 or len(y1) < 2:
                equation = "❌ Please enter at least two points."
                return render_template(
                    "linear_descriptive.html",
                    equation=equation,
                    plot_url=None,
                    values=None,
                    title="Linear Regression"
                )
            df = pd.DataFrame({"x": x1, "y": y1})

        # ---------- CASE 2: File upload ----------
        else:
            file = request.files.get("file")
            action = request.form.get("action")

            if not file or file.filename == "":
                equation = "❌ No file uploaded."
                return render_template(
                    "linear_descriptive.html",
                    equation=equation,
                    plot_url=None,
                    values=None,
                    title="Linear Regression"
                )

            if file.filename.endswith(".csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            x1 = df.iloc[:, 0].to_numpy(dtype=float)
            y1 = df.iloc[:, 1].to_numpy(dtype=float)

        # ---------- COMPUTATIONS ----------
        n = len(y1)
        x_bar = np.mean(x1)
        y_bar = np.mean(y1)

        Sxx = np.sum(x1**2) - (np.sum(x1)**2) / n
        Syy = np.sum(y1**2) - (np.sum(y1)**2) / n
        Sxy = np.sum(x1 * y1) - (np.sum(x1) * np.sum(y1)) / n

        m = round(Sxy / Sxx, 4)
        b = round(y_bar - m * x_bar, 4)

        R_squared = Sxy**2 / (Sxx * Syy)
        sig = np.sqrt(R_squared)

        y_pred = m * x1 + b
        residuals = y1 - y_pred

        # Equation
        x, y = sp.symbols("x y")
        equation = latex(Eq(y, m * x + b))

        se = np.sqrt(np.sum(residuals**2) / (n - 2))
        SSE = np.sum(residuals**2)

        # ---------- PLOTS ----------
        if action in ("plot", "plot1"):
            fig, ax = plt.subplots( 1, 1, figsize=(6, 6))
            fig1, ax1 = plt.subplots( 1, 1, figsize=(6, 6))
            fig2, ax2 = plt.subplots( 1, 1, figsize=(6, 6))
            fig3, ax3 = plt.subplots( 1, 1, figsize=(6, 6))


            # Scatter + regression
            ax.scatter(x1, y1, color="blue", label="Data points", marker='o')
            ax.set_xlabel("x values")
            ax.set_ylabel("y values")
            ax.set_title("Scatter Plot")
            ax.legend(loc="best")
            ax.grid()
            img = io.BytesIO()
            plt.tight_layout()
            fig.savefig(img, format="png")
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()            
            plt.close(fig)

            #scatter + regression line
            ax1.scatter(x1, y1, color="blue", label="Data points", marker='o')
            ax1.plot(x1, y_pred, color="red", label="Regression Line", marker = '*')
            for i in range(n):
                ax1.plot([x1[i], x1[i]], [y1[i], y_pred[i]], linestyle="--", linewidth=0.7)
            ax1.scatter(x1, y_pred, color="green", label="Predicted Points", marker='x')
            ax1.set_xlabel("x values")
            ax1.set_ylabel("y values")
            ax1.set_title("Scatter Plot with Regression Line")
            ax1.legend(loc="best")
            ax1.grid()
            img1 = io.BytesIO()
            plt.tight_layout()
            fig1.savefig(img1, format="png")
            img1.seek(0)
            plot_url1 = base64.b64encode(img1.getvalue()).decode()
            plt.close(fig1)


            ax2.scatter(x1, residuals, color="purple")
            ax2.axhline(0, linestyle="--", color="black")
            ax2.set_xlabel("x values")
            ax2.set_ylabel("Residuals")
            ax2.set_title("Residuals vs X")
            ax2.legend(loc="best")
            ax2.grid()
            img2 = io.BytesIO()
            plt.tight_layout()
            fig2.savefig(img2, format="png")
            img2.seek(0)
            plot_url2 = base64.b64encode(img2.getvalue()).decode()
            plt.close(fig2)


            #Normal probability plot
            ordered_residuals = np.sort(residuals)
            theoretical_quants = norm.ppf((np.arange(1, n + 1) - 0.5) / n)
            ax3.scatter(ordered_residuals, theoretical_quants, color="orange")
            ax3.set_xlabel("Residuals")
            ax3.set_ylabel("Normal Probability Quantiles")
            ax3.set_title("Normal Probability Plot")
            ax3.legend(loc="best")
            ax3.grid()
            img3 = io.BytesIO()
            plt.tight_layout()
            fig3.savefig(img3, format="png")
            img3.seek(0)
            plot_url3 = base64.b64encode(img3.getvalue()).decode()           
            plt.close(fig3)

            values =[x_bar,
                y_bar,
                Sxx,
                Syy,
                Sxy,
                m,
                b,
                R_squared,
                sig,
                se,
                SSE]
            

    return jsonify({
        'df': df.to_html(classes = "fancy-table", index=False),
        "equation": equation,
        "values": values,
        "img_scatter": plot_url,
        "img_regression": plot_url1,
        "img_residuals": plot_url2,
        "img_qq": plot_url3
    })









@linear_bp.route("/inferential", methods=["GET", "POST"])
def inferential():
    return render_template(
        "linear_inferential.html")





