function togglePasswordVisibility() {
    var pass = document.getElementById("togleable");
    if (pass != null)
    if (pass.type == "password") {
        pass.type = "text";
    } else {
        pass.type = "password";
    }
}   