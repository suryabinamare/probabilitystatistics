
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
from scipy.stats import t
from scipy.stats import chi2
from werkzeug.utils import secure_filename
import matplotlib
import math
matplotlib.use('Agg')  # Use non-GUI backend





distributions_bp = Blueprint("distributions", __name__, template_folder="../templates")

@distributions_bp.route("/binomialdistribution", methods=["GET", "POST"])
def binomialdistribution():
    return render_template("binomial_distribution.html")

binom_histogram = []
def generate_binom_plot():
    for n, p in binom_histogram:
        x = np.arange(0, n+1)
        y = np.zeros(len(x))
        for i in x:
            y[i] = (math.factorial(n) / (math.factorial(i) * math.factorial(n - i))) * (p ** i) * ((1 - p) ** (n - i))
        #plt.bar(x, y, alpha=0.6, label=f"n={n}, p={p}")
        plt.figure(figsize=(8,6))
        bars = plt.bar(x, y, color = 'purple', alpha=0.8, label=f"n={n}, p={p}")
        plt.bar_label(bars, labels=[f"{v:.2f}%" for v in y*100], padding=3, fontsize=8)
    plt.title("Binomial Distributions")
    plt.xlabel("Number of Successes")
    plt.ylabel("Probability")
    plt.legend()
    plt.grid()
    # Save plot to memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()
    return encoded

@distributions_bp.route("/add_binom_curve", methods = ['GET', 'POST'])
def add_binom_curve():
    n = int(request.form["n"])
    p = float(request.form["p"])
    error = None
    try:
        binom_histogram.append((n, p))

        image = generate_binom_plot()
    except ValueError:
        return jsonify({"error": "Invalid input for number of trials or probability."}), 400    
    return jsonify({"img": image, "error": error})
@distributions_bp.route("/reset_binom", methods=["POST", "GET"])
def reset_binom():
    binom_histogram.clear()
    image = generate_binom_plot()
    return jsonify({"img": image})






@distributions_bp.route("/find_prob", methods=["POST"])
def find_prob():
    n = int(request.form["n"])
    p = float(request.form["p"])
    k = int(request.form["k"])
    error = None
    data = None
    try:
        data = pd.DataFrame(columns=["Number of Successes (x)","Coef:C(n,k)", "Probability P(X=k)"])
        suc = []
        coeff = []
        prob = []
        prob_sum1 = 0
        prob_sum = 0
        for i in range(n+1):
            coef = math.factorial(n) / (math.factorial(i) * math.factorial(n - i))
            coeff.append(coef)
            suc.append(i)
            prob_i = coef * (p ** i) * ((1 - p) ** (n - i))
            prob.append(prob_i)
            data = pd.concat([data, pd.DataFrame({"Number of Successes (x)": [i], "Coef:C(n,k)": [int(coef)], "Probability P(X=k)": [prob_i]})], ignore_index=True)
        for j in range(k+1):
                prob_sum += prob[j]
        pro_k = prob[k]
        prob_sum1 = 1 - prob_sum
        data_values = pd.DataFrame({
            rf"$P(X \leq {k})$": [prob_sum],
            rf"$P(X < {k})$": [prob_sum - pro_k],
            rf"$P(X = {k})$": [pro_k],
            rf"$P(X > {k})$": [prob_sum1],
            rf"$P(X \geq {k})$": [prob_sum1 + pro_k]
        })
    except ValueError:
        return jsonify({"error": "Invalid input for number of trials, probability, or number of successes."}), 400    
    return jsonify({"probability": prob_sum, "error": error, 
                    "data": data.to_html(classes="fancy-table", index=False), 
                    "data_values": data_values.to_html(classes="fancy-table", index=False)})


#*****************************************************************************************************************************





@distributions_bp.route("/poissondistribution", methods=["GET", "POST"])
def poissondistribution():
    return render_template("poisson_distribution.html")

@distributions_bp.route("/plot_poisson", methods=["POST", "GET"])
def plot_poisson():
    lam = float(request.form["lambda"])
    error = None
    try:
        x = np.arange(0, math.floor(lam + 20))  # Extend range to ensure sufficient data points
        y = [(lam ** i) * np.exp(-lam) / math.factorial(i) for i in x]
        plt.figure(figsize=(8, 4))
        bars = plt.bar(x, y, color="purple", alpha=0.8)
        bars.datavalues = [f"{v:.4f}" for v in y]
        plt.title(f"Poisson Distribution (λ={lam})")
        plt.xlabel("Number of Occurrences (k)")
        plt.ylabel("Probability")
        plt.grid(True, linestyle = "--", alpha=0.5)
        # Save plot to memory buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        plt.close()
    except ValueError:
        return jsonify({"error": "Invalid input for mean (λ)."}), 400    
    return jsonify({"img": encoded, "error": error})



