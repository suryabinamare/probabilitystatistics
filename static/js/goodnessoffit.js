function addRow() {
  const container = document.getElementById("fitness_test");

  const row = document.createElement("div");
  row.className = "goodness_test";

  row.innerHTML = `

    <input type="number" step="any"
           placeholder="Expected Distribution"
           class="expected"
           style="width:200px; border-radius:5px;" />

    &nbsp;&nbsp;
    <input type="number" step="any"
           placeholder="Observed Frequency"
           class="observed"
           style="width:200px; border-radius:5px;" />

    &nbsp;&nbsp;

    

    <button type="button"
            onclick="removeRow(this)"
            class="remove-button">✖</button>
    <br><br>
  `;

  container.appendChild(row);
}




function removeRow(button) {
  const container = document.getElementById("fitness_test");
  const rows = container.getElementsByClassName("goodness_test");

  // Prevent deleting the last row
  if (rows.length <= 1) {
    alert("At least one row is required.");
    return;
  }

  button.closest(".goodness_test").remove();
}












async function calculateGoodnessFit() {
  const observedInputs = document.querySelectorAll(".observed");
  const expectedInputs = document.querySelectorAll(".expected");
  const alpha = parseFloat(document.getElementById("alpha").value);

  let observedValues = [];
  let expectedValues = [];

  if (observedInputs.length < 2) {
    alert("At least two rows are required for a chi-square test.");
    return;
  }
  if (isNaN(alpha) || alpha <= 0 || alpha >= 1) {
    alert("Significance level (alpha) must be between 0 and 1.");
    return;
  }

  for (let i = 0; i < observedInputs.length; i++) {
    const oVal = observedInputs[i].value.trim();
    const eVal = expectedInputs[i].value.trim();

    // Skip completely empty rows
    if (oVal === "" && eVal === "") {
      continue;
    }

    // One filled but not the other
    if (oVal === "" || eVal === "") {
      alert(`Row ${i + 1}: both observed and expected values are required.`);
      return;
    }

    const o = parseFloat(oVal);
    const e = parseFloat(eVal);

    if (isNaN(o) || isNaN(e)) {
      alert(`Row ${i + 1}: values must be numeric.`);
      return;
    }

    if (o < 0) {
      alert(`Row ${i + 1}: observed frequency cannot be negative.`);
      return;
    }

    if (e <= 0 || e >= 1) {
      alert(`Row ${i + 1}: expected frequency must be between 0 and 1.`);
      return;
    }

    observedValues.push(o);
    expectedValues.push(e);
  }

  if (observedValues.length < 2) {
    alert("At least two valid rows are required.");
    return;
  }

  try {
    const response = await fetch("/chisquare/goodnessfit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ observedValues, expectedValues, alpha  }),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error || "Server error");
    }

    const result = await response.json();

    document.getElementById("result").innerHTML = `
      <strong>Values:</strong> ${result.DF}<br>
      <strong>Chi-Square Statistic:</strong> ${result.chi2_stat}<br>
      <strong>Critical Value:</strong> ${result.chi2_crit}<br>
      <strong>Significance Level (Alpha):</strong> ${result.alpha}<br>
      <strong>P-Value:</strong> ${result.p_value}<br>
      
    `;
    document.getElementById("chi2plot").src = `data:image/png;base64,${result.image}`;    
  } catch (err) {
    alert(err.message || "Error calculating goodness of fit.");
    console.error(err);
  }
}
