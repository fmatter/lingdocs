var dl = document.getElementById("glossing_abbrevs")
var keys = Object.keys(abbrev_dict).sort()
console.log("Gathering glossing abbreviations")
for (var key in keys){{
    console.log(key)
    const dd = document.createElement('dd');
    const dt = document.createElement('dt');
    const text = document.createTextNode(abbrev_dict[keys[key]]);
    const abbr = document.createTextNode(keys[key]);
    dt.classList.add('smallcaps');
    dd.appendChild(text);
    dt.appendChild(abbr);
    dl.append(dt)
    dl.append(dd)
}};