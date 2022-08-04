//shared/global variables
export const store = Pinia.defineStore('store', {
    state: () => ({"current": "", "originalContents": {}, "previewMode": "file", "text": "", "modified": {}, "contents": {}, "autoPreview": true})
})

var initial_data = {
    "parts": [],
    "drawer": true,
    "contentView": "both",
    "contentViewItems": ["both", "editor", "viewer"],
    "editor": true,
    "viewer": true,
    "renderConfig": {
        // Mermaid config
        mermaid: {
          theme: "dark"
        }
      },
}


async function render() {
    console.log("Rendering")
    if (this.originalContents[this.current] != this.contents[this.current]) {
        this.modified[this.current] = true
    } else {
        this.modified[this.current] = false
    }
    var inputString = ""
    if (this.previewMode == "all"){
        inputString = Object.values(this.contents).join("\n\n")
    } else {
        inputString = this.contents[this.current]
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
                style(3)
            });
        })
    });
}

async function mounted() {
    console.log("Mounting")
    fetch("http://localhost:5000/getfiles", {headers: {'Content-Type': 'application/json'}}).then((response) => {
        let dataPromise = response.json();
        dataPromise.then((files) => {
            this.parts = files
            var init = false
            for (const part of files) {
                this.modified[part["id"]] = false
                fetch("http://localhost:5000/getpart/"+part["id"], {headers: {'Content-Type': 'application/json'}}).then((response) => {
                    let dataPromise = response.json();
                    dataPromise.then((content) => {
                       this.originalContents[part["id"]] = content
                       console.log(part["id"])
                       this.contents[part["id"]] = content
                       if (!init){
                        this.current = part["id"]
                        init=true
                        this.render()
                       }
                    })
                })
            }
        })
    })
    console.log("Mounted")
}

function insertEntity() {
    console.log("TBD")
}

function style(start=0) {
    console.log("Styling")
    number_examples();
    number_sections(start)
    number_captions()
    resolve_crossrefs()
}

function loadPart(part){
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
        this.render()
    } else {
        console.log("Not rendering")
        console.log(this.autoPreview)
    }
}

var methods = {
    'render': render,
    "loadPart": loadPart,
    "handleAutoPreview": handleAutoPreview,
    "updateContent": updateContent,
    "saveFile": saveFile,
    "entity": insertEntity
}


Vue.component('my-markdown-editor', {
    data() {
        return {
            "custom":{
                'entity': {
                    cmd: 'entity',
                    ico: "mdi mdi-database-arrow-down-outline",
                    title: 'Insert entity'
                }
            },
        }
    },
    computed: {...Pinia.mapWritableState(store, ["current", "contents", "autoPreview", "previewMode", "originalContents", "text", "modified"])},
    methods: methods,
    template: `<markdown-editor
                                height="83vh"
                                v-model:value="contents[current]"
                                v-on:input="updateContent"
                                id="textinput"
                                toolbar="bold italic heading numlist bullist entity"
                                @command:entity="entity"
                                :extend="custom"
                                >
                            </markdown-editor>`
});



Vue.use(Pinia.PiniaVuePlugin)
const { ref, createApp } = Vue
var vueApp = new Vue({
    el: "#app",
    data() {return initial_data},
    computed: {...Pinia.mapWritableState(store, ["current", "contents", "autoPreview", "previewMode", "originalContents", "text", "modified"])},
    methods: methods,
    mounted: mounted,
    vuetify: new Vuetify(),
    pinia: Pinia.createPinia(),
    // components: {"my-markdown-editor":}
});
