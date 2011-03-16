function fillInScore( score ) {
	var strHTML = "<div><img src='/img/game_art/xp_30.png' title='Your experience points.'/> " + score.xp + "</div>";
	$("#currencies").html(strHTML);
}

function getPlayerScore() {
	$.getJSON("/get_player_score",function(data) {
		fillInScore( data );
	});
}