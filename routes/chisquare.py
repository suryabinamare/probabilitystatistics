from flask import Flask, jsonify, request, Blueprint, render_template, current_app
import os
from matplotlib.pylab import chisquare
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from scipy import io
import seaborn as sns
from scipy.stats import f
from scipy.stats import norm
from scipy.stats import t
from scipy.stats import chi2
import base64
import io
from werkzeug.utils import secure_filename


chisquare_bp = Blueprint("chisquare", __name__)


@chisquare_bp.route("/goodnessfit", methods=["POST", "GET"])
def goodnessfit():
    DF = None
    encode = None
    chi2_crit = None
    p_value = None
    alpha = None
    if request.method == "GET":
        return render_template("goodnesstest.html")
    try:
        data = request.get_json()

        observed = np.array(data["observedValues"])
        expected = np.array(data["expectedValues"])
        alpha = data.get("alpha", 0.05)
        if len(observed) != len(expected):
            return jsonify({"error": "Observed and expected arrays must have the same length."}), 400
        n = observed.sum()
        observed_dist = observed / n
        exp_frequency = expected*n
        diff = observed - exp_frequency
        squared_diff = diff ** 2
        divided = squared_diff / exp_frequency
        chi2_stat = divided.sum()
        DF = pd.DataFrame({
            "Expected Dist": expected,
            "Observed Freq (O)": observed,
            "Observed Dist": observed_dist,
            "Expected Freq (E)": exp_frequency,
            "(O-E)": diff,
            "(O-E)² / E": divided
        })

        p_value = chi2.sf(chi2_stat, df=len(observed) - 1)
        chi2_crit = chi2.isf(alpha, df=len(observed) - 1)
        x = np.linspace(0, chi2_stat + 10, 500)
        y = chi2.pdf(x, df=len(observed) - 1)
        y1 = np.zeros(len(x))
        x1 = np.zeros(len(x))
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(x, y, label="Chi-Square Distribution", color="blue")
        ax.plot(x, y1, color="black")
        ax.plot(x1, y, color="black")
        ax.scatter(chi2_stat, 0, color="red", zorder=5, label = "Chi-Square Statistic")
        ax.scatter(chi2_crit, 0, color="green", zorder=5, label = "Critical Value") 
        ax.fill_between(x, y, where=(x >= chi2_crit), color="blue", alpha=0.5, label="Rejection Region")
        ax.axvline(chi2_crit, color="black", linestyle="--")
        ax.set_title("Chi-Square Goodness of Fit Test")
        ax.set_xlabel("Chi-Square Value")
        ax.set_ylabel("Probability Density")
        ax.legend()
        plt.tight_layout()
        # Save to base64
        buf1 = io.BytesIO()
        plt.savefig(buf1, format="png")
        buf1.seek(0)
        encoded = base64.b64encode(buf1.read()).decode()
        plt.close(fig)


        return jsonify({
            "chi2_stat": round(chi2_stat, 4),
            "chi2_crit": round(chi2_crit, 4),
            "p_value": round(p_value, 4),
            "alpha": alpha,
            "DF": DF.to_html(classes="table table-bordered table-striped table-hover", index=False), 
            "image": encoded
                  })
    except Exception as e:
        return jsonify({"error": str(e)}), 400
















