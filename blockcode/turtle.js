(function(global)
{
    'use strict';

    var PIXEL_RATIO = window.devicePixelRatio || 1;
    var canvasPlaceholder = document.querySelector('.canvas-placeholder');
    var canvas = document.querySelector('.canvas');
    var script = document.querySelector('.script');
    var ctx = canvas.getContext('2d');
    var cos = Math.cos;
    var sin = Math.sin;
    var sqrt = Math.sqrt;
    var PI = Math.PI;
    var DEGREE = PI / 180;
    var WIDTH;
    var HEIGHT;
    var position;
    var direction;
    var visible;
    var pen;
    var color;

    function onResize(evt)
    {
        WIDTH = canvasPlaceholder.getBoundingClientRect().width * PIXEL_RATIO;
        HEIGHT = canvasPlaceholder.getBoundingClientRect().height * PIXEL_RATIO;
        canvas.setAttribute('width', WIDTH);
        canvas.setAttribute('height', HEIGHT);
        canvas.style.top = canvasPlaceholder.getBoundingClientRect().top + 'px';
        canvas.style.left = canvasPlaceholder.getBoundingClientRect().left + 'px';
        canvas.style.width = (WIDTH / PIXEL_RATIO) + 'px';
        canvas.style.height = (HEIGHT / PIXEL_RATIO) + 'px';
        if (evt)
            Menu.runSoon();
    }

    function reset()
    {
        recenter();
        direction = deg2rad(90);
        visible = true;
        pen = true;
        color = 'black';
    }

    function deg2rad(degrees)
    {
        return DEGREE * degrees;
    }

    function drawTurtle()
    {
        var userPen = pen;
        if (visible)
        {
            penUp();
            _moveForward(5);
            penDown();
            _turn(-150);
            _moveForward(12);
            _turn(-120);
            _moveForward(12);
            _turn(-120);
            _moveForward(12);
            _turn(30);
            penUp();
            _moveForward(-5);
            if (userPen)
                penDown();
        }
    }

    function drawCircle(radius)
    {
        if (pen)
        {
            penUp();
            _moveForward(-radius);
            penDown();
            _turn(-90);
            var steps = Math.min(Math.max(6, Math.floor(radius / 2)), 360);
            var theta = 360 / steps;
            var side = radius * 2 * sin(PI / steps);
            _moveForward(side / 2);
            for (var i = 1; i < steps; i++)
            {
                _turn(theta);
                _moveForward(side);
            }
            _turn(theta);
            _moveForward(side / 2);
            _turn(90);
            penUp();
            _moveForward(radius);
            penDown();
        }
    }

    function _moveForward(distance)
    {
        var start = position;
        position = 
        {
            x: cos(direction) * distance * PIXEL_RATIO + start.x,
            y: -sin(direction) * distance * PIXEL_RATIO + start.y,
        };
        if (pen)
        {
            ctx.lineStyle = color;
            ctx.beginPath();
            ctx.moveTo(start.x, start.y);
            ctx.lineTo(position.x, position.y);
            ctx.stroke();
        }
    }

    function _turn(degrees)
    {
        direction += deg2rad(degrees);
    }

    function penUp()
    {
        pen = false;
    }

    function penDown()
    {
        pen = true;
    }

    function hideTurtle()
    {
        visible = false;
    }

    function showTurtle()
    {
        visible = true;
    }

    function forward(block)
    {
        _moveForward(Block.value(block));
    }

    function back(block)
    {
        _moveForward(-Block.value(block));
    }

    function circle(block)
    {
        drawCircle(Block.value(block));
    }

    function left(block)
    {
        _turn(Block.value(block));
    }

    function right(block)
    {
        _turn(-Block.value(block));
    }

    function recenter()
    {
        position = {x: WIDTH / 2, y: HEIGHT / 2};
    }

    function clear()
    {
        ctx.save();
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, WIDTH, HEIGHT);
        ctx.restore();
        reset();
        ctx.moveTo(position.x, position.y);
    }

    onResize();
    clear();
    drawTurtle();

    Menu.item('Left', left, 5, 'degrees');
    Menu.item('Right', right, 5, 'degrees');
    Menu.item('Forward', forward, 10, 'steps');
    Menu.item('Back', back, 10, 'steps');
    Menu.item('Circle', circle, 20, 'radius');
    Menu.item('Pen up', penUp);
    Menu.item('Pen down', penDown);
    Menu.item('Back to center', recenter);
    Menu.item('Hide turtle', hideTurtle);
    Menu.item('Show turtle', showTurtle);

    script.addEventListener('beforeRun', clear, false);
    script.addEventListener('afterRun', drawTurtle, false);
    window.addEventListener('resize', onResize, false);

})(window);
