import flask
import dotenv
import boto3
import os
import json
import uuid
def r2_key(fid):
    return f"freezer {fid}"

def r2_exists(key):
    try:
        s3.head_object(Bucket=BUCKET, Key=key)
        return True
    except:
        return False

def update_s3(data, fid):
    s3.put_object(Bucket=BUCKET,
                  Key=r2_key(fid),
                  Body=json.dumps(data),)

def get_s3(fid):
    return json.loads(s3.get_object(Bucket=BUCKET,
                             Key=r2_key(fid))["Body"].read())

dotenv.load_dotenv(".env")
s3 = boto3.client(
    "s3",
    endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
    aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    region_name="auto",
)

BUCKET = os.environ["R2_BUCKET"]
app = flask.Flask(__name__)

@app.route("/addfreezer", methods=["POST"])
def addfreezer():
    try:
        freezer_request = flask.request.get_json()
        if freezer_request["secret"] == os.environ["SECRET_PASS"]:
            fid = uuid.uuid4().hex[:6]
            name = freezer_request["name"]
            cid = uuid.uuid4().hex[:6]
            payload = json.dumps({"cid":cid, "fid": fid, "items": {}, "name": name})
            s3.put_object(Bucket=BUCKET, Key=f"{r2_key(fid)}",Body=payload)
            return flask.jsonify({"Success":True, "fid":fid, "cid":cid}), 200

        else:
            return flask.jsonify({"Hacker":True}), 401
    except Exception as e:
        return flask.jsonify({"success": False, "error": str(e)}), 500
@app.route("/deletefreezer", methods=["POST"])
def deletefreezer():
    try:
        freezer_request = flask.request.get_json()
        if freezer_request["secret"] == os.environ["SECRET_PASS"]:
            fid = freezer_request["fid"]
            s3.delete_object(Bucket=BUCKET, Key=f"{r2_key(fid)}")
            return flask.jsonify({"Success":True}), 200
        else:
            return flask.jsonify({"Hacker":True}), 401
    except Exception as e:
        return flask.jsonify({"Success":False,"error":str(e)}), 500
@app.route("/", methods=["POST"])
def hello():
    return flask.jsonify({"api":{"active":True},"meta":{"name":"The FreezerOne API","security":"Password Protected. Add secret to every post request JSON body with the value you have been given to authenticate.","endpoints":["/addfreezer [Adds a freezer to the FreezerOne servers. Requires name, gives creator ID (cid) and freezer ID (fid).]", "/deletefreezer [Delete freezer, requires fid.]", "/loadfreezer [Get the active freezer data, requires fid.]", "/updatefreezer [Send a JSON file of the freezer in the data portion of your request. Requires fid.]"]}})
@app.route("/loadfreezer", methods=["POST"])
def loadfreezer():
    try:
        freezer_request = flask.request.get_json()
        if freezer_request["secret"] == os.environ["SECRET_PASS"]:
            fid = freezer_request["fid"]
            data = get_s3(fid)
            return flask.jsonify(data)
        else:
            return flask.jsonify({"Hacker":True}), 401
    except Exception as e:
        return flask.jsonify({"Success":False,"error":str(e)}), 500
@app.route("/updatefreezer", methods=["POST"])
def updatefreezer():
    try:
        freezer_request = flask.request.get_json()
        if freezer_request["secret"] == os.environ["SECRET_PASS"]:
            fid = freezer_request["fid"]
            data = json.loads(freezer_request["data"])
            print(data)
            update_s3(data, fid)
            return flask.jsonify({"Success":True})
        else:
            return flask.jsonify({"Hacker":True}), 401
    except Exception as e:
        return flask.jsonify({"Success":False,"error":str(e)}), 500
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
