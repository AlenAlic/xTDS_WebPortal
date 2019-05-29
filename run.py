from ntds_webportal import create_app
from instance.populate import create_teams


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'create_teams': create_teams_old}


def create_teams_old():
    with app.app_context():
        create_teams()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
