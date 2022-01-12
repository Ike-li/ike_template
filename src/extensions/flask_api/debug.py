"""Flask Extensions
"""
import flask
import flask_debugtoolbar


class DevToolbar:  # pragma: no cover
    """Add debug toolbars with json to html

    Note you must pass `_debug` param to convert the json response
    """

    def __init__(self, app):
        wrap_json = """
        <html>
            <head>
                <title>Debugging JSON Response</title>
            </head>

            <body>
                <h1>Wrapped JSON Response</h1>

                <h2>HTTP Code</h2>
                <pre>{{ http_code }}</pre>

                <h2>JSON Response</h2>
                <pre>{{ response }}</pre>
            </body>
        </html>
        """

        @app.after_request
        def after_request(response):
            is_json = response.mimetype == "application/json"
            if is_json and "_debug" in flask.request.args:
                html_wrapped_response = flask.make_response(
                    flask.render_template_string(
                        wrap_json,
                        response=response.data.decode("utf-8"),
                        http_code=response.status,
                    ),
                    response.status_code,
                )
                return app.process_response(html_wrapped_response)

            return response

        flask_debugtoolbar.DebugToolbarExtension(app)
