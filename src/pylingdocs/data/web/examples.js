function number_examples() {
    console.log("Numbering examples")
    var examples = document.querySelectorAll("li.example");
    var exrefs = document.querySelectorAll("a.exref");
    for (var exc = 0; exc < examples.length; exc++) {
        ex = examples[exc]
        ex.setAttribute("value", exc + 1)
        var subexamplesol = ex.querySelector("ol.subexample");
        if (subexamplesol) {
            subexamples = subexamplesol.children
            for (var subexc = 0; subexc < subexamples.length; subexc++) {
                subexamples[subexc].setAttribute("value", subexc + 1)
            }
        }
    }
    exrefs.forEach(function(x, i) {
        example_id = x.getAttribute("example_id")
        x.setAttribute("href", "#" + example_id)
        x.textContent = "("+get_example_marker(example_id)
        if (x.hasAttribute("end")) {
            end = x.getAttribute("end")
            x.textContent += "-" + get_example_marker(end)
        }
        if (x.hasAttribute("suffix")) {
            x.textContent += x.getAttribute("suffix")
        }
        x.textContent += ")"
    });
}


function get_example_marker(example_id) {
    ex = document.getElementById(example_id)
    if (ex != null) {
        parent = ex.parentElement
        if (parent.getAttribute("class") == "subexample") {
            return parent.parentElement.value + String.fromCharCode(96 + ex.value)
        }
    return ex.value
    } else {
        console.log("Can't find example with the ID " + example_id)
    }
}