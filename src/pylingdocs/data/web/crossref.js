// returns strings like 3. or 4.3.2
function getNumberLabel(counters, level) {
    output = []
    for (var i = 2; i <= level; i++) {
        output.push(counters["h"+i])
    }
    return output.join(".")
}

//used for storing both section labels and float counters
if (typeof refLabels === 'undefined') {
    var refLabels = {}
}

//for labels that are on another page
if (typeof refLocations === 'undefined') {
    var refLocations = {}
}

function numberSections(start=0){
    var toc = document.getElementById("nav-items") // get the div holding our eventual table of contents
    // initialize counters for every heading level except h1 (below)
    var counters = {};
    var levels = ["h2", "h3", "h4", "h5", "h6"];
    levels.forEach(function(x, i) {
        counters[x] = 0
    })
    counters["h2"] = start

    // there is only supposed to be one h1
    // in our case, this is potentially a chapter number
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

    // iterate all sections
    // var headings = document.querySelectorAll("h2, h3, h4, h5, h6");
    var sections = document.querySelectorAll("section");
    // store what level the last node was so we can build a hierarchical TOC
    var lastNodes = {}
    sections.forEach(function(section, i) {
        var heading = section.querySelectorAll("h2, h3, h4, h5, h6")[0];
        var level = heading.tagName.toLowerCase();
        var levelInt = parseInt(level.charAt(level.length - 1))
        counters[level] += 1
        number = getNumberLabel(counters, level.charAt(level.length - 1)) // the formatted X.Y.Z counter
        if (!heading.textContent.startsWith(prefix + number)){
            heading.textContent = prefix + number + ". " + heading.textContent    
        }
        if (toc) {
            tocLink = document.createElement('a')
            tocLink.textContent = heading.textContent //'\xa0\xa0'.repeat(level.charAt(level.length - 1)-2)+
            tocLink.href = "#"+section.id
            subItems = document.createElement("ol")
            subItems.setAttribute('class', 'subitems');
            tocEntry = document.createElement("li")
            tocEntry.id = "nav-"+section.id
            tocEntry.appendChild(tocLink)
            tocEntry.appendChild(subItems)
            if (levelInt-1 in lastNodes){
                lastNodes[levelInt-1].appendChild(tocEntry)             
            } else {
                toc.appendChild(tocEntry)             
            }
            lastNodes[levelInt] = subItems
        }
        // reset the counters smaller than the current level
        reached = false;
        levels.forEach(function(lvl_i, j) {
            if (reached){
                counters[lvl_i] = 0
            };
            if (level==lvl_i){
                reached = true;
            }
        });
        refLabels[section.id] = prefix + number // for crossref resolution
    });


    // headings.forEach(function(heading, i) {
    //     var level = heading.tagName.toLowerCase();
    //     var levelInt = parseInt(level.charAt(level.length - 1))
    //     counters[level] += 1
    //     number = getNumberLabel(counters, level.charAt(level.length - 1)) // the formatted X.Y.Z counter
    //     if (!heading.textContent.startsWith(prefix + number)){
    //         heading.textContent = prefix + number + ". " + heading.textContent    
    //     }
    //     // if there is a toc div, populate it
    //     if (toc) {
    //         tocLink = document.createElement('a')
    //         tocLink.textContent = heading.textContent //'\xa0\xa0'.repeat(level.charAt(level.length - 1)-2)+
    //         tocLink.href = "#"+heading.id
    //         subItems = document.createElement("ol")
    //         subItems.setAttribute('class', 'subitems');
    //         tocEntry = document.createElement("li")
    //         tocEntry.id = "nav-"+heading.id
    //         tocEntry.appendChild(tocLink)
    //         tocEntry.appendChild(subItems)
    //         if (levelInt-1 in lastNodes){
    //             lastNodes[levelInt-1].appendChild(tocEntry)             
    //         } else {
    //             toc.appendChild(tocEntry)             
    //         }
    //         lastNodes[levelInt] = subItems
      // <li><a href="#introduction">Introduction</a></li>

            // tocDiv = document.createElement('div')
            // tocDiv.classList = ["toc-div"]
            // tocDiv.id = "toc-"+heading.id
            // levelInt = level.charAt(level.length - 1)
            // if (levelInt > 2){
            //     tocDiv.style.display = "none"
            // }
            // lastNodes[levelInt] = tocDiv

            // // arrows for expanding and collapsing TOC entries
            // arrow = document.createElement('div')
            // arrow.style.display = "inline-block"
            // arrow.textContent = "🞂"
            // arrow.onclick = function() {
            //     let sec = document.getElementById("toc-"+heading.id);
            //     kids = sec.getElementsByClassName('toc-div')
            //     for (const [pos, kid] of Object.entries(kids)) {
            //         if (kid.style.display === "none") {
            //             kid.style.display = "block";
            //             this.textContent = "🞃"
            //         } else {
            //             kid.style.display = "none";
            //             this.textContent = "🞂"
            //         }
            //     };
            // };

            // // compile entry and add it to appropriate div in TOC tree
            // tocDiv.appendChild(arrow)
            // tocDiv.appendChild(tocLink);

            // if (levelInt-1 in lastNodes){
            //     lastNodes[levelInt-1].appendChild(tocDiv);
            // } else {
            //     toc.appendChild(";)");                
            // }
        // }


        // refLabels[heading.id] = prefix + number // for crossref resolution

        // // reset the counters smaller than the current level
        // reached = false;
        // levels.forEach(function(lvl_i, j) {
        //     if (reached){
        //         counters[lvl_i] = 0
        //     };
        //     if (level==lvl_i){
        //         reached = true;
        //     }
        // });
    // });
    // TOC entries without subentries don't need a (visible) toggle arrow
    for (const [pos, tocDiv] of Object.entries(document.getElementsByClassName("toc-div"))) {
        kids = tocDiv.getElementsByClassName('toc-div')
        if (kids.length == 0){
            tocDiv.children[0].textContent = "\xa0\xa0"
        }
    }

}


