var renderer = PIXI.autoDetectRenderer(800, 600,{backgroundColor: 0xFFFFFF});
document.body.appendChild(renderer.view);

// create the root of the scene graph
var stage = new PIXI.Container();

var count = 0;

// build a rope!
var ropeLength = 700 / 25;


var points = [];

for (var i = 0; i < 25; i++)
{
    points.push(new PIXI.Point(i * ropeLength, 0));
}

var strip = new PIXI.mesh.Rope(PIXI.Texture.fromImage('snake.gif'), points);

strip.position.x = 0;
strip.position.y = 0;
strip.interactive = true;
stage.interactive = true;
strip.on('mousemove', remakeSnake);
strip.on('touchmove', remakeSnake);

stage.addChild(strip);

var g = new PIXI.Graphics();

g.x = strip.x;
g.y = strip.y;
stage.addChild(g);

// start animating
animate();



function remakeSnake(e) {
	//console.log(e.data.originalEvent);
	
	var x = e.data.originalEvent.layerX;
	var y = e.data.originalEvent.layerY;
		
	//console.log(x + " " + y);
	var newPosition = new PIXI.Point(x,y);
	var d = (newPosition.x - points[points.length-1].x)*
	(newPosition.x - points[points.length-1].x)+
	        (newPosition.y - points[points.length-1].y)*
	        (newPosition.y - points[points.length-1].y);
	if (d < 100) return;   
	for (var i = 1; i < points.length; i++)
		points[i-1] = points[i];
	points[points.length-1] = newPosition;
}


function animate() {

    count += 0.1;

    // make the snake
    
    

    // render the stage
    renderer.render(stage);

 

    requestAnimationFrame(animate);
}