@distributions_bp.route("/find_poisson_prob", methods=["POST"])
def find_poisson_prob():
    lam = float(request.form["lambda"])
    k = int(request.form["k"])
    error = None
    data = None
    try:       
        
        prob = 0
        prob_list = []
        for j in range(k+1):
            p_j = (lam ** j) * np.exp(-lam) / math.factorial(j)
            prob_list.append(p_j)
            prob += p_j
        pro_k = prob_list[k]
        mean = lam
        std = np.sqrt(lam)
        
        data_values = pd.DataFrame({
            rf"$P(X \leq {k})$": [prob],
            rf"$P(X < {k})$": [prob - pro_k],
            rf"$P(X = {k})$": [pro_k],
            rf"$P(X > {k})$": [1-prob],
            rf"$P(X \geq {k})$": [1-prob + pro_k]
        })
       
    except ValueError:
        return jsonify({"error": "Invalid input for mean or number of successes."}), 400    
    return jsonify({"error": error, 
                    "data_values": data_values.to_html(classes="fancy-table", index=False), "mean": mean, "std": std})















#*****************************************************************************************************************************
# Normal Distribution

curves = []

def generage_plot():
    for mean, std in curves:
        x = np.linspace(mean - 4*std, mean + 4*std, 400)
        y = (1/(std * np.sqrt(2*np.pi))) * np.exp(-((x-mean)**2) / (2*std**2))
        plt.plot(x, y, label=f"μ={mean}, σ={std}")
        y1 = np.zeros(len(x))
        plt.plot(x, y1, color='black')  # x-axis
        plt.plot(mean, 0, 'ro')  # mean point
        plt.axvline(mean, color='red', linestyle='--')
    plt.title("Normal Distributions")

    plt.legend()
    plt.grid()
    # Save plot to memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()
    return encoded





@distributions_bp.route("/zdistribution", methods=["GET", "POST"])
def zdistribution():
    if request.method == "GET":
        # Simply render the HTML page when the user opens /distributions/zdistribution
        return render_template("z-distribution.html")
    # Initialize values so they always exist
    z_value = None
    p_value = None
    error = None
    encoded = None
    p_value_bigger = None
    try:
        # Read raw input (string)
        raw_z = request.form.get("z_given", "").strip()
        z_value = float(raw_z)
        p_value = norm.cdf(z_value)
        p_value_bigger = 1 - p_value

        #genetate a plot:      
        x = np.linspace(-4, 4, 500)
        y = norm.pdf(x)
        y1 = np.zeros(len(x))

        fig, ax = plt.subplots(figsize=(6,4))
        ax.plot(x, y)

        # Z score marker
        ax.plot(z_value, 0, 'ro')
        ax.plot(x, y1, color='black')  # x-axis
        #ax.axvline(z_value, color='red', linestyle='--')

        # Fill area under curve
        x_fill = np.linspace(-4, z_value, 500)
        y_fill = norm.pdf(x_fill)
        ax.fill_between(x_fill, y_fill, alpha=0.6, color='skyblue', label=f'P(Z ≤ {z_value})= {p_value:.4f}')
        x_fill1 = np.linspace(z_value, 4, 500)
        y_fill1 = norm.pdf(x_fill1)
        ax.fill_between(x_fill1, y_fill1, alpha=0.6, color='lightcoral', label=f'P(Z > {z_value})= {p_value_bigger:.4f}')
        #ax.text(z_value-0.1, 0.05, f"P = {p_value:.4f}", color="red", ha="right")
        ax.set_xlabel("Z-value")
        ax.set_ylabel("Density")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.5)
        # Save figure to base64
        buf1 = io.BytesIO()
        plt.savefig(buf1, format="png")
        buf1.seek(0)
        encoded = base64.b64encode(buf1.read()).decode("utf-8")
        plt.close()

    except ValueError as e:
        error = str(e)
    return jsonify({
        "z_value": z_value,
        "p_value": p_value,
        "p_value_bigger": p_value_bigger,
        "img": encoded,
        "error": error
    })



