async function CalculateCI_twomean_equalvar() {
    var sample_mean1 = parseFloat(document.getElementById("sample_mean1").value);
    var sample_mean2 = parseFloat(document.getElementById("sample_mean2").value);
    var sample_size1 = parseInt(document.getElementById("sample_size1").value);
    var sample_size2 = parseInt(document.getElementById("sample_size2").value);
    var sample_std1 = parseFloat(document.getElementById("sample_std1").value);
    var sample_std2 = parseFloat(document.getElementById("sample_std2").value);
    var alpha_ci = parseFloat(document.getElementById("alpha_ci").value);
    var DF = parseInt(document.getElementById("DF").value);

    // Safety: Ensure numbers are valid
    if (Number.isNaN(sample_size1) || Number.isNaN(sample_size2) || Number.isNaN(DF)) {
        alert("Sample sizes and DF must be valid numbers.");
        return;
    }
    if (Number.isNaN(sample_mean1) || Number.isNaN(sample_mean2) || Number.isNaN(sample_std1) || Number.isNaN(sample_std2) || Number.isNaN(alpha_ci)) {
        alert("Please ensure all inputs are valid numbers.");
        return;
    }
    if (alpha_ci <= 0 || alpha_ci >= 1) {
        alert("Alpha for confidence interval must be between 0 and 1.");
        return;
    }
    if (sample_size1 <= 1 || sample_size2 <= 1) {
        alert("Sample sizes must be greater than 1.");
        return;
    }
    if (sample_std1 <= 0 || sample_std2 <= 0) {
        alert("Sample standard deviations must be positive.");
        return;
    }


    // Check DF formula
    if (DF !== sample_size1 + sample_size2 - 2) {
        alert("DF should be n₁ + n₂ − 2");
        return;
    }

    const formData = new FormData();
    formData.append("sample_mean1", sample_mean1);
    formData.append("sample_mean2", sample_mean2);
    formData.append("sample_size1", sample_size1);
    formData.append("sample_size2", sample_size2);
    formData.append("sample_std1", sample_std1);
    formData.append("sample_std2", sample_std2);
    formData.append("alpha_ci", alpha_ci);
    formData.append("DF", DF);

    const res = await fetch("/populationmean/calculate_ci_popmean_varequal", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    if (data.CI) {
        const el = document.getElementById("ci-result");

        el.innerHTML = `
            ME = ${data.ME}<br>
            CI = (${data.CI[0].toFixed(4)}, ${data.CI[1].toFixed(4)})<br>
            \\( t_{\\alpha/2} \\) = ${data.t_alpha}
        `;

        el.style.fontSize = "25px";
       
        el.style.textAlign = "left";

        MathJax.typesetPromise([el]);
    }

}








async function hypotesting_twomeans_equalvar() {
    var sample_mean1 = parseFloat(document.getElementById("hypo_sample_mean1").value);
    var sample_mean2 = parseFloat(document.getElementById("hypo_sample_mean2").value);
    var sample_size1 = parseInt(document.getElementById("hypo_sample_size1").value);
    var sample_size2 = parseInt(document.getElementById("hypo_sample_size2").value);
    var sample_std1 = parseFloat(document.getElementById("hypo_sample_std1").value);
    var sample_std2 = parseFloat(document.getElementById("hypo_sample_std2").value);
    var alpha_ci = parseFloat(document.getElementById("hypo_alpha_ci").value);
    var DF = parseInt(document.getElementById("hypo_DF").value);
    var type = document.getElementById("Type").value;

    // Safety: Ensure numbers are valid
    if (Number.isNaN(sample_size1) || Number.isNaN(sample_size2) || Number.isNaN(DF)) {
        alert("Sample sizes and DF must be valid numbers.");
        return;
    }
    if (Number.isNaN(sample_mean1) || Number.isNaN(sample_mean2) || Number.isNaN(sample_std1) || Number.isNaN(sample_std2) || Number.isNaN(alpha_ci)) {
        alert("Please ensure all inputs are valid numbers.");
        return;
    }
    if (sample_size1 <= 1 || sample_size2 <= 1) {
        alert("Sample sizes must be greater than 1.");
    return;
    }

    if (alpha_ci <= 0 || alpha_ci >= 1) {
        alert("Alpha for confidence interval must be between 0 and 1.");
        return;
    }
    if (sample_std1 <= 0 || sample_std2 <= 0) {
        alert("Sample standard deviations must be positive.");
        return;
    }

    // Check DF formula
    if (DF !== sample_size1 + sample_size2 - 2) {
        alert("DF should be n₁ + n₂ − 2");
        return;
    }

    const formData = new FormData();
    formData.append("sample_mean1", sample_mean1);
    formData.append("sample_mean2", sample_mean2);
    formData.append("sample_size1", sample_size1);
    formData.append("sample_size2", sample_size2);
    formData.append("sample_std1", sample_std1);
    formData.append("sample_std2", sample_std2);
    formData.append("alpha", alpha_ci);
    formData.append("DF", DF);
    formData.append("type", type)

    const res = await fetch("/populationmean/twopopmeans_equalvar", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    if (data.test_type) {
        const el = document.getElementById("ci-result-hypo");
        el.style.fontSize = "25px";
       
        el.style.textAlign = "left";

        el.innerHTML = `
            \\[
            \\begin{aligned}
            \\text{p-value} &= ${data.p_value} \\\\
            \\alpha &= ${data.alpha} \\\\
            t_{\\text{crit}} &= ${data.test_type === "two-tailed" ? "\\pm" : ""} ${data.t_crit} \\\\
            t_{\\text{test}} &= ${data.t_test}
            \\end{aligned}
            \\]
            `;


        MathJax.typesetPromise([el]);
    }
   
    if (data.image) {
        document.getElementById("twopopmeans-varequal-plot").src = "data:image/png;base64," + data.image;
    }

}
