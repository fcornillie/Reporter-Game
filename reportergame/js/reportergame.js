function fillInScore( score ) {
	var strHTML = "<div>readers: " + score.xp + "</div><div>articles written: XXX</div><div>articles edited: XXX</div><div>badges: XXX</div><div>inventory: XXX</div>";
	$("#currencies").html(strHTML);
}

function getPlayerScore() {
	$.getJSON("/get_player_score",function(data) {
		fillInScore( data );
	});
}