function numberSectionsOld(start=0){
    var toc = document.getElementById("toc") // get the div holding our eventual table of contents
    // initialize counters for every heading level except h1 (below)
    var counters = {};
    var levels = ["h2", "h3", "h4", "h5", "h6"];
    levels.forEach(function(x, i) {
        counters[x] = 0
    })
    counters["h2"] = start

    // there is only supposed to be one h1
    // in our case, this is potentially a chapter number
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
    // store what level the last node was so we can build a hierarchical TOC
    var lastNodes = {}
    headings.forEach(function(heading, i) {
        var level = heading.tagName.toLowerCase();
        counters[level] += 1
        number = getNumberLabel(counters, level.charAt(level.length - 1)) // the formatted X.Y.Z counter
        if (!heading.textContent.startsWith(prefix + number)){
            heading.textContent = prefix + number + ". " + heading.textContent    
        }
        // if there is a toc div, populate it
        if (toc) {
            tocLink = document.createElement('a')
            tocLink.textContent = '\xa0\xa0'.repeat(level.charAt(level.length - 1)-2)+heading.textContent
            tocLink.href = "#"+heading.id
            tocDiv = document.createElement('div')
            tocDiv.classList = ["toc-div"]
            tocDiv.id = "toc-"+heading.id
            levelInt = level.charAt(level.length - 1)
            if (levelInt > 2){
                tocDiv.style.display = "none"
            }
            lastNodes[levelInt] = tocDiv

            // arrows for expanding and collapsing TOC entries
            arrow = document.createElement('div')
            arrow.style.display = "inline-block"
            arrow.textContent = "🞂"
            arrow.onclick = function() {
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

            // compile entry and add it to appropriate div in TOC tree
            tocDiv.appendChild(arrow)
            tocDiv.appendChild(tocLink);

            if (levelInt-1 in lastNodes){
                lastNodes[levelInt-1].appendChild(tocDiv);
            } else {
                toc.appendChild(tocDiv);                
            }
        }


        refLabels[heading.id] = prefix + number // for crossref resolution

        // reset the counters smaller than the current level
        reached = false;
        levels.forEach(function(lvl_i, j) {
            if (reached){
                counters[lvl_i] = 0
            };
            if (level==lvl_i){
                reached = true;
            }
        });
    });
    // TOC entries without subentries don't need a (visible) toggle arrow
    for (const [pos, tocDiv] of Object.entries(document.getElementsByClassName("toc-div"))) {
        kids = tocDiv.getElementsByClassName('toc-div')
        if (kids.length == 0){
            tocDiv.children[0].textContent = "\xa0\xa0"
        }
    }
}

function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}



function numberCaptions(){
    var captions = document.querySelectorAll("caption"); // get all captions
    var figcaptions = document.querySelectorAll("figcaption"); // get all captions
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
                refLabels[caption.id] = ref_counter // store the value for resolveCrossrefs below
            }
        });
    });
    figcaptions.forEach(function(caption, i) {
        counters["figure"] += 1
        ref_counter = capitalizeFirstLetter("figure") + " " + counters["figure"];
        if (!caption.textContent.startsWith(ref_counter + ": ")){
            caption.textContent = ref_counter + ": " + caption.textContent
        }
        refLabels[caption.id] = ref_counter // store the value for resolveCrossrefs below
    })
}

// iterate all a.crossref and insert the calculated values; for floats and sections
function resolveCrossrefs(){
    var refs = document.querySelectorAll("a.crossref");
    refs.forEach(function(ref, i) {
        ref.textContent = refLabels[ref.name]
        console.log(ref.name)
        console.log(refLabels[ref.name])

        if (ref.name in refLocations){
            ref.href = "/"+refLocations[ref.name] + "#" + ref.href.split("#").pop()
        }
        if (ref.hasAttribute("end")) { // for ranges
            end = ref.getAttribute("end")
            ref.textContent += "-" + refLabels[end]
        }
    })
}