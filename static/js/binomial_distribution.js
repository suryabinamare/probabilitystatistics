async function addCurveBinomial() {
    const n = document.getElementById("num_trials").value;
    const p = document.getElementById("prob_success").value;
    if (n <= 0 || p <= 0 || p >= 1) {
        alert("Please enter valid inputs: n should be positive and p should be between 0 and 1.");
        return;
    }
    const formData = new FormData();
    formData.append("n", n);
    formData.append("p", p);
    const res = await fetch("/distributions/add_binom_curve", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    if (data.error) {
        alert(data.error);
        return;
    }
    if (data.img) {
        document.getElementById("binomial-plot").src = "data:image/png;base64," + data.img;
    }
}

async function resetBinomialPlot() {
    const res = await fetch("/distributions/reset_binom", {
        method: "POST"
    });
    const data = await res.json();
    document.getElementById("binomial-plot").src = "data:image/png;base64," + data.img;
}


async function find_prob() {

    const k = Number(document.getElementById("prob_k").value);
    const n = Number(document.getElementById("trials").value);
    const p = Number(document.getElementById("prob").value);

    if (isNaN(k) || isNaN(n) || isNaN(p)) {
        alert("Please enter numeric values only.");
        return;
    }

    if (n <= 0 || p <= 0 || p >= 1) {
        alert("Please enter valid inputs: n should be positive and p should be between 0 and 1.");
        return;
    }

    if (k < 0 || k > n) {
        alert("Please enter a valid number of successes (k) between 0 and n.");
        return;
    }

    const formData = new FormData();
    formData.append("k", k);
    formData.append("n", n);
    formData.append("p", p);

    const res = await fetch("/distributions/find_prob", {
        method: "POST",
        body: formData
    });

    const data1 = await res.json();

    if (data1.error) {
        alert(data1.error);
        return;
    }

    if (data1.probability !== undefined) {
        document.getElementById("probability-result").innerHTML = data1.data_values;
    }

    if (data1.data) {
        document.getElementById("prob-result-container").innerHTML = data1.data;
    }

    MathJax.typeset();
}
