function updateN() {
    var n = document.getElementById("n").value;
    document.getElementById("samplesize").innerText = n;
    
}



async function calculate_ci_unknown() {
    // Get input values
    var sample_mean = parseFloat(document.getElementById("mu0").value);
    var sample_std = parseFloat(document.getElementById("sigma").value);
    var df = parseInt(document.getElementById("df").value);
    var alpha = parseFloat(document.getElementById("alpha").value);
    var n = parseInt(document.getElementById("n").value);
    if (isNaN(sample_mean) || isNaN(sample_std) || isNaN(df) || isNaN(alpha) || isNaN(n)) {
        alert("Please enter valid numeric values for all fields.");
        return;
    }
    if (sample_std <= 0) {
        alert("Sample standard deviation (s) must be greater than 0.");
        return;
    }
    if (alpha <= 0 || alpha >= 1) {
        alert("Significance level (α) must be between 0 and 1.");
        return;
    }
    if (n <= 0) {
        alert("Sample size (n) must be greater than 0.");
        return;
    }
    if (df !== n - 1) {
        alert("Degrees of freedom (df) should be equal to n - 1.");
        return;
    }

    const formData = new FormData();
    formData.append("sample_mean", sample_mean);
    formData.append("sample_std", sample_std);
    formData.append("df", df);
    formData.append("alpha", alpha);
    formData.append("n", n);
    const res = await fetch("/populationmean/calculate_ci_unknown", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    
    if (data.error) {
        alert(data.error);
        return;
    }
    document.getElementById("ci-result").innerText = " CI = [" + data.ci_result[0] + ", " + data.ci_result[1] + "] \n ME = " + data.me.toFixed(4);
    document.getElementById("ci-result").style.fontSize = "20px";   // BIG
    document.getElementById("ci-result").style.fontWeight = "bold"; // BOLD
    document.getElementById("ci-plot").src = "data:image/png;base64," + data.plot;
    updateN();
}

document.getElementById("n").oninput = updateN;







async function hypothesis_testing_sigmaunknown()  {
    // Get input values
    var sample_mean = parseFloat(document.getElementById("sample_mean").value);
    var population_mean = parseFloat(document.getElementById("population_mean").value);
    var sample_std = parseFloat(document.getElementById("sample_std").value);
    var n = parseInt(document.getElementById("sample_size").value);
    var alpha = parseFloat(document.getElementById("alpha1").value);
    var df = parseInt(document.getElementById("df1").value);
    var test_type = document.getElementById("Type").value;
    
    if (isNaN(sample_mean) || isNaN(population_mean) || isNaN(sample_std) || isNaN(n) || isNaN(alpha) || isNaN(df)) {
        alert("Please enter valid numeric values for all fields.");
        return;
    }
    if (sample_std <= 0) {
        alert("Sample standard deviation (s) must be greater than 0.");
        return;
    }
    if (alpha <= 0 || alpha >= 1) {
        alert("Significance level (α) must be between 0 and 1.");
        return;
    }
    if (n <= 0) {
        alert("Sample size (n) must be greater than 0.");
        return;
    }
    if (df !== n - 1) {
        alert("Degrees of freedom (df) should be equal to n - 1.");
        return;
    }

    
    const formData = new FormData();
    formData.append("sample_mean", sample_mean);
    formData.append("population_mean", population_mean);
    formData.append("sample_std", sample_std);
    formData.append("n", n);
    formData.append("alpha", alpha);
    formData.append("df", df);
    formData.append("test_type", test_type);
    const res = await fetch("/populationmean/sigmaunknown", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    
    if (data.error) {
        alert(data.error);
        return;
    }
    if (data.image) {
        document.getElementById("hypothesis-plot").src = "data:image/png;base64," + data.image;
    }
    if (data.df) {
        document.getElementById("hypothesis-result").innerHTML = data.df;
    }
}

