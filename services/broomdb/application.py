#!/usr/bin/env python
#
# BroomDB RESTful API HTTP service. 
#
# Provides a web-based API for querying Broom database
# objects by ID or by using a simple filter.
#
# The interface is as follows:
#
# /object_type           - Return a list of all objects of the type.    
# /object_type/?query    - Return a list of all objects matching query.
# /object_type/object_id - Return data for a particular object.

import broom
import flask
import json
import traceback

application = app = flask.Flask('broomdb')

def error_response(exception, status_code):
    return json.dumps({'error': exception.message}), status_code, None

@app.route('/<object_type>/<int:object_id>', methods=["GET"])
def read(object_type, object_id):
    args = dict(flask.request.args)
    callback = args.pop('broom:callback', None)
    for k in list(args):
        if k.startswith('broom:'):
            args.pop(k)
    try:
        # TODO: This is a workaround until true sessions are 
        #       implemented; for now we force expire.
        broom.db._session.expire_all()
        obj = broom.db.read(object_type, object_id)
    except broom.BroomDBObjectNotFoundError, e:
        return error_response(e, 404)
    except Exception, e:
        return error_response(e, 500)
    data = obj.toDict(meta=True, expand=True, extra=True)
    ret = json.dumps(data)
    if callback:
        ret = '%s(%s)' % (callback[0], ret)
    return ret

@app.route('/<object_type>/', methods=["GET"])
def find_by(object_type):
    args = dict(flask.request.args)
    callback = args.pop('broom:callback', None)
    for k in list(args):
        if k.startswith('broom:'):
            args.pop(k)
    object_filter = dict(args)
    try:
        broom.db._session.expire_all()
        objs = broom.db.find_by(object_type, **object_filter)
    except Exception, e:
        return error_response(e, 500)
    data = [obj.toDict(data=True) for obj in objs]
    ret = json.dumps(data)
    if callback:
        ret = '%s(%s)' % (callback[0], ret)
    return ret

@app.route('/', methods=["POST"])
def write():
    try:
        broom.db._session.expire_all()
        obj = broom.BroomObject.from_json(flask.request.data)
        broom.db.write()
    except Exception, e:
        broom.db.rollback()
        return error_response(e, 500)
    return json.dumps(obj.toDict(meta=True, data=False))

# TODO: Support multi-column primary keys.
@app.route('/<object_type>/<int:object_id>', methods=["DELETE"])
def delete(object_type, object_id):
    try:
        broom.db._session.expire_all()
        broom.db.delete_by_id(object_type, object_id)
        broom.db.commit()
    except Exception, e:
        broom.db.rollback()
        return error_response(e, 500)
    return ''

def main():
    import socket
    app.run(port=5000, debug=True)

if __name__ == '__main__':
    main()
