async function calculate_ci_oneprop() {

    const sample_size = parseInt(
        document.getElementById("sample_size1").value
    );

    const proportion = parseFloat(
        document.getElementById("sample_prop1").value
    );

    const alpha = parseFloat(
        document.getElementById("alpha1").value
    );

    const formData = new FormData();
    formData.append("sample_size", sample_size);
    formData.append("proportion", proportion);
    formData.append("alpha", alpha);

    const res = await fetch("/populationproportion/calculate_ci_proportion1", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    if (data.CI) {
        const el = document.getElementById("ci-result-proportion1");
        el.innerHTML = `
        CI = (${data.CI[0]},  ${data.CI[1]}) <br>
        ME = ${data.ME} <br>
        Critical Value = 
        \\(z_{\\alpha/2} \\) = ${data.z_alpha} <br>
        
        `;
        el.style.fontSize = "25px";
        el.style.textAlign = "center";
        el.style.fontWeight = "bold";
        MathJax.typesetPromise([el]);
        
    }
    if (data.image) {
        document.getElementById("proportion1-plot").src = "data:image/png;base64," + data.image;
    }
}













async function calculate_ht_oneprop() {
    const sample_size = parseInt(
        document.getElementById("sample_size_ht1").value
    );
    const proportion = parseFloat(
        document.getElementById("sample_prop_ht1").value
    );
    const null_prop = parseFloat(
        document.getElementById("null_prop_ht1").value
    );
    const alpha = parseFloat(
        document.getElementById("alpha_ht1").value
    );
    const test_type = document.getElementById("test_type").value;
    const formData = new FormData();
    formData.append("sample_size", sample_size);
    formData.append("sample_proportion", proportion);
    formData.append("null_prop", null_prop);
    formData.append("alpha", alpha);
    formData.append("test_type", test_type);
    const res = await fetch("/populationproportion/proportion1_ht", {
        method: "POST",
        body: formData
    }); 
    const data = await res.json();

    if (data.error) {
        alert(data.error);
        return;
    }   
    if (data.z) {
        const el = document.getElementById("proportion-ht1-result");
        el.innerHTML = `
        Test Statistic (z) = ${data.z} <br>
        Critical Value (z) = ${data.z_alpha} <br>
        P-value = ${data.p_value} <br>  
        \\( \\alpha\\) = ${data.alpha}
        `;
        el.style.fontSize = "25px";
        el.style.textAlign = "center";
        el.style.fontWeight = "bold";
        MathJax.typesetPromise([el]);
    }
    if (data.image) {
        document.getElementById("proportion-ht1-plot").src = "data:image/png;base64," + data.image;
    }
}
    







async function calculate_n() {
    const me = parseFloat(document.getElementById("me").value);
    const p_hat = parseFloat(document.getElementById("p_hat_estimate").value);
    const alpha = parseFloat(document.getElementById("sig_level").value);
    if (isNaN(me) || isNaN(alpha) || isNaN(p_hat)) {
        alert("Please enter valid numeric values for ME, significance level, and estimated proportion.");
        return;
    }
    if (me <= 0) {
        alert("Margin of error (ME) must be greater than 0.");
        return;
    }

    if (p_hat < 0 || p_hat > 1) {
        alert("Estimated proportion (p̂) must be between 0 and 1.");
        return;
    }


    if (alpha <= 0 || alpha >= 1) {
        alert("Significance level (α) must be between 0 and 1.");
        return;
    }   
    newData = new FormData();
    newData.append("me", me);
    newData.append("alpha", alpha);
    newData.append("p_hat", p_hat);
    const res = await fetch("/populationproportion/calculate_n", {
        method: "POST",
        body: newData
    });
    const data = await res.json();
    if (data.error) {
        alert(data.error);
        return;
    }
    if (data.sample_size) {
        const el = document.getElementById("sample-size-result");
        el.innerHTML = `
        Required Sample Size (n) = ${data.sample_size}
        `;
        el.style.fontSize = "25px";
        el.style.textAlign = "center";
        el.style.fontWeight = "bold";
    }   

}