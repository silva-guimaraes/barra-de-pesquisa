import os
import flask

app = flask.Flask(__name__, template_folder='pages')


@app.route('/')
def hello():
    search = flask.request.args.get('search')
    print(search)

    if search is None:
        return flask.send_file('pages/index.html')

    files = os.listdir('pages')
    try:
        result = files.index(search)
    except ValueError:
        return 'no results were found.'

    return flask.render_template('search.html', files=[files[result]])


@app.route('/<path:path>')
def serve_file(path):
    return flask.send_from_directory('pages', path)
