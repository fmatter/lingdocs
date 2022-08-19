import logging
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask import send_file
from flask_cors import CORS
from pycldf import Dataset
from pylingdocs.config import CONTENT_FOLDER
from pylingdocs.config import DATA_DIR
from pylingdocs.config import FIGURE_DIR
from pylingdocs.config import STRUCTURE_FILE
from pylingdocs.helpers import _get_relative_file
from pylingdocs.helpers import _load_cldf_dataset
from pylingdocs.helpers import load_content
from pylingdocs.helpers import write_file as write
from pylingdocs.output import HTML
from pylingdocs.preprocessing import postprocess
from pylingdocs.preprocessing import preprocess
from pylingdocs.preprocessing import render_markdown


log = logging.getLogger(__name__)


class Editor:
    def __init__(self, cldf, source, output_dir):
        self.cldf = cldf
        self.source = source
        self.output_dir = output_dir
        self.builder = HTML

    def build(self, content):
        preprocessed = preprocess(content)
        preprocessed = self.builder.preprocess_commands(preprocessed)
        preprocessed += "\n\n" + self.builder.reference_list()
        try:
            preprocessed = render_markdown(
                preprocessed, self.ds, output_format=self.builder.name
            )
        except KeyError as e:
            return f"Key not found: {e.args[0]}"
        preprocessed = postprocess(preprocessed, self.builder)
        return self.builder.preprocess(preprocessed)

    def load(self):
        self.ds = _load_cldf_dataset(self.cldf)
        self.structure_file = _get_relative_file(
            folder=self.source / CONTENT_FOLDER, file=STRUCTURE_FILE
        )
        self.contents = load_content(
            structure_file=self.structure_file, source_dir=self.source / CONTENT_FOLDER
        )

    def run(self):

        # initialize data
        self.load()

        # all js and css files live in the static folder
        app = Flask(__name__, template_folder=DATA_DIR, static_folder=DATA_DIR / "web")

        # needed because of vue
        CORS(app)

        # the main editor GUI
        @app.route("/")
        def editor():
            return render_template("editor.html")


        # compile markdown
        @app.post("/render")
        def render():
            return self.build(request.json["input"])

        # save changes
        @app.post("/write/<file_id>")
        def write_file(file_id):
            write(file_id, request.json["text"], structure_file=self.structure_file)
            self.load()
            return "Good"

        # serve images directly from the input folder
        @app.route("/<path:filename>")
        def download_file(filename):
            return send_file(FIGURE_DIR.resolve() / filename)



        @app.route("/getpart/<part_id>")
        def getpart(part_id):
            return jsonify(self.contents[part_id]["content"])

        @app.route("/getparts")
        def getparts():
            return jsonify(self.contents)

        @app.route("/getfiles")
        def getfiles():
            return jsonify(
                [{"id": x, "name": y["filename"]} for x, y in self.contents.items()]
            )


        app.run(debug=True, port=5000)
