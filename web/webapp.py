import sys
sys.path.append('..')

import os
import io
import flask
import clipboard
from flask import request, jsonify
from flask import render_template
from flask import make_response
from flask import send_file
from engine import crypto as cry
from engine import storage as st
from mykeep import _get_decrypted_dict
import mykeep
from engine import utils
from engine import pwd_utils
import qrcode
import random
import base64

#app = flask.Flask(__name__, template_folder='web/templates')
app = flask.Flask(__name__)
app.config["DEBUG"] = True

def _set_environ():
    os.environ['DPKEEP_NETRC'] = os.path.join(os.path.dirname(__file__),'../res/prd/.netrc')
    os.environ['DPKEEP_STORAGE'] = os.path.join(os.path.dirname(__file__),'../res/prd/.mykeep_storage')


@app.route('/keep/', methods=['GET'])
def home():
    netrcfile = os.path.join(os.path.dirname(__file__),'../res/prd/.netrc')
    storagefile = os.path.join(os.path.dirname(__file__),'../res/prd/.mykeep_storage')
    crypto = cry.Crypto(utils.get_password(netrcfile))
    storage = st.Storage(storagefile)
    data_dict = _get_decrypted_dict(crypto, storage)

    return render_template('index.html', data=data_dict)


@app.route('/keep/api/v1/cp/', methods=['GET'])
def copy():
    name = request.args['name'] if 'name' in request.args else None

    _set_environ()
    mykeep.parse_args(['cp', name])

    return jsonify({'data':'copied'})


@app.route('/keep/api/v1/rm', methods=['DELETE'])
def rm():
    name = request.args['name'] if 'name' in request.args else None
    
    if name:
        _set_environ()
        mykeep.parse_args(['rm',name])
        return jsonify({'data':'deleted'})
    return jsonify({'data':'not found'})


@app.route('/keep/api/v1/new_entry', methods=['POST'])
def add_new():
    data = request.json
    _set_environ()

    if 'name' in data and 'link' in data and 'pwd' in data:
        tags = data['tags'] if 'tags' in data else ''
        tags = ','.join(x.strip() for x in tags.split(',') if x.strip().isalnum())
        mykeep.parse_args(['add','-name',data['name'],'-link',data['link'],'-pwd',data['pwd'],'-tags',tags])
        return jsonify({'data':'created'})

    return jsonify({'data':'data is not good'})


@app.route('/keep/api/v1/update_entry', methods=['PUT'])
def update_entry():
    data = request.json
    print('update data: {}'.format(data))
    
    _set_environ()
    mykeep.parse_args(['up', '-link', data['link'], '-pwd', data['pwd'], '-tags', data['tags'], data['name']])

    return jsonify({'data':'updated'})


@app.route('/keep/api/v1/ll', methods=['GET'])
def ll():
    netrcfile = os.path.join(os.path.dirname(__file__),'../res/prd/.netrc')
    storagefile = os.path.join(os.path.dirname(__file__),'../res/prd/.mykeep_storage')
    crypto = cry.Crypto(utils.get_password(netrcfile))
    storage = st.Storage(storagefile)
    data_dict = _get_decrypted_dict(crypto, storage)

    result = [] 
    for key in sorted(data_dict.keys()):
        result.append({'name': key, 'link': data_dict[key]['link'], 'tags':data_dict[key]['tags'] if 'tags' in data_dict[key] else ''})

    return jsonify({'data':result})


@app.route('/keep/passgen/', methods=['GET'])
def pass_gen():
    return render_template('passgen.html')


@app.route('/keep/addnew/', methods=['GET'])
def addnew():
    return render_template('addnew.html')


@app.route('/keep/api/v1/passgen/', methods=['GET'])
def pass_gen_api():
    pwd = pwd_utils.generate_pwd()
    clipboard.copy(pwd)
    return jsonify({'data':{'pwd':pwd, 'result':'success'}})


@app.route('/keep/api/v1/genqr/', methods=['GET'])
def generate_qr_img():
    name = request.args['name'] if 'name' in request.args else None

    netrcfile = os.path.join(os.path.dirname(__file__),'../res/prd/.netrc')
    storagefile = os.path.join(os.path.dirname(__file__),'../res/prd/.mykeep_storage')
    crypto = cry.Crypto(utils.get_password(netrcfile))
    storage = st.Storage(storagefile)
    data_dict = _get_decrypted_dict(crypto, storage)

    if name in data_dict:
        img = qrcode.make(data_dict[name]['pwd'])
        tmp_qr = 'static/styles/tempqr.png'
        img.save(tmp_qr)
        with open(tmp_qr, 'rb') as ifile:
            data = ifile.read()
        os.remove(tmp_qr)

        if len(data):
            image_binary = data
            encoded = base64.b64encode(image_binary)
            return jsonify({'data':{'result':'success', 'bin': io.BytesIO(encoded).getvalue().decode()}})

    return jsonify({'data':{'result':'fail'}})


@app.route('/keep/area51/popup', methods=['GET'])
def area51_popup():
    # return render_template('area51popup.html')
    return render_template('area51qrpopup.html')


app.run()
