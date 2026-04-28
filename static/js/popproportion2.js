async function calculate_ci_twoprop() {
    const n1 = parseFloat(document.getElementById("n1").value);
    const p1 = parseFloat(document.getElementById("p1").value);
    const n2 = parseFloat(document.getElementById("n2").value);
    const p2 = parseFloat(document.getElementById("p2").value);
    const alpha = parseFloat(document.getElementById("alpha1").value); 
    
    const formData = new FormData();
    formData.append("n1", n1);
    formData.append("p1", p1);
    formData.append("n2", n2);
    formData.append("p2", p2);
    formData.append("alpha", alpha);

    const res = await fetch("/populationproportion/calculate_ci_twoprop", {
        method: "POST",
        body: formData
     });
    const data = await res.json();
    if (data.error) {
        alert(data.error);
        return;
    }
    if (data.CI) {
        const el = document.getElementById("ci-result-proportion2");
        el.innerHTML = `
        Confidence Interval = (${data.CI[0]}, ${data.CI[1]})<br>
        Margin of Error = ${data.ME} <br>
        Critical Value = ${data.z_alpha} <br>  
        `;
        el.style.fontSize = "20px";
        el.style.textAlign = "center";
        el.style.fontWeight = "bold";
        MathJax.typesetPromise([el]);

    }
    if (data.image) {
        document.getElementById("proportion2-plot").src = "data:image/png;base64," + data.image;
    }
}








async function calculate_ht_twoprop() {
    const n1 = parseInt(document.getElementById("sample_size1").value);
    const p1 = parseFloat(document.getElementById("sample_prop1").value);
    const n2 = parseInt(document.getElementById("sample_size2").value);
    const p2 = parseFloat(document.getElementById("sample_prop2").value);
    const alpha = parseFloat(document.getElementById("alpha").value);
    const test_type = document.getElementById("test_type").value;

    if (p1 < 0 || p1 > 1 || p2 < 0 || p2 > 1) {
    alert("Sample proportions must be between 0 and 1.");
    return;}

    const formData = new FormData();
    formData.append("n1", n1);
    formData.append("p1", p1);
    formData.append("n2", n2);
    formData.append("p2", p2);
    
    formData.append("alpha", alpha);
    formData.append("test_type", test_type);
    const res = await fetch("/populationproportion/calculate_ht_twoprop", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    if (data.error) {
        alert(data.error);
        return;
    }   
    if (data.z) {
        const el = document.getElementById("proportion-ht2-result");
        el.innerHTML = `
        Test Statistic = ${data.z}<br>
        Critical Value = ${data.z_alpha}<br>
        p-value = ${data.p_value}<br>
        \\( \\alpha \\) = ${data.alpha}<br>
        `;
        el.style.fontSize = "20px";
        el.style.textAlign = "center";
        el.style.fontWeight = "bold";
        MathJax.typesetPromise([el]);
    }
    if (data.image) {
        document.getElementById("proportion-ht2-plot").src = "data:image/png;base64," + data.image;
    }
}