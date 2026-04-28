
function updaten()
{
    var n = document.getElementById("n").value;
    document.getElementById("samplesize").innerText = n;
}

const n_slider = document.getElementById("n");
n_slider.oninput = updaten;

async function calculateCI() {
    // Get input values
    var mu0 = parseFloat(document.getElementById("mu0").value);
    var sigma = parseFloat(document.getElementById("sigma_ci").value);
    var alpha = parseFloat(document.getElementById("alpha_ci").value);
    var n = parseInt(document.getElementById("n").value);

    if (isNaN(mu0) || isNaN(sigma) || isNaN(alpha) || isNaN(n)) {
        alert("Please enter valid numeric values for all fields.");
        return;
    }

    if (sigma <= 0) {
        alert("Standard deviation (σ) must be greater than 0.");
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


    const formData = new FormData();
    formData.append("mu0", mu0);
    formData.append("sigma", sigma);
    formData.append("alpha", alpha);
    formData.append("n", n);
    const res = await fetch("/populationmean/calculate_ci", {
        method: "POST",
        body: formData
    });

    const data = await res.json();
    
    if (data.error) {
        alert(data.error);
        return;
    }
    if (data.plot) {
        document.getElementById("ci-plot").src = "data:image/png;base64," + data.plot;
    }   
    if (data.ci_result) {
        document.getElementById("ci-result").innerHTML =  
            `CI =  [${data.ci_result[0].toFixed(4)}, ${data.ci_result[1].toFixed(4)}]
            <br>
            ME =  ${data.me.toFixed(4)}`;
        document.getElementById("ci-result").style.textAlign = "center"; // CENTER
        document.getElementById("ci-result").style.fontSize = "20px";   // BIG
        document.getElementById("ci-result").style.fontWeight = "bold"; // BOLD
        
    }
}








// Hypothesis Testing for Population Mean (σ known)
async function hypothesis_testing_sigmaknown()  { 
    // Get input values
    var sample_mean = parseFloat(document.getElementById("sample_mean").value);
    var population_mean = parseFloat(document.getElementById("population_mean").value);
    var sigma = parseFloat(document.getElementById("sigma").value);
    var n = parseInt(document.getElementById("sample_size").value);
    var alpha = parseFloat(document.getElementById("alpha").value);
    var test_type = document.getElementById("Type").value;
    if (isNaN(sample_mean) || isNaN(population_mean) || isNaN(sigma) || isNaN(n) || isNaN(alpha)) {
        alert("Please enter valid numeric values for all fields.");
        return;
    }
    if (sigma <= 0) {
        alert("Standard deviation (σ) must be greater than 0.");
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

    const formData = new FormData();
    formData.append("sample_mean", sample_mean);
    formData.append("population_mean", population_mean);
    formData.append("sigma", sigma);
    formData.append("n", n);
    formData.append("alpha", alpha);
    formData.append("Type", test_type);
    const res = await fetch("/populationmean/sigmaknown", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    if (data.error) {
        alert(data.error);
        return;
    }
    if (data.image) {
        document.getElementById("ht-plot").src = "data:image/png;base64," + data.image;
    }
    if (data.df) {
        document.getElementById("ht-table").innerHTML = data.df;
    }
 MathJax.typeset();
}






//Sample Size Calculation for Population Mean (σ known)
async function calculateSampleSizeKnown() {
    // Get input values
    var sigma = parseFloat(document.getElementById("sigma_me").value);
    var alpha = parseFloat(document.getElementById("alpha_me").value);
    var me = parseFloat(document.getElementById("me").value);
    if (isNaN(sigma) || isNaN(alpha) || isNaN(me)) {
        alert("Please enter valid numeric values for all fields.");
        return;
    }
    if (sigma <= 0) {
        alert("Standard deviation (σ) must be greater than 0.");
        return;
    }
    if (alpha <= 0 || alpha >= 1) {
        alert("Significance level (α) must be between 0 and 1.");
        return;
    }
    if (me <= 0) {
        alert("Margin of error (ME) must be greater than 0.");
        return;
    }
    
    const formData = new FormData();
    formData.append("sigma", sigma);
    formData.append("alpha", alpha);
    formData.append("me", me);
    const res = await fetch("/populationmean/calculate_sample_size_known", {
        method: "POST",
        body: formData
    });
    const data = await res.json();  
    if (data.error) {
        alert(data.error);
        return;
    }
    if (data.sample_size) {
        document.getElementById("me-n-result").innerText = ' = ' +   data.sample_size;
        document.getElementById("me-n-result").style.fontSize = "30px";   // BIG
        document.getElementById("me-n-result").style.fontWeight = "bold"; // BOLD
    }
}