
function show_modal(data){
	var item = $(document.createElement("div"));
	item.html("<center><b>LN Monitize</B></center>");

	var main = $(document.createElement("div"));
	main.html("Pay <b id='ln_payamount'>" + data.amount + "</b> sat per <b id='ln_timeframe'>" + data.timeframe + "</b> seconds of ad-free experience?");
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
		btn1.text( mp*data.amount + " sats - " + data.timeframe * mp + " secs");

		select.append(btn1);
	}

	select.on("change", function(evt){
		var mp = steps[$(this).val()];


		$("#ln_payamount").html( mp*data.amount )
		$("#ln_timeframe").html( mp*data.timeframe )
	});

	var buy = $(document.createElement("button"));
	buy.text("Buy");

	btns.append(select);
	btns.append(buy);

	btns.css("text-align", "center")

	item.append(btns);

	item.css("position", "absolute")
		.css("background","white")
		.css("border", "5px solid black")
		.css("border-radius", "10px")
		.width(300)
		.height(100)
		.css("right","-500px")
		.css("top","10px")
		.animate({
			"right": "10px"
		},500);

	$("body").append(item);
}

$(document).ready(function(){
	$.get("ln-monetize.json", {}, function(data){

		for(var i=0;i<data.entries.length;i++){
			var entry = data.entries[i];

			if(entry.type == "visit-time"){
				show_modal(entry);
			}
		}

	});
});