@chisquare_bp.route("/independence-test", methods=["POST", "GET"])
def independence_test():
    if request.method == "GET":
        return render_template("independencetest.html")
    try:
        data = request.get_json()
        col_labels = data["colLabels"]       
        row_labels = data["rowLabels"]     
        table_data = data["data"]
        alpha = data.get("alpha", 0.05)

        df = pd.DataFrame(table_data, columns=col_labels, index=row_labels)
        #normalized to plot relative frequencies
        df_normalized = df.div(df.sum(axis=1), axis=0) * 100
        #make a copy of original df
        df_copy = df.copy()
        # Add totals
        df.loc["Total"] = df.sum(axis=0)
        df["Total"] = df.sum(axis=1)
        # Calculate expected frequencies
        total_sum = df_copy.values.sum()
        row_sums = df_copy.sum(axis = 1).to_list()
        col_sums = df_copy.sum(axis = 0).to_list()
        df_expected = np.outer(row_sums, col_sums) / total_sum
        df1 = pd.DataFrame(df_expected, columns = df_copy.columns, index = df_copy.index)

        #normalized to plot relative frequencies
        df1_normalized = df1.div(df1.sum(axis=1), axis=0)* 100
        # Calculate Chi-Square statistic       
        if (df1 == 0).any().any():
            raise ValueError("Expected frequencies contain zero; cannot compute chi-square.")
        else:
            df_diff = (df1 - df_copy) ** 2 / df1
            chi2_stat = df_diff.values.sum()

        df1.loc["Total"] = df1.sum(axis=0).astype(np.int64)
        df1["Total"] = df1.sum(axis=1).astype(np.int64)
        dof = (len(row_sums)-1) * (len(col_sums)-1)

        p_value = chi2.sf(chi2_stat, df=dof)
        if alpha>=1 or alpha<0:
            return jsonify({"error": "Invalid alpha value. Please enter a value between 0 and 1."}), 400
        else:
            chi2_crit = chi2.isf(alpha, df=dof)
        #chi-square plots
        x_chi = np.linspace(0, chi2_stat + 10, 500)
        y_chi = chi2.pdf(x_chi, df=dof)
        y1 = np.zeros(len(x_chi))
        x1 = np.zeros(len(x_chi))
        fig1, ax = plt.subplots(figsize=(7, 5))
        ax.plot(x_chi, y_chi, label="Chi-Square Distribution", color="blue")
        ax.plot(x_chi, y1, color="black")
        ax.plot(x1, y_chi, color="black")
        ax.scatter(chi2_stat, 0, color="red", zorder=5, label = "Chi-Square Statistic")
        ax.scatter(chi2_crit, 0, color="green", zorder=5, label = "Critical Value") 
        ax.fill_between(x_chi, y_chi, where=(x_chi >= chi2_crit), color="blue", alpha=0.5, label="Rejection Region")
        ax.axvline(chi2_crit, color="black", linestyle="--")
        ax.set_title("Chi-Square Goodness of Fit Test")
        ax.set_xlabel("Chi-Square Value")
        ax.set_ylabel("Probability Density")
        ax.legend()
        plt.tight_layout()
        # Save to base64
        buf1 = io.BytesIO()
        plt.savefig(buf1, format="png")
        buf1.seek(0)
        encoded1 = base64.b64encode(buf1.read()).decode()
        plt.close(fig1)


        
        #plots: observed vs expected (relative)
        # plots: observed vs expected
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 5))
        x = np.arange(len(df_normalized.index))
        width = 0.5

        # ------------------
        # Observed plot
        bottoms = np.zeros(len(df_normalized.index))
        for col in df_normalized.columns:
            col_values = df_normalized[col].values
            bars = ax1.bar(x, col_values, width, bottom=bottoms, label=col)
            for bar, val, bottom in zip(bars, col_values, bottoms):
                if val > 0:
                    ax1.text(bar.get_x() + bar.get_width()/2,
                            bottom + val/2,
                            f"{val:.2f}%",
                            ha='center', va='center', color='white', fontsize=10)
            bottoms += col_values

        ax1.set_xticks(x)
        ax1.set_xticklabels(df_normalized.index, rotation=45)
        ax1.set_title("Observed Relative Frequencies")
        ax1.set_ylabel("Percentage")
        ax1.set_xlabel("Categories")

        # ------------------
        # Expected plot
        bottoms = np.zeros(len(df1_normalized.index))  # reset for second plot
        for col in df1_normalized.columns:
            col_values = df1_normalized[col].values
            bars = ax2.bar(x, col_values, width, bottom=bottoms, label=col)
            for bar, val, bottom in zip(bars, col_values, bottoms):
                if val > 0:
                    ax2.text(bar.get_x() + bar.get_width()/2,
                            bottom + val/2,
                            f"{val:.2f}%",
                            ha='center', va='center', color='white', fontsize=10)
            bottoms += col_values

        ax2.set_xticks(x)
        ax2.set_xticklabels(df1_normalized.index, rotation=45)
        ax2.set_title("Expected Relative Frequencies")
        ax2.set_ylabel("Percentage")
        ax2.set_xlabel("Categories")

        # ------------------
        # Single legend for the figure
        handles, labels = ax1.get_legend_handles_labels()
        fig.legend(handles, labels, loc="upper center", ncol=len(labels))

        # Adjust layout so legend doesn’t overlap
        plt.tight_layout(rect=[0, 0, 1, 0.9])

        # save the figure
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
       
        return jsonify({
            "chi2_stat": round(chi2_stat, 4),
            "observed_df": df.to_html(classes="fancy-table", index=True),
            "expected_df": df1.to_html(classes="fancy-table", index=True),
            "p_value": round(p_value, 4),
            "chi2_crit": round(chi2_crit, 4),
            "alpha": alpha,
            "dof": dof,
            "image": encoded, 
            "image_chi": encoded1
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

