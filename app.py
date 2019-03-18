import logging, sys
from blueprints import app, manager
from logging.handlers import RotatingFileHandler

if __name__ == '__main__':
    # define log format and create a rotating log with max size of 10 Mb and max backup to 10 files
    formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    log_handler = RotatingFileHandler("%s/%s" % (app.root_path, 'storage/log/app.log'), maxBytes=10000000, backupCount=10)
    log_handler.setLevel(logging.INFO)
    log_handler.setFormatter(formatter)
    app.logger.addHandler(log_handler)
    
    try:
        if sys.argv[1] == 'db':
            manager.run()
        else:
            app.run(debug=False, host='0.0.0.0', port=5001)
    except IndexError as e:
        app.run(debug=True, host='0.0.0.0', port=5001)

