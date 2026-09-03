let form = document.querySelector("#score-form");

form.addEventListener("submit", function (event) {
    event.preventDefault();


    let mon1 = document.querySelector("#mon1").value;
    let mon2 = document.querySelector("#mon2").value;
    let mon3 = document.querySelector("#mon3").value;
    console.log("mon1", mon1);
    console.log("mon2", mon2);
    console.log("mon3", mon3);

    let totalScore = parseFloat(mon1) + parseFloat(mon2) + parseFloat(mon3);
    console.log("totalScore", totalScore);

    let sum = document.querySelector("#sum");
    sum.textContent = "Total Score: " + totalScore;

});