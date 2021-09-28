'use strict';

function example_trials()
{
    var vertices = [
        {name: 'alice'},
        {_id: 10, name: 'bob', hobbies: ['asdf', {x:3}]},
        {_id: 'charlie', name: 'charlie'},
        {_id: 30, name: 'delta'},
    ];

    var edges = [
        {_out: 1, _in: 10, _label: 'knows'},
        {_out: 10, _in: 30, _label: 'parent'},
        {_out: 10, _in: 'charlie', _label: 'knows'},
    ];

    var tests = [
        {
            fun: function(G, V, E)
            {
                return G.v(1).out('knows').out().run();
            },
            got: function(G, V, E)
            {
                return [V['charlie'], V[30]];
            },
        },
        {
            fun: function(G, V, E)
            {
                var q = G.v(1).out('knows').out().take(1);                
                return q.run();
            },
            got: function(G, V, E)
            {
                return [V['charlie']];
            },
        },
        {
            fun: function(G, V, E)
            {
                var q = G.v(1).out('knows').out().take(1);
                q.run();
                return q.run();
            },
            got: function(G, V, E)
            {
                return [V[30]];
            },
        },
        {
            fun: function(G, V, E)
            {
                var q = G.v(1).out('knows').out().take(1);
                q.run();
                q.run();
                return q.run();
            },
            got: function(G, V, E)
            {
                return [];
            },
        },
    ];

    return {vertices: vertices, edges: edges, tests: tests};
}
