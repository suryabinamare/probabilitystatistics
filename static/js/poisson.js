
async function plot_poisson() {
    const lambda = Number(document.getElementById("lambda_plot").value);
    if (isNaN(lambda)) {
        alert("Please enter a numeric value for λ.");
        return;
    }
    if (lambda <= 0) {
        alert("Please enter a valid mean (λ) greater than 0.");
        return;
    }
    const formData = new FormData();
    formData.append("lambda", lambda);
    const res = await fetch("/distributions/plot_poisson", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    if (data.error) {
        alert(data.error);
        return;
    }

    if (data.img) {
        document.getElementById("poisson_histogram").src = "data:image/png;base64," + data.img;
    }
}














async function find_prob() {

    const lambda = Number(document.getElementById("lambda").value);
    const k = Number(document.getElementById("prob_k").value);
    if (isNaN(lambda) || isNaN(k)) {
        alert("Please enter numeric values only.");
        return;
    }
    if (lambda <= 0) {
        alert("Please enter a valid mean (λ) greater than 0.");
        return;
    }   
    if (k < 0) {
        alert("Please enter a valid number of successes (k) greater than or equal to 0.");
        return;
    }
    formData = new FormData();
    formData.append("lambda", lambda);
    formData.append("k", k);
    const res = await fetch("/distributions/find_poisson_prob", {
        method: "POST",
        body: formData
    });
    const data1 = await res.json();
    if (data1.error) {
        alert(data1.error);
        return;
    }
    const resultContainer = document.getElementById("prob-result-container");
    resultContainer.innerHTML = `
        <h4>Results:</h4>
        <p>Mean (λ) = ${data1.mean}</p>
        <p>Standard Deviation (σ) = ${data1.std}</p>      
    `;
    MathJax.typeset();

    const resultContainer1 = document.getElementById("probability-result");
    resultContainer1.innerHTML = data1.data_values;
    MathJax.typeset();
}