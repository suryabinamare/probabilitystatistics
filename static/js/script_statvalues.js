async function uploadFile() {
    const file = document.getElementById("fileInput").files[0];
    if (!file) {
        alert("Please select a file!");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch("/statvalues/upload", {
            method: "POST",
            body: formData
        });

        if (!res.ok) {
            throw new Error("Bad response from server");
        }

        const data = await res.json();

        let table = "<h3>The first five rows: </h3>";
        table += data.table_html;
        document.getElementById("uploadOutput").innerHTML =  table;

        let html = "<h3>Select Column</h3>";
        html += "<select id='columnSelect'>";
        data.columns.forEach(c => {
            html += `<option value="${c}">${c}</option>`;
        });
        html += "</select>";

        document.getElementById("columnSelectArea").innerHTML = html;

    } catch (err) {
        console.error("Upload error:", err);
    }
}



async function showMean() {
    const col = document.getElementById("columnSelect").value;

    try {
        const res = await fetch("/statvalues/get_mean", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ col })
        });

        const data = await res.json();

        document.getElementById("meanOutput").innerHTML += 
            `<p> ${data.mean}</p>`;
    } catch (err) {
        console.error("Mean fetch error:", err);
    }
}



async function showBoxplot() {
    const col = document.getElementById("columnSelect").value;

    try {
        const res = await fetch("/statvalues/get_boxplot", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ col })
        });

        const data = await res.json();

        document.getElementById("boxplotOutput").innerHTML += 
            `<p><b>Boxplot of ${col}:</b></p>
             <img src="data:image/png;base64,${data.image}" width="400">`;

    } catch (err) {
        console.error("Boxplot fetch error:", err);
    }
}

async function showNormalplot() {
    const col = document.getElementById("columnSelect").value;

    const res = await fetch ("/statvalues/get_normalplot", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({col})
    });

    const data = await res.json();

    document.getElementById("normalplotoutput").innerHTML += 
    `<p><b>Normal probability plot of ${col}:</b></p>
             <img src="data:image/png;base64,${data.image}" width="600">`;

}


async function showHistogram() {
    const col = document.getElementById("columnSelect").value;
    const res = await fetch ("/statvalues/get_histogram",{
        method: "POST", 
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({col})
    });
    const data = await res.json();
    document.getElementById("histogramoutput").innerHTML += 
    `<p><b>Histogram of ${col}:</b></p>
             <img src="data:image/png;base64,${data.image}" width="400">`;

}





