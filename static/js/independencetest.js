let rowCount = 2;
let colCount = 2;

/* ---------- ADD ROW ---------- */
function addRow() {
    rowCount++;
    const tbody = document.querySelector("#dataTable tbody");
    const row = document.createElement("tr");
    row.style = "width:150px; border-radius:5px;";

    // Row heading input
    const th = document.createElement("th");
    const rowInput = document.createElement("input");
    rowInput.style = "width:150px; border-radius:5px;";
    rowInput.value = `Row ${rowCount}`;
    th.appendChild(rowInput);
    row.appendChild(th);

    // Data cells
    for (let i = 0; i < colCount; i++) {
        const td = document.createElement("td");
        const input = document.createElement("input");
        input.style = "width:150px; border-radius:5px;";
        input.type = "number";
        td.appendChild(input);
        row.appendChild(td);
    }

    tbody.appendChild(row);
}

/* ---------- DELETE ROW ---------- */
function deleteRow() {
    const tbody = document.querySelector("#dataTable tbody");
    if (tbody.rows.length > 1) {
        tbody.deleteRow(-1);
        rowCount--;
    } else {
        alert("At least one row must remain.");
    }
}

/* ---------- ADD COLUMN ---------- */
function addColumn() {
    colCount++;
    const table = document.getElementById("dataTable");

    // Column heading input
    const headerRow = table.querySelector("thead tr");
    const th = document.createElement("th");
    const colInput = document.createElement("input");
    colInput.value = `Col ${colCount}`;
    colInput.style = "width:150px; border-radius:5px;";
    th.appendChild(colInput);
    headerRow.appendChild(th);

    // Data cells
    const rows = table.querySelectorAll("tbody tr");
    rows.forEach(row => {
        const td = document.createElement("td");
        const input = document.createElement("input");
        input.style = "width:150px; border-radius:5px;";
        input.type = "number";
        td.appendChild(input);
        row.appendChild(td);
    });
}

/* ---------- DELETE COLUMN ---------- */
function deleteColumn() {
    if (colCount > 1) {
        const table = document.getElementById("dataTable");
        table.querySelector("thead tr").deleteCell(-1);

        const rows = table.querySelectorAll("tbody tr");
        rows.forEach(row => row.deleteCell(-1));

        colCount--;
    } else {
        alert("At least one column must remain.");
    }
}









let result = {};

async function sendTableData() {
    const table = document.getElementById("dataTable");
    const alpha = parseFloat(document.getElementById("alpha").value);
    const loadingDiv = document.getElementById("loading");
    // Columns labels
    const colLabels = [];
    table.querySelectorAll("thead th input").forEach(input => {
        colLabels.push(input.value);
    })
    // Row labels and data
    const rows = table.querySelectorAll("tbody tr");
    const rowLabels = [];
    const data = [];

    

    rows.forEach(row => {
        rowLabels.push(row.querySelector("th input").value);
        const rowData = [];
        row.querySelectorAll("td input").forEach(input => {
            rowData.push(parseFloat(input.value));
        });
        data.push(rowData);
    });

    const payload = {
        colLabels: colLabels,
        rowLabels: rowLabels,
        data: data, 
        alpha: alpha
    };      


    loadingDiv.style.display = "block";

    try{
        const response = await fetch("/chisquare/independence-test", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        }); 
        result = await response.json();
    } catch (error) {
        console.error(err);
        alert("Upload Failed!");
    } finally {
        loadingDiv.style.display = "none";
    }
    document.getElementById("result").innerHTML = "Observed Frequencies <br>" + result.observed_df;
    
    
}




function showOutput(type) {
    let div;
    if (!result || Object.keys(result).length === 0) {
        alert("Please fill in the contingency table above first and click 'Calculate'.");
        return;
    }

    switch (type) {
        case "critical":
            div = document.getElementById("critical");
            div.innerHTML = `
                <strong>Chi-Square Test Statistics</strong> = ${result.chi2_stat}<br>
                <strong> Chi-Square Critical Value</strong> = ${result.chi2_crit}<br>
                <strong> P-value</strong> = ${result.p_value}<br>
                <strong> Significance Level, α = ${result.alpha}<br>
                <strong> Degrees of Freedom</strong> = ${result.dof}
            `;
            break;

        case "observed":
            div = document.getElementById("observed");
            div.innerHTML = `<h4>Observed Frequencies</h4>${result.observed_df}`;
            break;

        case "expected":
            div = document.getElementById("expected");
            div.innerHTML = `<h4>Expected Frequencies</h4>${result.expected_df}`;
            div.style.textAlign = "center";
            break;

        case "plot":
            div = document.getElementById("plot");
            div.innerHTML = `
                <h4>Observed vs Expected</h4>
                <img src="data:image/png;base64,${result.image}" class="img-fluid">
            `;
            break;

        case "chi_plot":
            div = document.getElementById("chi_plot");
            div.innerHTML = `
                <h4>Chi-Square Distribution</h4>
                <img src="data:image/png;base64,${result.image_chi}" class="img-fluid">
            `;
            break;
    }

    // 🔑 only show THIS output — do NOT hide others
    div.style.display = "block";
}

