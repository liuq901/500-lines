'use strict';

function people_trials()
{
    var vertices = [
        {_id: 1, name: 'marko', age: 29, dow: ['mon', 'tue'], dob: '1984-05-05', active: true, salary: '$120,000', device: {qty: 3, mobile: {phone: ['iphone', 'samsung'], tablet: ['galaxy']}}, stars: 0},
        {_id: 2, name: 'vadas', age: 27, dow: ['mon', 'wed', 'thu'], dob: '1986-03-12', active: false, salary: '$100,000', device: {qty: 1, mobile: {phone: ['iphone']}}},
        {_id: 3, name: 'lop', lang: 'java'},
        {_id: 4, name: 'josh', age: 32, dow: ['fri'], dob: '1981-09-01', active: true, salary: '$80,000', device: {qty: 2, mobile: {phone: ['iphone'], tablet: ['ipad']}}},
        {_id: 5, name: 'ripple', lang: 'java'},
        {_id: 6, name: 'peter', age: 35, dow: ['mon', 'fri'], dob: '1978-12-13', active: true, salary: '$70,000', device: {qty: 2, mobile: {phone: ['iphone'], tablet: ['ipad']}}},
    ];

    var edges = [
        {_out: 1, _in: 2, weight: 0.5, _label: 'knows'},
        {_out: 1, _in: 4, weight: 1.0, _label: 'knows'},
        {_out: 1, _in: 3, weight: 0.4, _label: 'created'},
        {_out: 4, _in: 5, weight: 1.0, _label: 'created'},
        {_out: 4, _in: 3, weight: 0.4, _label: 'created'},
        {_out: 6, _in: 3, weight: 0.2, _label: 'created'},
    ];

    var Q;

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
                return G.v().run();
            },
            got: function(G, V, E)
            {
                return [V[6], V[5], V[4], V[3], V[2], V[1]];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v(1, 4).run();
            },
            got: function(G, V, E)
            {
                return [V[4], V[1]];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v({lang: 'java'}).run();
            },
            got: function(G, V, E)
            {
                return [V[5], V[3]];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v({lang: 'asdf'}).run();
            },
            got: function(G, V, E)
            {
                return [];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v().out().unique().run();
            },
            got: function(G, V, E)
            {
                return [V[3], V[5], V[4], V[2]];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v().out('knows').run();
            },
            got: function(G, V, E)
            {
                return [V[4], V[2]];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v().out(['knows']).run();
            },
            got: function(G, V, E)
            {
                return [V[4], V[2]];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v().out(['knows', 'created']).unique().run();
            },
            got: function(G, V, E)
            {
                return [V[3], V[5], V[4], V[2]];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v(1).out().run();
            },
            got: function(G, V, E)
            {
                return [V[3], V[4], V[2]];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v().out({weight: 1}).run();
            },
            got: function(G, V, E)
            {
                return [V[5], V[4]];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v().out({weight: 1, _label: 'knows'}).run();
            },
            got: function(G, V, E)
            {
                return [V[4]];
            },
        },
        {
            fun: function(G, V, E)
            {
                Q = G.v(1).out().property('name').take(1);
                return Q.run();
            },
            got: function(G, V, E)
            {
                return ['lop'];
            },
        },
        {
            fun: function(G, V, E)
            {
                return Q.run();
            },
            got: function(G, V, E)
            {
                return ['josh'];
            },
        },
        {
            fun: function(G, V, E)
            {
                return Q.run();
            },
            got: function(G, V, E)
            {
                return ['vadas'];
            },
        },
        {
            fun: function(G, V, E)
            {
                return Q.run();
            },
            got: function(G, V, E)
            {
                return [];
            },
        },
        {
            fun: function(G, V, E)
            {
                var newG = Dagoba.fromString(G.toString());
                return newG.v(1).out().property('name').run();
            },
            got: function(G, V, E)
            {
                return G.v(1).out().property('name').run();
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v({name: 'marko'}).as('x').out().back('x').property('name').run();
            },
            got: function(G, V, E)
            {
                return ['marko', 'marko', 'marko'];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v({name: 'marko'}).as('x').out().back('x').unique().property('name').run();
            },
            got: function(G, V, E)
            {
                return ['marko'];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v({name: 'marko'}).out().in().unique().property('name').run();
            },
            got: function(G, V, E)
            {
                return ['peter', 'josh', 'marko'];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v(1).as('x').out().in().unique().except('x').property('name').run();
            },
            got: function(G, V, E)
            {
                return ['peter', 'josh'];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v(1).property('stars').run();
            },
            got: function(G, V, E)
            {
                return [0];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v().property('stars').run();
            },
            got: function(G, V, E)
            {
                return [0];
            },
        },
    ];

    return {vertices: vertices, edges: edges, tests: tests};
}