@distributions_bp.route("/zvalue", methods=["POST"])
def zvalue():
    try:
        p_raw = request.form.get("p_given")
        area_type = request.form.get("area_type")

        p_given = float(p_raw)

        # Compute z-value
        if area_type == "left":
            z_value = norm.ppf(p_given)
        else:
            z_value = norm.isf(p_given)

        # Adjust plot range dynamically
        x_limit = max(4, abs(z_value) + 1)
        x = np.linspace(-x_limit, x_limit, 500)
        y = norm.pdf(x)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(x, y)

        ax.plot(z_value, 0, 'ro', label = f'z-value = {z_value:.4f}')
        ax.axhline(0, color='black')

        if area_type == "left":
            x_fill = np.linspace(-x_limit, z_value, 500)
            label = f'p-value = {p_given:.4f}'
            color = 'skyblue'
        elif area_type == "right":
            x_fill = np.linspace(z_value, x_limit, 500)
            label = f'p-value = {p_given:.4f}'
            color = 'skyblue'

        ax.fill_between(x_fill, norm.pdf(x_fill), alpha=0.6, color=color, label=label)

        ax.set_xlabel("Z-value")
        ax.set_ylabel("Density")
        ax.legend(loc = "upper right")
        ax.grid(True, linestyle='--', alpha=0.5)

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)

        return jsonify({
            "z_value": round(z_value, 4),
            "img": encoded,
            "error": None
        })

    except Exception as e:
        return jsonify({"error": str(e)})




@distributions_bp.route("/add_curve", methods = ['GET', 'POST'])
def add_curve():
    mean = float(request.form["mean"])
    std = float(request.form["std"])
    try:
        if std <= 0:
            return jsonify({"error": "Standard deviation must be positive."}), 400
        curves.append((mean, std))

        image = generage_plot()
    except ValueError:
        return jsonify({"error": "Invalid input for mean or standard deviation."}), 400    
    return jsonify({"img": image})




@distributions_bp.route("/reset", methods = ['GET', 'POST'])
def reset():
    curves.clear()
    image = generage_plot() 
    return jsonify({"img": image})



@distributions_bp.route("/find_probabilities", methods = ['GET', 'POST'])
def find_probabilities():
    mean = float(request.form["mean"])
    std = float(request.form["std"])
    x_value = float(request.form["x_value"])
    error = None
    probabilities = None
    try:
        z_score = (x_value - mean) / std
        p_less_than_x = norm.cdf(z_score)
        p_greater_than_x = 1 - p_less_than_x
        
        probabilities = pd.DataFrame({
            "Probability": [
                rf"$P(X < {x_value})$",
                rf"$P(X > {x_value})$"
            ],
            "Value": [
                p_less_than_x,
                p_greater_than_x
            ]})
        #plotting
        plt.figure(figsize=(8,6))
        x = np.linspace(mean - 4*std, mean + 4*std, 1000)
        y = (1/(std * np.sqrt(2*np.pi))) * np.exp(-((x-mean)**2) / (2*std**2))
        plt.plot(x, y, label=f"μ={mean}, σ={std}")
        y1 = np.zeros(len(x))
        plt.plot(x, y1, color='black')  # x-axis
        plt.plot(x_value, 0, 'ro')  # mean point
        #plt.axvline(x_value, color='red', linestyle='--')
        # Fill area under curve
        x_fill = np.linspace(mean - 4*std, x_value, 500)
        y_fill = norm.pdf(x_fill, mean, std)
        x_fill1 = np.linspace(x_value, mean + 4*std, 500)
        y_fill1 = norm.pdf(x_fill1, mean, std)
        plt.fill_between(x_fill, y_fill, alpha=0.6, color='skyblue', label=f'$P(X < {x_value})$ = {p_less_than_x:.4f}')
        plt.fill_between(x_fill1, y_fill1, alpha=0.6, color='lightcoral', label=f'$P(X > {x_value})$ = {p_greater_than_x:.4f}')
        plt.title("Normal Distribution")

        plt.legend()
        
        plt.grid(True, linestyle='--', alpha=0.5)
        
        # Save plot to memory buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        plt.close()
    except ValueError:
        return jsonify({"error": "Invalid input for mean, standard deviation, or X value."}), 400    
    return jsonify({"p_less_than": p_less_than_x, "p_greater_than": p_greater_than_x, "img": encoded, "error": error})




#*****************************************************************************************************************************

# Chi-Square Distribution

