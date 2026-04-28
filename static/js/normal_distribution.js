async function addCurve() {
    const mean = document.getElementById("mean").value;
    const std = document.getElementById("std").value;

    const formData = new FormData();
    formData.append("mean", mean);
    formData.append("std", std);

    const res = await fetch("/distributions/add_curve", {
        method: "POST",
        body: formData
    });

    const data = await res.json();
    document.getElementById("plot").src = "data:image/png;base64," + data.img;
}

async function resetPlot() {
    const res = await fetch("/distributions/reset", {
        method: "POST"
    });

    const data = await res.json();
    document.getElementById("plot").src = "data:image/png;base64," + data.img;
}





async function p_value() {
    const z_value = document.getElementById("z-value").value;
    if (z_value.trim() === "") {
        alert("Please enter a z-score value.");
        return;
    }
    const formData = new FormData();
    formData.append("z_given", z_value);
    
    const res = await fetch("/distributions/zdistribution", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    if (data.error) {
        alert(data.error);
    } else {
       
        // Update text (do NOT delete the img)
    document.getElementById("zp-results").innerHTML = 
        `<br> <p><strong>Area to the left of z = ${z_value} is </strong> ${data.p_value.toFixed(4)}</p>
        <p><strong>Area to the right of z = ${z_value} is </strong> ${data.p_value_bigger.toFixed(4)}</p><br>`;
    document.getElementById("zp-plot").src = "data:image/png;base64," + data.img;
   
    }
}




async function z_value() {
    const p_value = document.getElementById("p-value").value;
    area_type = document.getElementById("area-type").value;
    if (p_value.trim() === "") {
        alert("Please enter a p-value.");
        return;
    }
    if (p_value <= 0 || p_value >= 1) {
        alert("Please enter a valid p-value between 0 and 1.");
        return;
    }
    const formData = new FormData();
    formData.append("p_given", p_value);
    formData.append("area_type", area_type);
    const res = await fetch("/distributions/zvalue", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    if (data.error) {
        alert(data.error);
    } else {
    document.getElementById("zp-results11").innerHTML = 
        `<br> <p><strong>z-value corresponding to p = ${p_value} to the ${area_type} is  =  </strong> ${data.z_value.toFixed(4)}</p><br>`;
    document.getElementById("zp-plot11").src = "data:image/png;base64," + data.img;
    }
}




async function findProbabilities() {
    const mean = document.getElementById("mu").value;
    const std = document.getElementById("sigma").value;
    const x_value = document.getElementById("x-value").value;
    if (mean.trim() === "" || std.trim() === "" || x_value.trim() === "") {
        alert("Please fill in all fields.");
        return;
    }
    if (std <= 0) {
        alert("Standard deviation must be positive.");
        return;
    }
    const formData = new FormData();
    formData.append("mean", mean);
    formData.append("std", std);
    formData.append("x_value", x_value);
    const res = await fetch("/distributions/find_probabilities", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    if (data.error) {
        alert(data.error);
    } else {
        // Update text (do NOT delete the img)
    document.getElementById("zp-results1").innerHTML = 
        `<br><br> <p><strong>P(X < ${x_value}) = </strong> ${data.p_less_than.toFixed(4)}</p>
        <p><strong>P(X > ${x_value}) = </strong> ${data.p_greater_than.toFixed(4)}</p>`;



    document.getElementById("prob_values").src = "data:image/png;base64," + data.img;
    }
}