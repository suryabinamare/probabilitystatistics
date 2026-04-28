
async function calculateChiSquareDistribution() {

    const chi2_raw = document.getElementById("chi2-score").value;
    const df_raw = document.getElementById("df").value;

    if (chi2_raw.trim() === "" || df_raw.trim() === "") {
        alert("Please provide both Chi-square score and degrees of freedom.");
        return;
    }

    const chi2_score = Number(chi2_raw);
    const df = Number(df_raw);

    if (isNaN(chi2_score) || isNaN(df)) {
        alert("Please enter numeric values only.");
        return;
    }

    if (chi2_score < 0) {
        alert("Chi-square score must be 0 or greater.");
        return;
    }

    if (df <= 0) {
        alert("Degrees of freedom must be greater than 0.");
        return;
    }

    if (!Number.isInteger(df)) {
        alert("Degrees of freedom must be an integer.");
        return;
    }

    const formData = new FormData();
    formData.append("chi2_given", chi2_score);
    formData.append("df_given", df);

    const res = await fetch("/distributions/chisquaredistribution", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    document.getElementById("chi2-results").innerHTML =
        `<p><strong>P-value = </strong> ${data.p_value}</p>`;

    document.getElementById("chi2_value").src =
        "data:image/png;base64," + data.plot_path;
}
 




async function calculatechi2value() {
    const p_value= document.getElementById("p-value").value;
    const df = document.getElementById("DF").value;

    if (p_value.trim() === "" || df.trim() === "") {
        alert("Please provide both p-value and degrees of freedom.");
        return;
    }

    const p_value_num = Number(p_value);
    const df_num = Number(df);

    if (isNaN(p_value_num) || isNaN(df_num)) {
        alert("Please enter numeric values only.");
        return;
    }

    if (p_value_num < 0 || p_value_num > 1) {
        alert("P-value must be between 0 and 1.");
        return;
    }

    if (df_num <= 0) {
        alert("Degrees of freedom must be greater than 0.");
        return;
    }

    if (!Number.isInteger(df_num)) {
        alert("Degrees of freedom must be an integer.");
        return;
    }

    const formData = new FormData();
    formData.append("p_value", p_value_num);
    formData.append("df", df_num);

    const res = await fetch("/distributions/chisquarevalue", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    document.getElementById("chi2-value-results").innerHTML =
        `<p><strong>Chi-square value = </strong> ${data.chi_square_value}</p>`;

    document.getElementById("chi2-distribution-plot1").src =
        "data:image/png;base64," + data.img;
    MathJax.typeset();
}






async function drawChiSquareDistribution() {
    const df = document.getElementById("df_plot").value;
    if (df.trim() === "") {
        alert("Please enter the degrees of freedom (df) value.");
        return;
    }
    const formData = new FormData();
    formData.append("df", df);
    const res = await fetch("/distributions/add_chisquare_curve", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    if (data.error) {
        alert(data.error);
        return;
    }
    if (data.img) {
        document.getElementById("plot").src = "data:image/png;base64," + data.img;
    }
}

async function reset1() {
    const res = await fetch("/distributions/reset_chisquare", {
        method: "POST"
    });
    const data = await res.json();
    document.getElementById("plot").src = "data:image/png;base64," + data.img;
}