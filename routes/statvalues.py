import base64
from io import BytesIO
from flask import Blueprint, render_template, request, current_app, session, jsonify
import os
import seaborn as sns
from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import io
from werkzeug.utils import secure_filename

statistics_bp = Blueprint("statvalues", __name__, template_folder="../templates")


df_global = None


@statistics_bp.route("/statvalues")
def statvalues():
    return render_template("stat-values.html")

# Descriptive Values Calculator
@statistics_bp.route('/upload', methods=["GET", "POST"])
def upload():
    global df_global
    file = request.files['file']
    if file.filename.endswith('.csv'):
        df_global = pd.read_csv(file)
    elif file.filename.endswith('.xlsx'):
        df_global = pd.read_excel(file)
        
    else:
        return "Invalid file format. Please upload CSV or XLSX."
    df_global1 = df_global.head()
    table_html = df_global1.to_html(index=False, na_rep ="", classes="fancy-table")
    return jsonify({"columns": df_global.columns.tolist(), "table_html": table_html})

@statistics_bp.route("/get_mean", methods=["GET", "POST"])
def get_mean():
    global df_global
    col = request.json['col']
    
    if df_global is None:
        return "No data uploaded."
    if col not in df_global.columns:
        return jsonify({"error": "Column not found"}), 400
    mean_value = df_global[col].describe().T.to_frame()
    return jsonify({"mean": mean_value.to_html(na_rep ="", classes="fancy-table")})

@statistics_bp.route("/get_boxplot", methods=["GET", "POST"])
def get_boxplot():
    global df_global
    if df_global is None:
        return "No data uploaded."
    col = request.json['col']
    if col not in df_global.columns:
        return jsonify({"error": "Column not found"}), 400
    
    plt.figure(figsize=(4,6))
    plt.boxplot(df_global[col].dropna(),
                boxprops=dict(color="#4C72B0", linewidth=2))
    #sns.set_style("whitegrid")
    #sns.boxplot(y=df_global[col], color = "#B6CBD4", linewidth=2, width=0.3,
                #flierprops=dict(marker='o', markerfacecolor='red', markersize=8, linestyle='none'))
    plt.title(f"Boxplot of {col}")
    buf = BytesIO()
    plt.savefig(buf, format = 'png')
    buf.seek(0)
    plt.close()
    #encode to base64
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    
    return jsonify({"image": image_base64})

@statistics_bp.route("/get_normalplot", methods = ["GET", "POST"])
def get_normalplot():
    img = None
    global df_global
    if df_global is None:
        return "No data uploaded."
    col = request.json['col']
    if col not in df_global.columns:
        return jsonify({"error": "Column not found"}), 400
    plt.figure(figsize = (10,10))
    stats.probplot(df_global[col].dropna(), dist = 'norm', plot = plt)
    plt.title(f"Normal Probablity Plot of {col}")
    plt.xlabel(r'Theoretical quantiles: $z_{i}$')
    plt.ylabel(r"Ordered Data Values: ${x_{(i)}}$")
    plt.grid()

    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()
    return jsonify({"image":img})



@statistics_bp.route("/get_histogram", methods = ["GET", "POST"])
def get_histogram():
    img = None
    global df_global
    if df_global is None:
        return "No data uploaded."
    col = request.json['col']
    if col not in df_global.columns:
        return jsonify({"error": "Column not found"}), 400
    plt.figure(figsize = (6,6))
    #plt.hist(df_global[col].dropna(), bins = 10, edgecolor = 'black')
    sns.histplot(df_global[col].dropna(), bins = 15, kde = False)
    plt.title(f"Histogram of {col}")
    plt.grid()

    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()
    return jsonify({"image":img})
