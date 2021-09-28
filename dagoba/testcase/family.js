'use strict';

function family_trials()
{
    var vertices = [
        {_id: 1, name: 'Fred'},
        {_id: 2, name: 'Bob'},
        {_id: 3, name: 'Tom'},
        {_id: 4, name: 'Dick'},
        {_id: 5, name: 'Harry'},
        {_id: 6, name: 'Lucy'},
    ];

    var edges = [
        {_out: 1, _in: 2, _label: 'son'},
        {_out: 2, _in: 3, _label: 'son'},
        {_out: 2, _in: 4, _label: 'son'},
        {_out: 2, _in: 5, _label: 'son'},
        {_out: 2, _in: 6, _label: 'daughter'},
        {_out: 3, _in: 4, _label: 'brother'},
        {_out: 3, _in: 5, _label: 'brother'},
        {_out: 4, _in: 3, _label: 'brother'},
        {_out: 4, _in: 5, _label: 'brother'},
        {_out: 5, _in: 3, _label: 'brother'},
        {_out: 5, _in: 4, _label: 'brother'},
        {_out: 3, _in: 6, _label: 'sister'},
        {_out: 4, _in: 6, _label: 'sister'},
        {_out: 5, _in: 6, _label: 'sister'},
        {_out: 6, _in: 3, _label: 'brother'},
        {_out: 6, _in: 4, _label: 'brother'},
        {_out: 6, _in: 5, _label: 'brother'},
    ];

    var tests = [
        {
            fun: function(G, V, E)
            {
                return G.v(1).out().out().run();
            },
            got: function(G, V, E)
            {
                return [V[6], V[5], V[4], V[3]];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v(1).out().in().out().run();
            },
            got: function(G, V, E)
            {
                return [V[2]];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v(1).out().out('daughter').run();
            },
            got: function(G, V, E)
            {
                return [V[6]];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v(3).out('sister').run();
            },
            got: function(G, V, E)
            {
                return [V[6]];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v(3).out().in('son').in('son').run();
            },
            got: function(G, V, E)
            {
                return [V[1], V[1]];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v(3).out().in('son').in('son').unique().run();
            },
            got: function(G, V, E)
            {
                return [V[1]];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v(1).out('son').out('son').property('name').run();
            },
            got: function(G, V, E)
            {
                return ['Harry', 'Dick', 'Tom'];
            },
        },        
    ];

    return {vertices: vertices, edges: edges, tests: tests};
}

