function fillInScore( score ) {
	var strHTML = "<div id='readers'><img src='/img/game-art/readers_30.png' title='Your current readership' /><span class='score'>" + score.xp + "</span></div>\n\
	<div id='articles_written'><img src='/img/game-art/article_written_30.png' title='Number of articles you have written' /><span class='score'>X</span></div>\n\
	<div id='articles_edited'><img src='/img/game-art/article_edited_30.png' title='Number of articles you have edited' /><span class='score'>X</span></div>\n\
	<div id='inventory'><img src='/img/game-art/inventory_30.png' title='Your inventory; items you are carrying with you' /><span class='score'>X</span></div>";
	$("#currencies").html(strHTML);
}

function getPlayerScore() {
	$.getJSON("/get_player_score",function(data) {
		fillInScore( data );
	});
}