chisquare_curves = []
def generate_chisquare_plot():
    for df in chisquare_curves:
        x = np.linspace(0, 3*df, 500)
        y = chi2.pdf(x, df)
        plt.plot(x, y, label=f"df={df}")
        y1 = np.zeros(len(x))
        x1 = np.zeros(len(x))
        plt.plot(x, y1, color='black')  # x-axis
        plt.plot(x1, y, color='black')  # y-axis
        plt.plot(df, 0, 'ro')  # mean point
        plt.axvline(df, color='red', linestyle='--', label = "mean")
        
    plt.title("Chi-Square Distributions")

    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    #plt.grid()
    # Save plot to memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()
    return encoded
@distributions_bp.route("/add_chisquare_curve", methods = ['GET', 'POST'])
def add_chisquare_curve():
    error = None
    df = float(request.form["df"])
    try:
        chisquare_curves.append((df))
        image = generate_chisquare_plot()
    except ValueError:
        return jsonify({"error": "Invalid input for Degrees of Freedom."}), 400    
    return jsonify({"img": image, "error": error})



@distributions_bp.route("/reset_chisquare", methods=["POST", "GET"])
def reset_chisquare():
    chisquare_curves.clear()
    image = generate_chisquare_plot()
    return jsonify({"img": image})






@distributions_bp.route("/chisquaredistribution", methods=["GET", "POST"])
def chisquaredistribution():  
    p_value = None
    encoded = None
    error = None
    if request.method == "GET":
        return render_template("chisquare_distribution.html")
    try:
        chi_raw = float(request.form.get("chi2_given"))
        df_raw = float(request.form.get("df_given"))
        p_value = 1 - chi2.cdf(chi_raw, df_raw)
        

        # ---------- Plot ----------
        x = np.linspace(0, 4*df_raw, 500)
        y = chi2.pdf(x, df_raw)
        y1 = np.zeros(len(x))
        x1 = np.zeros(len(x))

        fig, ax = plt.subplots(figsize=(6,4))
        ax.plot(x, y)
        ax.plot(x1, y, color='black')  # y-axis
        ax.plot(x, y1, color='black')  # x-axis
        ax.plot(chi_raw, 0, 'ro', label = f"Chi-Square Value = {chi_raw}")  # chi-square point
        #ax.axvline(chi_raw, color="red", linestyle="--")
        ax.fill_between(x[x >= chi_raw], y[x >= chi_raw], alpha=0.6, color='skyblue', label=f'P-value = {p_value:.4f}')
        # ax.text(chi_raw + 0.1, 0.01, f'p-value = {p_value:.4f}', color='red', ha='left')
        ax.set_xlabel("Chi-Square Value")
        ax.set_ylabel("Probability Density")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.5)

        # Save to base64
        buf1 = io.BytesIO()
        fig.savefig(buf1, format="png")
        buf1.seek(0)
        encoded = base64.b64encode(buf1.read()).decode()
        plt.close(fig)

    except Exception as e:
        error = f"Error: {str(e)}"

    return jsonify({"p_value": p_value,
       "plot_path": encoded,
        "error": error
    })




@distributions_bp.route("/chisquarevalue", methods = ["POST", "GET"])
def chisquarevalue():
    try:
        p_raw = float(request.form.get("p_value"))
        df_input = float(request.form.get("df"))
        chi_value = chi2.isf(p_raw, df_input)
       
        x_limit = max(4*df_input, chi_value + 1)
        x = np.linspace(0, x_limit, 500)
        y = chi2.pdf(x, df_input)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(x, y)

        ax.plot(chi_value, 0, 'ro', label=f'Chi-Square Value = {chi_value:.4f}')
        ax.axhline(0, color='black')
        x_fill = np.linspace(chi_value, x_limit, 500)
        ax.fill_between(x_fill, chi2.pdf(x_fill, df_input), alpha=0.6, color='skyblue', label=f'P-value = {p_raw:.4f}')

        ax.set_xlabel("Chi-Square Value")
        ax.set_ylabel("Density")
        ax.legend(loc="upper right")
        ax.grid(True, linestyle='--', alpha=0.5)

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)

        return jsonify({
            "chi_square_value":chi_value,
            "img": encoded,
            "error": None
        })

    except Exception as e:
        return jsonify({"error": str(e)})







#*****************************************************************************************************************************

# T-distribution
@distributions_bp.route("/tdistribution", methods=["GET", "POST"])

