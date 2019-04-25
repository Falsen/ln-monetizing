import json, requests, time
import os,binascii

from flask import Flask, render_template, request, redirect


data = json.loads( open("static/ln-monetize.json").read() )
apikey = open("apikey").read().split("\n")[0]

keys = {}

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

	return render_template("index.html", token=token, token_data=data, now=time.time())

@app.route("/checkout", methods=["POST"])
def checkout():
	id = request.form.get("id")
	count = request.form.get("amount")

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

	expire = int(this_entry['timeframe']) * int(count)
	keys[id] = { "count": int(count), "length": expire, "expire": None }

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

	if paid:
		keys[id]['expire'] = int(time.time()) + keys[id]['length']

	obj = { "success": True, "paid": paid, "expire": keys[id]['expire'] }
	return json.dumps(obj)

app.run(debug=True, port=7000, host="127.0.0.1", threaded=True)
