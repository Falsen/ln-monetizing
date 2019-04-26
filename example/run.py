import json, requests, time, sys
import os,binascii

from flask import Flask, render_template, request, redirect

if len(sys.argv) < 2:
	print("Please specify host address")
	sys.exit(0)

data = json.loads( open("static/ln-monetize.json").read() )
apikey = open("apikey").read().split("\n")[0]

keys = {}
comments = []

comments.append({'text': 'Hello everyone', 'time': 0})

try:
	f = open("db.json")
	j = json.loads(f.read())
	keys = j['keys']
	comments = j['comments']
	f.close()
except Exception as e:
	try:
		f.close()
	except Exception as e:
		pass

def updateDb():
	f = open("db.json","w+")
	f.write(json.dumps({'comments': comments, 'keys': keys}))
	f.close()

def checkInvoice(payreq):
	global apikey

	req = requests.get(
		"https://api.opennode.co/v1/charge/{}".format(payreq),
		headers={
			"Authorization": apikey,
			'content-type' : "application/json"
		},
		data=json.dumps({"id": payreq})
	)

	return req.json()

def createInvoice(amount, description):
	global apikey

	req = requests.post(
		"https://api.opennode.co/v1/charges",
		headers={
			"Authorization": apikey,
			'content-type' : "application/json"
		},
		data=json.dumps({ "amount": amount, "description": description })
	)

	return req.json()

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def main():
	token = request.args.get("token")

	data = None
	if token in keys:
		data = keys[token]
		if data['expire'] < time.time():
			token = None
	else:
		token = None

	return render_template("index.html", token=token, token_data=data, now=time.time(), comments=comments)

@app.route("/checkout", methods=["POST"])
def checkout():
	id = request.form.get("id")
	count = request.form.get("amount")
	json_data = json.loads( request.form.get("data"))

	this_entry = None
	for entry in data["entries"]:
		if entry["id"] == int(id):
			this_entry = entry

	if not this_entry:
		return json.dumps({"success": False, "error": "Invalid id"})

	token = binascii.b2a_hex(os.urandom(32))

	amount = int(this_entry["amount"]) * int(count)
	invoice = createInvoice(amount, this_entry['name'])

	payreq = invoice['data']['lightning_invoice']['payreq']
	id = invoice['data']['id']

	if this_entry["type"] == "visit-time":
		expire = int(this_entry['timeframe']) * int(count)
		keys[id] = { "count": int(count), "length": expire, "expire": None }
		updateDb()
	elif this_entry["id"] == 3:
		keys[id] = { "text": json_data['text'], "time": int(time.time())}
		updateDb()
	else:
		keys[id] = {}

	keys[id]['id'] = this_entry['id']
	keys[id]['type'] = this_entry['type']

	obj = { "success": True, "invoice": payreq, "invoice_id": id, "token": token }
	return json.dumps(obj)


@app.route("/status", methods=["GET"])
def status():
	id = request.args.get("invoice")

	print id

	invoice_status = checkInvoice(id)

	print invoice_status

	status = invoice_status['data']['status']

	settle_time = invoice_status['data']['lightning_invoice']['settled_at']

	paid = (status == "paid")

	key = keys[id]

	obj = { "success": True, "paid": paid, "id": key["id"], "type": key["type"] }

	if paid:
		if key['id'] == 1:
			obj['expire'] = keys[id]['expire']
			keys[id]['expire'] = int(time.time()) + keys[id]['length']
			updateDb()

		elif key['id'] == 3:
			comments.append({"text": key['text'], "time": key['time']})
			updateDb()



	return json.dumps(obj)

app.run(debug=True, port=7500, host=sys.argv[1], threaded=True)
