function time_since(remaining){

	var negative = false;

	if(remaining < 0){
		negative = true;
		remaining = Math.abs(remaining)
	}

	var units = [
		[ "week", 86400*7],
		[ "day", 86400],
		[ "hour", 3600],
		[ "minute", 60],
		[ "second", 1],
	];
	var string = [];

	for(var i=0;(i<units.length && string.length<2);i++){
		var unit = units[i];
		var amount = 0;
		var unit_name = unit[0];
		var unit_length = unit[1]

		while(remaining >= unit_length && amount < 100){
			amount ++;
			remaining -= unit_length;
		}
		if(amount > 0) string.push(amount + " " + unit_name + (amount == 1 ? "" : "s"));

	}
	return (negative ? "in " : "") + string.join(", ");


}
