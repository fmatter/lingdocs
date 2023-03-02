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

function numberSections(start=0){
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
    var lastNodes = {}
    headings.forEach(function(heading, i) {
        var level = heading.tagName.toLowerCase();
        counters[level] += 1
        number = get_number_label(counters, level.charAt(level.length - 1)) // the formatted X.Y.Z counter
        if (!heading.textContent.startsWith(prefix + number)){
            heading.textContent = prefix + number + ". " + heading.textContent    
        }
        

        if (toc) {
            tocLink = document.createElement('a')
            tocLink.textContent = '\xa0\xa0'.repeat(level.charAt(level.length - 1)-2)+heading.textContent
            levelInt = level.charAt(level.length - 1)
            tocLink.href = "#"+heading.id
            tocDiv = document.createElement('div')
            tocDiv.classList = ["toc-div"]
            tocDiv.id = "toc-"+heading.id
            if (levelInt > 2){
                tocDiv.style.display = "none"
            }
            lastNodes[levelInt] = tocDiv
            btn = document.createElement('div')
            btn.style.display = "inline-block"
            btn.textContent = "🞂"
            btn.onclick = function() {
                let sec = document.getElementById("toc-"+heading.id);
                kids = sec.getElementsByClassName('toc-div')
                for (const [pos, kid] of Object.entries(kids)) {
                    if (kid.style.display === "none") {
                        kid.style.display = "block";
                        this.textContent = "🞃"
                    } else {
                        kid.style.display = "none";
                        this.textContent = "🞂"
                    }
                };
            };
            tocDiv.appendChild(btn)
            tocDiv.appendChild(tocLink);
            if (levelInt-1 in lastNodes){
                lastNodes[levelInt-1].appendChild(tocDiv);
            } else {
                toc.appendChild(tocDiv);                
            }
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
    var tocDivs = document.getElementsByClassName("toc-div");
    for (const [pos, tocDiv] of Object.entries(tocDivs)) {
        kids = tocDiv.getElementsByClassName('toc-div')
        if (kids.length == 0){
            tocDiv.children[0].textContent = "\xa0\xa0"
            // tocDiv.children[0].remove()
        }
    }

}

function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}



function number_captions(){
    var captions = document.querySelectorAll("caption"); // get all captions
    var figcaptions = document.querySelectorAll("figcaption"); // get all captions
    console.log(figcaptions)
    var kinds = ["table"] // might need "maps" or "plots" or sth. at some point
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
    figcaptions.forEach(function(caption, i) {
        counters["figure"] += 1
        ref_counter = capitalizeFirstLetter("figure") + " " + counters["figure"];
        if (!caption.textContent.startsWith(ref_counter + ": ")){
            caption.textContent = ref_counter + ": " + caption.textContent
        }
        stored[caption.id] = ref_counter // store the value for resolve_crossrefs below
    })
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