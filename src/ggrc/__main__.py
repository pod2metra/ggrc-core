# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Main ggrc entry point."""
import time
from logging import getLogger
from ggrc.app import app
from ggrc import INIT_TIME
HOST = app.config.get("HOST") or "0.0.0.0"
PORT = app.config.get("PORT") or 8080

getLogger("ggrc.performance").info("GGRC started in %.2fs (%.2fs CPU)",
                                   time.time() - INIT_TIME[0],
                                   time.clock() - INIT_TIME[1])
# from werkzeug.contrib.profiler import ProfilerMiddleware
# app.config['PROFILE'] = True
# app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[60])
app.run(host=HOST, port=PORT)
