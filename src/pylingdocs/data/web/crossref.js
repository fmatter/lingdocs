// returns strings like 3. or 4.3.2
function get_number_label(counters, level) {
    output = []
    for (var i = 2; i <= level; i++) {
        output.push(counters["h"+i])
    }
    return output.join(".")
}

//used for storing both section labels and float counters
var stored = {}


function number_sections(start=0){
    var toc = document.getElementById("toc") // get the table of contents
    var counters = {}; // initialize counters for every heading level except h1 (below)
    var levels = ["h2", "h3", "h4", "h5", "h6"];
    levels.forEach(function(x, i) {
        counters[x] = 0
    })
    counters["h2"] = start

    // there is only supposed to be one h1; get a potential chapter number and format it
    var h1 = document.querySelectorAll("h1");
    if (h1.length == 0){
        prefix = ""
    } else {
        h1 = h1[0]
        if (h1.hasAttribute("number")) {
            prefix = h1.getAttribute("number") + "."
        } else {
            prefix = ""
        }
        h1.textContent = prefix+" " + h1.textContent
    }

    // iterate all headings
    var headings = document.querySelectorAll("h2, h3, h4, h5, h6");
    headings.forEach(function(heading, i) {
        var level = heading.tagName.toLowerCase();
        counters[level] += 1
        number = get_number_label(counters, level.charAt(level.length - 1)) // the formatted X.Y.Z counter
        if (!heading.textContent.startsWith(prefix + number)){
            heading.textContent = prefix + number + ". " + heading.textContent    
        }
        

        if (toc) {
            toclink = document.createElement('a') // insert links into the TOC
            toclink.textContent = '\xa0\xa0'.repeat(level.charAt(level.length - 1)-2)+heading.textContent
            toclink.href = "#"+heading.id
            tocdiv = document.createElement('div')
            tocdiv.appendChild(toclink);
            toc.appendChild(tocdiv);
        }

        stored[heading.id] = prefix + number // for crossref resolution

        // reset the smaller counters
        reached = false;
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
    var captions = document.querySelectorAll("caption"); // get all captions
    var kinds = ["table", "figure"] // only these two types for now
    var counters = {"table": 0, "figure": 0}
    captions.forEach(function(caption, i) {
        kinds.forEach(function(kind, j) {
            if (caption.classList.contains(kind)){
                counters[kind] += 1
                ref_counter = capitalizeFirstLetter(kind) + " " + counters[kind];
                if (!caption.textContent.startsWith(ref_counter + ": ")){
                    caption.textContent = ref_counter + ": " + caption.textContent
                }
                stored[caption.id] = ref_counter // store the value for resolve_crossrefs below
            }
        });
    });
}

// iterate all a.crossref and insert the calculated values; for floats and sections
function resolve_crossrefs(){
    var refs = document.querySelectorAll("a.crossref");
    refs.forEach(function(ref, i) {
        ref.textContent = stored[ref.name]
        if (ref.hasAttribute("end")) { // for ranges
            end = ref.getAttribute("end")
            ref.textContent += "-" + stored[end]
        }
    })
}