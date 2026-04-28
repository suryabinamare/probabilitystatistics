from flask import Flask, request, Blueprint, render_template, current_app, jsonify
import os
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import f
from werkzeug.utils import secure_filename
import base64
import chardet
import io
import openpyxl
import xlrd
from IPython.display import display, Math



# Create a blueprint for ANOVA routes
anova_bp = Blueprint("anova", __name__, template_folder="../templates")


@anova_bp.route("/anova1", methods=["GET", "POST"])
def anova1():
    if request.method == "GET":
        # when you open /anova in browser, show the page
        return render_template("anova.html")

    # when JavaScript sends form data (POST)
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "No JSON data received"}), 400


        df_num = int(data.get("df_num", 0))
        df_deno = int(data.get("df_deno", 0))
        alpha = float(data.get("alpha", 0.05))

        if df_num <= 1 or df_deno <= 1:
            return jsonify({"error": "Degrees of freedom must be positive."}), 400

        if not (0 < alpha < 1):
            return jsonify({"error": "Alpha must be between 0 and 1."}), 400



        # Compute critical F value
        f_value = f.ppf(1 - alpha, df_num, df_deno)

        # Generate F-distribution curve
        mean = f.mean(df_num, df_deno)
        std = f.std(df_num, df_deno)
        x_max = mean + std * 4
        x = np.linspace(0, x_max, 500)
        y = f.pdf(x, df_num, df_deno)
        y1 = np.zeros(500)

        # Plot and save
        plt.figure(figsize=(6, 4))
        plt.plot(x, y, color="blue", label=f"F-dist (dfn={df_num}, dfd={df_deno})")
        plt.plot(x,y1)
        plt.scatter(f_value, 0, marker = 'o', color = 'red', s = 100, label=f"Critical F-value ={f_value:.3f}")
        plt.axvline(f_value, color="red", linestyle="--")
        x_fill = np.linspace(f_value, x_max, 500)
        y_fill = f.pdf(x_fill, df_num, df_deno)
        plt.fill_between(x_fill, y_fill, alpha=0.3, color="blue", label="Rejection region")
        plt.legend()
        plt.title("F-Distribution Curve")
        plt.xlabel("F-value")
        plt.ylabel("Density")
        plt.grid(True, linestyle="--", alpha=0.5)

        img1 = io.BytesIO()
        plt.tight_layout()
        plt.savefig(img1, format="png")
        img1.seek(0)
        plot_path = base64.b64encode(img1.getvalue()).decode()
        plt.close()

        return jsonify({
            "f_value": round(f_value, 4),
            "plot_fcurve": plot_path
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500






@anova_bp.route("/anovaValues", methods=["POST", "GET"])
def anova():
    if request.method == "GET":
        return render_template('anova.html')

    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    try:
        # Optionally detect encoding
        # raw_data = file.read()
        # encoding = chardet.detect(raw_data)["encoding"]
        # file.seek(0)
        if file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file, encoding="utf-8")

        stats_df = df.describe().iloc[0:3]
        stats_df.iloc[0] = stats_df.iloc[0].astype(int)  # sample size as int
        stats_df.index = ['Sample size', 'Sample mean', 'Sample std.']
        stats_html = stats_df.to_html(classes="fancy-table")
        
     
        x = df.mean().values
        y = [5]*len(x)
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
        ax = plt.gca()
        grand_mean = float(np.nanmean(df.values))
        ax.scatter(x, y, label='Sample Means')
        ax.scatter(grand_mean, [5], color='red', label='Grand Mean')        
        ax.set_title("Sample Means and Grand Mean")
        ax.set_xlabel("Value")
        ax.set_yticklabels([])   
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.5)

        img = io.BytesIO()
        fig.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close(fig)

    
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if len(numeric_cols) < 2:
            return jsonify({"error": "At least two numeric columns are required for ANOVA."})

        sample_size = [int(df[col].count()) for col in numeric_cols]
        mean_val = [float(df[col].mean()) for col in numeric_cols]
        std_val = [float(df[col].std(ddof=1)) for col in numeric_cols]

        flattened = df[numeric_cols].to_numpy().flatten()
        grand_mean = float(np.nanmean(flattened))

        k = len(numeric_cols)
        N = sum(sample_size)

        SSB = sum([sample_size[i] * (mean_val[i] - grand_mean) ** 2 for i in range(k)])
        SSW = sum([(sample_size[i] - 1) * std_val[i] ** 2 for i in range(k)])

        df_between = k - 1
        df_within = N - k

        if df_within == 0:
            return jsonify({"error": "Not enough data for ANOVA."})

        MSB = SSB / df_between
        MSW = SSW / df_within

        if MSW == 0:
            return jsonify({"error": "Within-group variance is zero."})

        F = MSB / MSW
        p_value = 1 - f.cdf(F, df_between, df_within)
        anov = pd.DataFrame({
            'n':[N],
            r"$$\bar{x}$$":[grand_mean],
            'deg of numerator':[df_between],
            'deg of denominator':[df_within],
            'SSTR':[SSB],
            'SSE':[SSW],
            'MSTR':[MSB],
            'MSE':[MSW],
            'F-value':[F],
            'p-value':[p_value]

        })
        anov1 = anov.transpose().reset_index()
        anov1.columns = ['Parameter', 'Value']  

        return jsonify({
            "data":df.to_html(classes = "fancy-table", na_rep = ""),
            "stat_table": stats_html,
            "image": plot_url,
            "anova_table": anov1.to_html(index=False, float_format="%.4f", classes="fancy-table")    
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
