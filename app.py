import os
from open_container import app

app.config.from_pyfile(os.path.join(os.getcwd(), "config.py"))


if __name__ == "__main__":
    app.run(host=app.config['IP'], port=app.config['PORT'])
