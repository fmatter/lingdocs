  document.querySelectorAll(".subitems").forEach(function (subitems) {
    if (subitems.children.length == 0) {
      subitems.parentNode.removeChild(subitems);
  }
});
  repl = { "🞃 ": "🞂 ", "🞂 ": "🞃 " };
  function toggleArrow(tog) {
    tog.innerHTML = repl[tog.innerHTML];
}

      var nav = document.getElementById("nav-items"); // get the div holding our eventual table of contents

      function collapse(target) {
        target.classList.remove("active");
        if (target.children[0].classList.contains("toggleWrap")) {
          target.children[0].classList.remove("show");
          toggleArrow(target.children[0].children[0])  
      }
  }

  function expand(target) {
    target.classList.add("active");
    if (target.children[0].classList.contains("toggleWrap")) {
      toggleArrow(target.children[0].children[0])  
      target.children[0].classList.add("show");
  }
}

function modifyTOC(target) {}

window.addEventListener("DOMContentLoaded", () => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        const id = entry.target.getAttribute("id");
        target = document.querySelector(`nav [id="nav-${id}"]`);
        if (entry.intersectionRatio > 0) {
          expand(target);
      } else {
          collapse(target);
      }
  });
  });
        // Track all sections that have an `id` applied
        // document.querySelectorAll("h2, h3, h4, h5, h6").forEach((section) => {
    document.querySelectorAll("section[id]").forEach((section) => {
      observer.observe(section);
  });
});
window.addEventListener("load", () => {
    for (let i of document.querySelectorAll(".collapse ol")) {
      let tog = document.createElement("span");
      tog.classList.add("toggle");
      tog.innerHTML = "🞂 ";
      tog.onclick = function () {
        tog.parentNode.classList.toggle("show");
        toggleArrow(tog);
    };
    i.previousSibling.style = "display: inline;";
    let line = document.createElement("span");
    line.classList.add("toggleWrap");
    line.appendChild(tog);
    line.appendChild(i.previousSibling);
    i.parentElement.insertBefore(line, i);
}
});