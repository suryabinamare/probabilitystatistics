function addPair() {
  const div = document.createElement("div");
  div.className = "pair";
  div.innerHTML = `
    <input type="number" step="any" class="x" placeholder="x" style="width: 150px; border-radius:5px;">
    <input type="number" step="any" class="y" placeholder="y" style="width: 150px; border-radius:5px;">
  `;
  document.getElementById("pairs").appendChild(div);
}

function removePair() {
  const pairsDiv = document.getElementById("pairs");
  if (pairsDiv.children.length >1) {
    pairsDiv.removeChild(pairsDiv.lastChild)
  }
  else {    alert("At least one pair must remain.");
  }

}


let result = {};
// Send x,y values
async function submitXY() {
  const xValues = Array.from(document.querySelectorAll(".x"))
    .map(input => parseFloat(input.value));

  const yValues = Array.from(document.querySelectorAll(".y"))
    .map(input => parseFloat(input.value));

  if (xValues.length === 0 || yValues.length === 0) {
  alert("Please enter x and y values.");
  return;
}


  if (xValues.length !== yValues.length) {
    alert("x and y must have same length");
    return;
  }

  const response = await fetch("/linear/descriptive", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      action: "plot",
      x: xValues,
      y: yValues
    })
  });
  result = await response.json();
}





// Upload file
async function uploadFile() {
  const fileInput = document.getElementById("fileInput");
  const loadingDiv = document.getElementById("loading");

  if (!fileInput.files.length) {
    alert("Please select a file");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  formData.append("action", "plot1");

  loadingDiv.style.display = "block";

  try {
    const response = await fetch("/linear/descriptive", {
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
  } finally {
    loadingDiv.style.display = "none";
  }
}









function showValues(type) {
    let div;
    if (!result || Object.keys(result).length === 0) {
        alert("Please submit data first.");
        return;
    }
    switch (type) {
      case "data":
          div = document.getElementById("displayData");
          div.innerHTML = result.df;
          break;
      case "scatterplot":
          div = document.getElementById("scatterPlot");
          div.innerHTML = `<img src="data:image/png;base64,${result.img_scatter}" class="img-fluid">`;         
          break;
      case "equations":
          div = document.getElementById("regressionEquation");
          div.innerHTML = `
            <strong> Regression Equation: </strong>${result.equation}<br>
            <strong> x̄ =</strong> ${result.values[0]}<br>
            <strong> ȳ =</strong> ${result.values[1]}<br>
            <strong> Sxx =</strong> ${result.values[2]}<br>
            <strong> Syy =</strong> ${result.values[3]}<br>
            <strong> Sxy =</strong> ${result.values[4]}<br>
            <strong> m =</strong> ${result.values[5]}<br>
            <strong> b =</strong> ${result.values[6]}<br>
            <strong> R² =</strong> ${result.values[7]}<br>
            <strong> r =</strong> ${result.values[8]}<br>
            <strong> SE =</strong> ${result.values[9]}<br>
            <strong> SSE =</strong> ${result.values[10]}<br>`;
          div.style.paddingLeft = "50px";
          div.style.fontSize = "18px";
          break;

      case "regressionplot":
          div = document.getElementById("regressionPlot");
          div.innerHTML = `<img src="data:image/png;base64,${result.img_regression}" class="img-fluid">`;
          break;
      case "residualsplot":
          div = document.getElementById("residualsPlot");
          div.innerHTML = `<img src="data:image/png;base64,${result.img_residuals}" class="img-fluid">`;
          break;
      case "qqplot":
          div = document.getElementById("qqPlot");
          div.innerHTML = `<img src="data:image/png;base64,${result.img_qq}" class="img-fluid">`;
          break;
    }
    div.style.display = "block";

}