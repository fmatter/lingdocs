
async function render() {
    console.log("Rendering")
    if (this.input != this.contents[this.current]) {
        this.modified[this.current] = true
        this.contents[this.current] = this.input
    }
    this.text = ""
    var inputString = ""
    if (this.previewMode == "all"){
        inputString = Object.values(this.contents).join("\n\n")
    } else {
        inputString = this.input
    }
    const options = {
        method: "POST",
        body: JSON.stringify({"input": inputString}),
        headers: {'Content-Type': 'application/json'}
    }
    fetch("http://localhost:5000/render", options).then((response) => {
        let dataPromise = response.text();
        dataPromise.then((data) => {
            this.text = data;
            this.$nextTick(() => {
                style()
            });
        })
    });
}

function mounted() {
    console.log("Mounted")
    for (const key of Object.keys(this.contents)) {
        this.modified[key] = false
    }
}


var initial_data = {
    "input": "placeholder",
    'text': "",
    "previewMode": "file",
    "autoPreview": true,
    "modified": {}
}


function style() {
    console.log("Styling")
    number_examples();
    number_sections()
    number_captions()
    resolve_crossrefs()
}

function load_part(part){
    this.input = this.contents[part]
    this.current = part
    if (this.previewMode == "file") {
        this.render()
    }
}


function handleAutoPreview(x){
}


function saveFile(){
    console.log(this.current)
        const options = {
        method: "POST",
        body: JSON.stringify({"text": this.contents[this.current]}),
        headers: {'Content-Type': 'application/json'}
    }
    fetch("http://localhost:5000/write/" + this.current, options);
}


function updateContent(){
    if (this.autoPreview === true){
        console.log("Rendering")
        // this.render.bind(this)
        this.render()
    } else {
        console.log("Not rendering")
        console.log(self.autoPreview)
    }
}

var methods = {
    'render': render,
    "load_part": load_part,
    "handleAutoPreview": handleAutoPreview,
    "updateContent": updateContent,
    "saveFile": saveFile
}

fetch("http://localhost:5000/getparts", {headers: {'Content-Type': 'application/json'}}).then((response) => {
    let dataPromise = response.json();
    dataPromise.then((contents) => {
        console.log(Object.keys(contents))
        initial_data["contents"] = contents
        const { ref, createApp } = Vue
        var vueApp = Vue.createApp({
            data() {return initial_data},
            methods: methods,
            mounted:mounted
        });
        vueApp.use(naive);
        vueApp.mount('#app');
    })
})


// function renderIcon (icon) {
//   return () =>Vue.h(NIcon, null, { default: () =>Vue.h(icon) })
// }

