'use strict';

function trivial_trials()
{
    var vertices = [
        {_id: 1, name: 'foo', type: 'banana'},
        {_id: 2, name: 'bar', type:' orange'},
    ];

    var edges = [
        {_out: 1, _in: 2, label: 'fruitier'},
    ];

    var tests = [
        {
            fun: function(G, V, E)
            {
                return G.v(1).run();
            },
            got: function(G, V, E)
            {
                return [V[1]];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v(1).out().run();
            },
            got: function(G, V, E)
            {
                return [V[2]];
            },
        },
        {
           fun: function(G, V, E)
            {
                return G.v(2).in().run();
            },
            got: function(G, V, E)
            {
                return [V[1]];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v(2).out().run();
            },
            got: function(G, V, E)
            {
                return [];
            },
        },
    ];

    return {vertices: vertices, edges: edges, tests: tests};
}

