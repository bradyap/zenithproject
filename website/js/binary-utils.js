m

function toDecimal() {
    var binary = document.forms["binaryToDecimal"]["input"].value;
    var out = parseInt(binary, 2);
    return out
}

function toBinary() {
    var input = document.forms["binaryToDecimal"]["input"].value;
    var out = input.toString(2);
    return out
}