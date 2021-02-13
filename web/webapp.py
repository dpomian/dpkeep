import sys
sys.path.append('..')

import os
import flask
import clipboard
from flask import request, jsonify
from flask import render_template
from engine import crypto as cry
from engine import storage as st
from mykeep import _get_decrypted_dict
from engine import utils
from engine import pwd_utils

#app = flask.Flask(__name__, template_folder='web/templates')
app = flask.Flask(__name__)
app.config["DEBUG"] = True

netrcfile = os.path.join(os.path.dirname(__file__),'../res/prd/.netrc')
storagefile = os.path.join(os.path.dirname(__file__),'../res/prd/.mykeep_storage')

@app.route('/keep/', methods=['GET'])
def home():
    global netrcfile, storagefile
    crypto = cry.Crypto(utils.get_password(netrcfile))
    storage = st.Storage(storagefile)
    data_dict = _get_decrypted_dict(crypto, storage)

    return render_template('index2.html', data=data_dict)

@app.route('/keep/api/v1/cp/', methods=['GET'])
def copy():
    name = request.args['name'] if 'name' in request.args else None

    global netrcfile, storagefile
    crypto = cry.Crypto(utils.get_password(netrcfile))
    storage = st.Storage(storagefile)
    data_dict = _get_decrypted_dict(crypto, storage)
    clipboard.copy(data_dict[name]['pwd']) if name in data_dict else clipboard.copy('')
    return jsonify({'data':'copied'})

@app.route('/keep/passgen/', methods=['GET'])
def pass_gen():
    return render_template('passgen.html')


@app.route('/keep/api/v1/passgen/', methods=['GET'])
def pass_gen_api():
    pwd = pwd_utils.generate_pwd()
    clipboard.copy(pwd)
    return jsonify({'data':{'pwd':pwd}})

app.run()