def tdistribution():
    if request.method == 'GET':
        return render_template('t-distribution.html')
   
    p_value = None
    df_input = None
    encoded = None
   
    error = None
   
    try:
        # Get form inputs
        t_input = float(request.form.get('t_given'))
        df_input = float(request.form.get('df_given'))
        p_value = t.cdf(float(t_input), df_input)
        

        # === Generate Plot if we have a valid t-score ===
        
        x = np.linspace(-5, 5, 500)
        y = t.pdf(x,df_input)
        y1 = np.zeros(len(x))
        fig, ax = plt.subplots(figsize = (6,4))

        ax.plot(x, y)
        ax.plot(t_input, 0, 'ro', label=f't-value = {t_input}')  # t-score point
        ax.plot(x, y1, color='black')  # x-axis


        # Fill area under curve up to Z
        x_fill = np.linspace(-5, t_input, 500)
        y_fill = t.pdf(x_fill, df_input)
        ax.fill_between(x_fill, y_fill, color='skyblue', alpha=0.6, label = f'P(t < {t_input}) = {p_value:.4f}')
        ax.fill_between(x[x >= t_input], y[x >= t_input], color='lightcoral', alpha=0.6, label = f'P(t > {t_input}) = {1-p_value:.4f}')
        ax.grid(True, linestyle='--', alpha=0.5)
        #ax.axvline(t_input, color='red', linestyle='--')
        #ax.text(t_input - 0.1, 0.05, f'p-value = {p_value:.4f}', color='red', ha='right')
        #ax.set_title('Z-Score and P-Value on Normal Curve')
        ax.set_xlabel('t-value')
        ax.set_ylabel('Probability Density')
        #ax.set_xticks([t_input])
        ax.legend()
        plt.grid(True)

            # Save figure to base64
        buf1 = io.BytesIO()
        fig.savefig(buf1, format="png")
        buf1.seek(0)
        encoded = base64.b64encode(buf1.read()).decode("utf-8")
        plt.close(fig)

    except Exception as e:
        error = f"Error: {str(e)}"

    return jsonify({"p_value": p_value, "p_value1": 1 - p_value,
                    "plot_path": encoded,
                    "error": error})





@distributions_bp.route("/tvalue", methods=["POST", "GET"])
def tvalue():
    try:
        p_raw = request.form.get("p_value")       
        df_input = float(request.form.get("df"))
        area_type = request.form.get("area_type")

        p_given = float(p_raw)

        # Compute t-value
        if area_type == "left":
            t_value = t.ppf(p_given, df_input)
        else:
            t_value = t.isf(p_given, df_input)

        # Adjust plot range dynamically
        x_limit = max(5, abs(t_value) + 1)
        x = np.linspace(-x_limit, x_limit, 500)
        y = t.pdf(x, df_input)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(x, y)

        ax.plot(t_value, 0, 'ro', label=f't-value = {t_value:.4f}')
        ax.axhline(0, color='black')

        if area_type == "left":
            x_fill = np.linspace(-x_limit, t_value, 500)
            label = f'p-value = {p_given:.4f}'
            color = 'skyblue'
        elif area_type == "right":
            x_fill = np.linspace(t_value, x_limit, 500)
            label = f'p-value = {p_given:.4f}'
            color = 'skyblue'

        ax.fill_between(x_fill, t.pdf(x_fill, df_input), alpha=0.6, color=color, label=label)

        ax.set_xlabel("t-value")
        ax.set_ylabel("Density")
        ax.legend(loc="upper right")
        ax.grid(True, linestyle='--', alpha=0.5)

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)

        return jsonify({
            "t_value": round(t_value, 4),
            "img": encoded,
            "error": None
        })

    except Exception as e:
        return jsonify({"error": str(e)})







#*****************************************************************************************************************************
# F-distribution
dof = []
def generate_f_plot():
    for dfn, dfd in dof:
        mean = f.mean(dfn, dfd)
        std = f.std(dfn, dfd)
        x_max = mean + 5 * std

        x = np.linspace(0, x_max, 500)
        y = f.pdf(x, dfn, dfd)
        plt.plot(x, y, label=f"dfn={dfn}, dfd={dfd}")
        y1 = np.zeros(len(x))
        x1 = np.zeros(len(x))
        plt.plot(x1, y, color='black')  # y-axis
        plt.plot(x, y1, color='black')  # x-axis
        plt.plot(mean, 0, 'ro', label = "Mean")  # mean point
        #plt.axvline(mean, color='red', linestyle='--')
        
    plt.title("F-Distributions")
    plt.grid(True, linestyle='--', alpha=0.5)

    plt.legend()
    #plt.grid(True)
    # Save plot to memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()
    return encoded

