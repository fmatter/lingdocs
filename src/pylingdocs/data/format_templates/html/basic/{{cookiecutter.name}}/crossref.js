function get_number_label(counters, level) {
    output = []
    for (var i = 2; i <= level; i++) {
        output.push(counters["h"+i])
    }
    return output.join(".")
}

var stored = {}


function number_sections(){
    var counters = {};
    var levels = ["h2", "h3", "h4", "h5", "h6"];
    levels.forEach(function(x, i) {
        counters[x] = 0
    })
    // assuming that there is a single h1!
    h1 = document.querySelectorAll("h1")[0];
    if (h1.hasAttribute("number")) {
        prefix = h1.getAttribute("number") + "."
    } else {
        prefix = ""
    }
    h1.textContent = prefix+" " + h1.textContent
    var headings = document.querySelectorAll("h2, h3, h4, h5, h6");
    headings.forEach(function(heading, i) {
        var level = heading.tagName.toLowerCase();
        counters[level] += 1
        number = get_number_label(counters, level.charAt(level.length - 1))
        heading.textContent = prefix + number + ". " + heading.textContent
        // reset the smaller counters
        reached = false;
        stored[heading.id] = prefix + number
        levels.forEach(function(level_comp, j) {
            if (reached){
                counters[level_comp] = 0
            };
            if (level==level_comp){
                reached = true;
            }
        });
    });
}

function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}


function number_captions(){
    var captions = document.querySelectorAll("caption");
    var kinds = ["table", "figure"]
    var counters = {"table": 0, "figure": 0}
    captions.forEach(function(caption, i) {
        kinds.forEach(function(kind, j) {
            if (caption.classList.contains(kind)){
                counters[kind] += 1
                ref_counter = capitalizeFirstLetter(kind) + " " + counters[kind];
                caption.textContent = ref_counter + ": " + caption.textContent
                stored[caption.id] = ref_counter
            }
        });
    });
    var refs = document.querySelectorAll("a.crossref");
    refs.forEach(function(ref, i) {
        ref.textContent = stored[ref.name]
    })
}