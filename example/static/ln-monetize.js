var jsonData = null;

function show_modal(data){
	var item = $(document.createElement("div"));
	item.html("<center><b>LN Monetize</B></center>");

	var main = $(document.createElement("div"));
	main.html("Pay <b id='ln_payamount'>" + data.amount + "</b> sat for <b id='ln_timeframe'>" + time_since(data.timeframe) + "</b> of an ad-free experience?");
	main.css("text-align", "center").css("margin-top","10px")

	//
	//	"type": "visit-time",
	//	"amount": 3,
	//	"timeframe": 60,
	//	"__comment__": "3 sat per 60 seconds",
	//	"id": 1

	item.append(main);

	var btns = $(document.createElement("div"));

	var select = $(document.createElement("select"));

	var steps = [1, 3, 5, 10, 30, 60];
	for(var i in steps){
		var mp = steps[i];
		var btn1 = $(document.createElement("option"));
		btn1.val(i);

		var length = time_since(data.timeframe * mp);
		btn1.text( mp*data.amount + " sats - " + length);

		select.append(btn1);
	}

	var multiplier = 1;

	select.on("change", function(evt){
		var mp = steps[$(this).val()];
		multiplier = mp;

		$("#ln_payamount").html( mp*data.amount )
		$("#ln_timeframe").html( time_since(mp*data.timeframe) )
	});

	var qrcode = $(document.createElement("canvas"));
	qrcode.attr("id", "ln_qrcode");

	var buy = $(document.createElement("button"));
	buy.text("Buy");

	buy.click(function(){
		var url = jsonData.api.checkout;

		$.post(url, {id: data.id, amount: multiplier}, function(data){
			var json = JSON.parse(data);
			item.height("auto");
			var qr = new QRious({element: document.getElementById("ln_qrcode"),value: json.invoice, 'size': 250});

			setTimeout(function(){
				setInterval(function(){
					$.get(jsonData.api.status, {"invoice": json.invoice_id},function(statusData){
						var status = JSON.parse(statusData);

						if(status.paid){
							window.location.href="?token=" + json.invoice_id;
						}
					});
				},3500);

			},5000);
		});
	});

	btns.append(select);
	btns.append(buy);

	btns.append(qrcode);

	btns.css("text-align", "center")

	item.append(btns);

	item.css("position", "absolute")
		.css("background","white")
		.css("border", "5px solid black")
		.css("border-radius", "10px")
		.width(300)
		.height(120)
		.css("right","-500px")
		.css("top","10px")
		.animate({
			"right": "10px"
		},500);

	$("body").append(item);
}

$(document).ready(function(){
	if(!ln_user_token)return;
	$.get("/static/ln-monetize.json", {}, function(data){
		jsonData = data;

		for(var i=0;i<data.entries.length;i++){
			var entry = data.entries[i];

			if(entry.type == "visit-time"){
				show_modal(entry);
			}
		}

	});
});
