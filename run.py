from gunicorn.app.base import BaseApplication
from config.wsgi import application


class GunicornApp(BaseApplication):
    def __init__(self, application, options=None):
        self.application = application
        self.options = options or {}
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def main():
    gunicorn_options = {"bind": "127.0.0.1:8000", "env": "DJANGO_SETTINGS_MODULE=mo.config.settings"}

    gunicorn_app = GunicornApp(application, gunicorn_options)
    gunicorn_app.run()


if __name__ == "__main__":
    main()
