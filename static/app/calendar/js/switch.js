function checkForm(){

    // Get the checkbox

    var checkBox = document.getElementById("checkForm");

    // Get the output text
    var daysOn = document.getElementById("daysOn");
    var daysOff = document.getElementById("daysOff");

    // If the checkbox is checked, display the output text

    if (checkBox.checked == true){
        daysOn.style.display = "none";
        daysOff.style.display = "block";

    } else {
        daysOn.style.display = "block";
        daysOff.style.display = "none";
    } 

}