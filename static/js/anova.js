// Upload file and send to python.














let result = {};

async function uploadCSV() {
    const fileInput = document.getElementById("csvFile");
    const loadingDiv = document.getElementById("loading");

    if (!fileInput.files.length) {
        alert("Please select a file");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    //show loading message
    loadingDiv.style.display = "block";

    try {
        const response = await fetch("/anova/anovaValues", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Server error");
        }

        result = await response.json();
        console.log(result);

    } catch (err) {
        console.error(err);
        alert("Upload failed");
    }
    finally {
        //hide loading message
        loadingDiv.style.display = "none";
    }
}

function calculateAnova(type) {
    if (!result || Object.keys(result).length === 0) {
        alert("Upload data first");
        return;
    }

    let div;

    switch (type) {
        case "display_file":
            div = document.getElementById("fileOutput");
            div.innerHTML = result.data;
            break;
        case "stat_values":
            div = document.getElementById("statOutput");
            div.innerHTML = result.stat_table;
            break;

        case "boxplot":
            div = document.getElementById("boxplotOutput");
            div.innerHTML = `
                <img src="data:image/png;base64,${result.image}" class="img-fluid">
            `;
            break;

        case "anova":
            div = document.getElementById("anovaOutput");
            div.innerHTML = result.anova_table;
            break;
    }

    if (div) div.style.display = "block";
}












//to compute F-value given degrees of numerator, denominator, and alpha
async function findFvalue() {
    const df_num = parseInt(document.getElementById("field1").value);
    const df_deno = parseInt(document.getElementById("field2").value);
    const alpha = parseFloat(document.getElementById("field3").value);

    // Basic validation
    if (!df_num || !df_deno || !alpha) {
        alert("Please enter all values.");
        return;
    }
    
    if (df_num <=0 || df_deno <=0) {
        alert("Degree should be positive integers")
    }
    
    if (alpha <=0 || alpha >= 1) {
        alert("alpha should be between 0 and 1, exclusive")
    }

    try {
        const response = await fetch("/anova/anova1", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                df_num: df_num,
                df_deno: df_deno,
                alpha: alpha
            })
        });

        const result = await response.json();

        if (!response.ok || result.error) {
            throw new Error(result.error || "Failed to compute F value.");
        }

        // Display F value
        document.getElementById("fValueOutput").innerHTML =
            `<strong>Critical F-value = </strong> ${result.f_value}`;

        // Display plot
        document.getElementById("fPlotOutput").innerHTML =
            `<img src="data:image/png;base64,${result.plot_fcurve}" class="img-fluid">
`;

    } catch (err) {
        console.error(err);
        alert("Error computing F-value.");
    }
}
