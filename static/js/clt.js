async function drawCLTPlot() {
    var dist = document.getElementById("dist_select").value;
    var sample_size = parseInt(document.getElementById("sample_size").value);
    var num_samples = parseInt(document.getElementById("num_samples").value);
    if (isNaN(sample_size) || isNaN(num_samples)) {
        alert("Please enter valid numeric values for sample size and number of samples.");
        return;
    }
    if (sample_size <= 0) {
        alert("Sample size (n) must be greater than 0.");
        return;
    }
    if (num_samples <= 0) {
        alert("Number of samples must be greater than 0.");
        return;
    }

    const formData = new FormData();
    formData.append("dist", dist);
    formData.append("sample_size", sample_size);
    formData.append("num_samples", num_samples);
    const res = await fetch("/clt/draw_clt_plot", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    if (data.error) {
        alert(data.error);
        return;
    }
    document.getElementById("clt-plot").src = "data:image/png;base64," + data.plot_url;
}
