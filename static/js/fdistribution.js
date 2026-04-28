








//**************************************************************************************************************************






//**************************************************************************************************************************
// F-distribution functions

async function drawFDistribution() {
    const dfn = document.getElementById("df1_plot").value;
    const dfd = document.getElementById("df2_plot").value;
    if (dfn.trim() === "" || dfd.trim() === "") {
        alert("Please enter both degrees of freedom (dfn and dfd) to draw the F-distribution curve.");
        return;
    }
    const dfn_num = Number(dfn);
    const dfd_num = Number(dfd);
    if (isNaN(dfn_num) || isNaN(dfd_num) || dfn_num <= 0 || dfd_num <= 0) {
        alert("Degrees of freedom must be positive numbers.");
        return;
    }

    const formData = new FormData();
    formData.append("dfn", dfn);
    formData.append("dfd", dfd);
    const res = await fetch("/distributions/add_f_curve", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    if (data.error) {
        alert(data.error);
        return;
    }
    if (data.img) {
        document.getElementById("f-plot").src = "data:image/png;base64," + data.img;
    }
}


async function resetFPlot() {
    const res = await fetch("/distributions/reset_f", {
        method: "POST"
    });
    const data = await res.json();
    document.getElementById("f-plot").src = "data:image/png;base64," + data.img;
}



async function calculateFDistribution() {
    const f_score = document.getElementById("fscore_input").value;
    const dfn = document.getElementById("df1_input").value;
    const dfd = document.getElementById("df2_input").value;
    if (dfn.trim() === "" || dfd.trim() === "" || f_score.trim() === "" ){ 
        alert("Please fill in all required fields.");
        return;
    }
    if (parseFloat(f_score) < 0) {
        alert("F-score must be a non-negative number.");
        return;
    }
    if (parseFloat(dfn) <= 0 || parseFloat(dfd) <= 0) {
        alert("Degrees of freedom must be positive numbers.");
        return;
    }
    const dfnNum = Number(dfn);
    const dfdNum = Number(dfd);

    if (!Number.isInteger(dfnNum) || !Number.isInteger(dfdNum)) {
        alert("Degrees of freedom must be integers.");
        return;
    }


    const formData = new FormData();
    formData.append("f_given", f_score);
    formData.append("dfn_given", dfn);
    formData.append("dfd_given", dfd);
    
    const res = await fetch("/distributions/fdistribution", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    
    if (data.error) {
        alert(data.error);
        return;
    }
    if (data.img) {
        document.getElementById("p-value-result").innerHTML = 
        `<br> <br><strong>P-value = </strong> ${data.p_value.toFixed(4)}`;
        document.getElementById("p-value-plot").src = "data:image/png;base64," + data.img;
    }
    
}   






async function calculateFValue() {
    const p_value = document.getElementById("pvalue_input1").value;
    const dfn = document.getElementById("df1_input1").value;
    const dfd = document.getElementById("df2_input1").value;
    if (dfn.trim() === "" || dfd.trim() === "" || p_value.trim() === "" ){ 
        alert("Please fill in all required fields.");
        return;
    }
    if (parseFloat(p_value) <= 0 || parseFloat(p_value) >= 1) {
        alert("P-value must be between 0 and 1.");
        return;
    }
    if (parseFloat(dfn) <= 0 || parseFloat(dfd) <= 0) {
        alert("Degrees of freedom must be positive numbers.");
        return;
    }
    const dfnNum = Number(dfn);
    const dfdNum = Number(dfd);
    if (!Number.isInteger(dfnNum) || !Number.isInteger(dfdNum)) {
        alert("Degrees of freedom must be integers.");
        return;
    }
    const formData = new FormData();
    formData.append("p_given", p_value);
    formData.append("dfn_given", dfn);
    formData.append("dfd_given", dfd);
    const res = await fetch("/distributions/fdistribution_value", {
        method: "POST",
        body: formData  
    });
    const data = await res.json();
    
    if (data.error) {
        alert(data.error);
        return;
    }
    if (data.img) {
        document.getElementById("f-value-result").innerHTML = 
        `<br> <br><strong>F-value = </strong> ${data.f_value.toFixed(4)}`;
        document.getElementById("f-value-plot").src = "data:image/png;base64," + data.img;
    }
}