@distributions_bp.route("/add_f_curve", methods = ['GET', 'POST'])
def add_f_curve():
    error = None
    dfn = float(request.form["dfn"])
    dfd = float(request.form["dfd"])
    
    try:
        dof.append(((dfn, dfd)))
        image = generate_f_plot()
    except ValueError:
        return jsonify({"error": "Invalid input for Degrees of Freedom."}), 400    
    return jsonify({"img": image, "error": error})

@distributions_bp.route("/reset_f", methods=["POST", "GET"])
def reset_f():
    global dof
    dof.clear()
    image = generate_f_plot()
    return jsonify({"img": image})  









@distributions_bp.route("/fdistribution", methods=["GET", "POST"])
def fdistribution():

    if request.method == "GET":
        return render_template("F-distribution.html")

    df = None
    error = None
    encoded = None

    try:
        f_value = float(request.form.get("f_given"))
        dfn = float(request.form.get("dfn_given"))
        dfd = float(request.form.get("dfd_given"))

        alpha = 1 - f.cdf(f_value, dfn, dfd)

        

        # ------------ Plot ------------
        mean = f.mean(dfn, dfd)
        std = f.std(dfn, dfd)
        x_max = mean + 10 * std

        x = np.linspace(0, x_max, 500)
        y = f.pdf(x, dfn, dfd)
        y1 = np.zeros(len(x))
        x1 = np.zeros(len(x))

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(x, y)
        ax.plot(x1, y, color='black')  # y-axis
        ax.plot(x, y1, color='black')  # x-axis
        ax.plot(f_value, 0, 'ro', label=f"F-value = {f_value}")  # f-value point
        #ax.text(f_value + 0.1, 0.01, f'P-Value = {alpha:.4f}', color='red', ha='left')
        #ax.axvline(f_value, color="red", linestyle="--")
        ax.fill_between(x[x >= f_value], y[x >= f_value], alpha=0.6, label = f'P-value = {alpha:.4f}', color='skyblue')

        ax.set_title("F-Distribution Curve")
        ax.set_xlabel("F-value")
        ax.set_ylabel("Density")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.5)

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)

    except Exception as e:
        error = f"Error: {str(e)}"

    return jsonify({
        "img": encoded,
        "error": error,
        "p_value": alpha
    })




@distributions_bp.route("/fdistribution_value", methods=["POST", "GET"])
def fdistribution_value():
    try:
        p_raw = float(request.form.get("p_given"))
        dfn = float(request.form.get("dfn_given"))
        dfd = float(request.form.get("dfd_given"))

        f_value = f.isf(p_raw, dfn, dfd)

        # Adjust plot range dynamically
        mean = f.mean(dfn, dfd)
        std = f.std(dfn, dfd)
        x_max = mean + 10 * std

        x = np.linspace(0, x_max, 500)
        y = f.pdf(x, dfn, dfd)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(x, y)

        ax.plot(f_value, 0, 'ro', label=f'F-value = {f_value:.4f}')
        ax.axhline(0, color='black')

        x_fill = np.linspace(f_value, x_max, 500)
        ax.fill_between(x_fill, f.pdf(x_fill, dfn, dfd), alpha=0.6, color='skyblue', label=f'p-value = {p_raw:.4f}')

        ax.set_xlabel("F-value")
        ax.set_ylabel("Density")
        ax.legend(loc="upper right")
        ax.grid(True, linestyle='--', alpha=0.5)

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)

        return jsonify({
            "f_value": round(f_value, 4),
            "img": encoded,
            "error": None
        })

    except Exception as e:
        return jsonify({"error": str(e)})







#*****************************************************************************************************************************


def create_normal_plot(mean, std):
    x = np.linspace(mean - 4*std, mean + 4*std, 400)
    y = (1/(std * np.sqrt(2*np.pi))) * np.exp(-((x-mean)**2) / (2*std**2))

    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title(f"Normal Distribution (mean={mean}, std={std})")

    # Save plot to memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()
    return encoded







@distributions_bp.route("/plot", methods = ['GET', 'POST'])
def plot():
    data = request.json
    mean = float(data["mean"])
    std = float(data["std"])

    image = create_normal_plot(mean, std)
    return jsonify({"image": image})



