var examples = document.querySelectorAll("ol.example");
var exrefs = document.querySelectorAll("a.exref");

for (var exc = 0; exc <examples.length; exc++){
  ex = examples[exc].children[0]
  ex.setAttribute("value", exc+1)
  var subexamplesol = ex.querySelector("ol.subexample");
  if (subexamplesol){
    subexamples = subexamplesol.children
    for (var subexc = 0; subexc < subexamples.length; subexc++){
      subexamples[subexc].setAttribute("value", subexc+1)
    }
  }
}

function get_example_marker(exid){
  ex = document.getElementById(exid)
  parent = ex.parentElement
  if (parent.getAttribute("class")=="subexample"){
    return "("+parent.parentElement.value+String.fromCharCode(96+ex.value)+")"
  }
  return "("+ex.value+")"
}

exrefs.forEach(function (x, i) { 
  exid = x.getAttribute("exid")
  x.setAttribute("href", "#"+exid)
  x.textContent = get_example_marker(exid)
});
