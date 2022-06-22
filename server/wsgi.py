from os import getenv  #, chdir
# chdir('../')

import core
application = core.app

if __name__ == '__main__':
    # application.run('0.0.0.0', port=os.getenv('PORT', 5000))
    core.socket.run(application, host='0.0.0.0', port=getenv('PORT', 5000))
