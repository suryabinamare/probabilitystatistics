async function calculateTDistribution() {
    const t_score = Number(document.getElementById("t-score").value);
    const df = Number(document.getElementById("df").value);

    if (isNaN(t_score) || isNaN(df)) {
        alert("Please enter valid numeric values for t-score and degrees of freedom.");
        return;
    }

    if (df <= 0) {
        alert("Degrees of freedom must be greater than 0.");
        return;
    }

    const formData = new FormData();
    formData.append("t_given", t_score);
    formData.append("df_given", df);

    const res = await fetch("/distributions/tdistribution", {
        method: "POST",
        body: formData
    });

    if (!res.ok) {
        alert("Server error occurred.");
        return;
    }

    const data = await res.json();

    document.getElementById("tp-results").innerHTML =
        `<br>
        <p><strong>Area to the left of t = ${t_score} is </strong> ${data.p_value.toFixed(4)}</p>
        <p><strong>Area to the right of t = ${t_score} is </strong> ${data.p_value1.toFixed(4)}</p>`;

    document.getElementById("t-distribution-plot").src =
        "data:image/png;base64," + data.plot_path;
}





async function calculateTValue() {
    const p_value = Number(document.getElementById("pvalue").value);
    const df = Number(document.getElementById("DF").value);
    const area_type = document.getElementById("area-type").value;
    if (isNaN(p_value) || isNaN(df)) {
        alert("Please enter valid numeric values for p-value and degrees of freedom.");
        return;
    }
    if (p_value <= 0 || p_value >= 1) {
        alert("Please enter a valid p-value between 0 and 1.");
        return;
    }
    if (df <= 0) {
        alert("Degrees of freedom must be greater than 0.");
        return;
    }
    
    const formData = new FormData();
    formData.append("p_value", p_value);
    formData.append("df", df);
    formData.append("area_type", area_type);

    const res = await fetch("/distributions/tvalue", {
        method: "POST",     
        body: formData
    });

    if (!res.ok) {
        alert("Server error occurred.");
        return;
    }

    const data = await res.json();

    document.getElementById("tp-results1").innerHTML =
        `<br>
        <p><strong>t-value for P = ${p_value} and df = ${df} to the ${area_type} is </strong> ${data.t_value.toFixed(4)}</p>`;

    document.getElementById("t-distribution-plot1").src =
        "data:image/png;base64," + data.img;
}