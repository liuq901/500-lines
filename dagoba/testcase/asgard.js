'use strict';

function asgard_trials()
{
    var vertices = [];

    var aesir = [
        ['Auðumbla', 'F'], ['Ymir', 'M'], ['Þrúðgelmir', 'M'], ['Bergelmir', 'M'], ['Búri', 'M'], ['Borr', 'M'],
        ['Bölþorn', 'M'], ['Bestla', 'F'], ['Odin', 'M'], ['Vili', 'M'], ['Vé', 'M'],
        ['Hœnir',' M'], ['Fjörgynn', 'M'], ['Frigg', 'F'], ['Annar', 'M'],
        ['Jörð', 'F'], ['Nepr', 'M'], ['Gríðr', 'F'], ['Forseti', 'M'],
        ['Rindr', 'F'], ['Dellingr', 'M'], ['Nótt', 'F'], ['Nanna', 'F'], ['Baldr', 'M'],
        ['Höðr', 'M'], ['Hermóðr', 'M'], ['Bragi', 'M'], ['Iðunn', 'F'], ['Víðarr', 'M'],
        ['Váli', 'M'], ['Gefjon', 'F'], ['Ullr', 'M'], ['Týr', 'M'], ['Dagr', 'M'],
        ['Thor', 'M'], ['Sif', 'F'], ['Járnsaxa', 'F'], ['Nörfi', 'M'],
        ['Móði', 'M'], ['Þrúðr', 'F'], ['Magni', 'M'],
        ['Ægir', 'M'], ['Rán', 'F'], ['Nine sisters', 'F'], ['Heimdallr', 'M'],
    ];
    aesir.forEach(function(pair)
    {
        vertices.push({_id: pair[0], name: pair[0], species: 'Aesir', gender: pair[1] == 'M' ? 'male' : 'female'});
    });

    var vanir = [
        'Alvaldi', 'Þjazi', 'Iði', 'Gangr', 'Fárbauti', 'Nál', 'Gymir', 'Aurboða', 'Njörðr', 'Skaði',
        'Sigyn', 'Loki', 'Angrboða', 'Býleistr', 'Helblindi', 'Beli', 'Gerðr', 'Freyr', 'Freyja',
        'Óðr', 'Vali', 'Narfi', 'Hyrrokkin', 'Fenrir', 'Jörmungandr', 'Hel', 'Fjölnir',
        'Hnoss', 'Gersemi', 'Hati Hróðvitnisson', 'Sköll', 'Mánagarmr',
    ];
    vanir.forEach(function(name)
    {
        vertices.push({_id: name, name: name, species: 'Vanir'});
    });

    var edges = [];

    var relationships = [
        ['Ymir', 'Þrúðgelmir'], ['Þrúðgelmir', 'Bergelmir'], ['Bergelmir', 'Bölþorn'], ['Bölþorn', 'Bestla'],
        ['Bestla', 'Odin'], ['Bestla', 'Vili'], ['Bestla', 'Vé'],
        ['Auðumbla', 'Búri'], ['Búri', 'Borr'], ['Borr', 'Odin'], ['Borr', 'Vili'], ['Borr', 'Vé'],
        ['Ægir', 'Nine sisters'], ['Rán', 'Nine sisters'], ['Nine sisters', 'Heimdallr'],
        ['Fjörgynn', 'Frigg'], ['Frigg', 'Baldr'], ['Odin', 'Baldr'],
        ['Nepr', 'Nanna'], ['Nanna', 'Forseti'], ['Baldr', 'Forseti'],
        ['Nörfi', 'Nótt'], ['Nótt', 'Dagr'], ['Nótt', 'Jörð'], ['Annar', 'Jörð'],
        ['Jörð', 'Thor'], ['Odin', 'Thor'], ['Thor', 'Móði'], ['Thor', 'Þrúðr'],
        ['Sif', 'Móði'], ['Sif', 'Þrúðr'], ['Thor', 'Magni'], ['Járnsaxa', 'Magni'],
    ];
    relationships.forEach(function(pair)
    {
        edges.push({_in: pair[0], _out: pair[1], _label: 'parent'});
    });

    var Q;

    var tests = [
        {
            fun: function(G, V, E)
            {
                return G.v('Thor').run();
            },
            got: function(G, V, E)
            {
                return [V['Thor']];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Thor', 'Odin').run();
            },
            got: function(G, V, E)
            {
                return [V['Odin'], V['Thor']];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v({species: 'Aesir'}).run();
            },
            got: function(G, V, E)
            {
                return Array.from(aesir, function(pair)
                {
                    return V[pair[0]];
                }).reverse();
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v().run();
            },
            got: function(G, V, E)
            {
                return vertices.reverse();
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Thor').in().out().unique().run();
            },
            got: function(G, V, E)
            {
                return [V['Járnsaxa'], V['Thor'], V['Sif']];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Thor').out().in().unique().run();
            },
            got: function(G, V, E)
            {
                return [V['Thor'], V['Baldr']];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Thor').in().in().out().out().run();
            },
            got: function(G, V, E)
            {
                return [];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Thor').out().in().unique().filter(function(asgardian)
                {
                    return asgardian._id != 'Thor';
                }).run();
            },
            got: function(G, V, E)
            {
                return [V['Baldr']];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Thor').out('parent').out('parent').property('_id').run();
            },
            got: function(G, V, E)
            {
                return G.v('Thor').out('parent').out('parent').run().map(function(vertex)
                {
                    return vertex._id;
                });
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Thor').out().in().unique().filter({survives: true}).run();
            },
            got: function(G, V, E)
            {
                return [];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Thor').out().in().unique().filter({gender: 'male'}).run();
            },
            got: function(G, V, E)
            {
                return [V['Thor'], V['Baldr']];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Thor').out().out().out().in().in().in().unique().run();
            },
            got: function(G, V, E)
            {
                return [V['Thor'], V['Baldr']];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Thor').out().out().out().in().in().in().unique().take(10).run();
            },
            got: function(G, V, E)
            {
                return [V['Thor'], V['Baldr']];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Thor').out().out().out().out().in().in().in().in().unique().take(12).run();
            },
            got: function(G, V, E)
            {
                return [V['Thor'], V['Baldr']];
            },
        },
        {
            fun: function(G, V, E)
            {
                Q = G.v('Auðumbla').in().in().in().property('_id').take(1);
                return Q.run();
            },
            got: function(G, V, E)
            {
                return ['Vé'];
            },
        },
        {
            fun: function(G, V, E)
            {
                return Q.run();
            },
            got: function(G, V, E)
            {
                return ['Vili'];
            },
        },
        {
            fun: function(G, V, E)
            {
                return Q.run();
            },
            got: function(G, V, E)
            {
                return ['Odin'];
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
                return G.v('Thor').out().as('parent').out().as('grandparent').out().as('great-grandparent')
                    .merge('parent', 'grandparent', 'great-grandparent').run();
            },
            got: function(G, V, E)
            {
                return [V['Búri'], V['Borr'], V['Odin'], V['Bölþorn'], V['Bestla'], V['Odin'], V['Nörfi'], V['Nótt'], V['Jörð']];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Thor').as('me').out().in().except('me').unique().run();
            },
            got: function(G, V, E)
            {
                return [V['Baldr']];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Thor').out().as('parent').out().in().except('parent').unique().run();
            },
            got: function(G, V, E)
            {
                return [V['Vé'], V['Vili'], V['Dagr']];
            },
        },
        {
            fun: function(G, V, E)
            {
                Dagoba.addAlias('parents', [['out', ['parent']]]);
                return G.v('Thor').parents().property('_id').run();
            },
            got: function(G, V, E)
            {
                return G.v('Thor').out('parent').property('_id').run();
            },
        },
        {
            fun: function(G, V, E)
            {
                Dagoba.addAlias('children', [['in', ['parent']]]);
                return G.v('Thor').children().run();
            },
            got: function(G, V, E)
            {
                return [V['Magni'], V['Þrúðr'], V['Móði']];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Thor').parents().children().run();
            },
            got: function(G, V, E)
            {
                return [V['Thor'], V['Baldr'], V['Thor']];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Thor').children().parents().run();
            },
            got: function(G, V, E)
            {
                return [V['Járnsaxa'], V['Thor'], V['Sif'], V['Thor'], V['Sif'], V['Thor']];
            },
        },
        {
            fun: function(G, V, E)
            {
                Dagoba.addAlias('siblings', [['as', ['me']], ['out', ['parent']], ['in', ['parent']], ['except', ['me']]]);
                return G.v('Magni').siblings().run();
            },
            got: function(G, V, E)
            {
                return [V['Þrúðr'], V['Móði']];
            },
        },
        {
            fun: function(G, V, E)
            {
                Dagoba.addAlias('grandparents', [['out', ['parent']], ['out', ['parent']]]);
                return G.v('Magni').grandparents().run();
            },
            got: function(G, V, E)
            {
                return [V['Odin'], V['Jörð']];
            },
        },
        {
            fun: function(G, V, E)
            {
                Dagoba.addAlias('cousins', [['out', ['parent']], ['as', ['folks']],
                    ['out', ['parent']], ['in', ['parent']], ['except', ['folks']],
                    ['in', ['parent']], ['unique']]);
                return G.v('Magni').cousins().run();
            },
            got: function(G, V, E)
            {
                return [V['Forseti']];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Magni').parents().as('parents').parents().children().except('parents').
                    children().unique().run();
            },
            got: function(G, V, E)
            {
                return [V['Forseti']];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Forseti').cousins().run();
            },
            got: function(G, V, E)
            {
                return [V['Magni'], V['Þrúðr'], V['Móði']];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Odin').children().children().take(2).run();
            },
            got: function(G, V, E)
            {
                return [V['Magni'], V['Þrúðr']];
            },
        },
        {
            fun: function(G, V, E)
            {
                Dagoba.addAlias('sons', [['in', ['parent']], ['filter', [{gender: 'male'}]]]);
                return G.v('Thor').sons().run();
            },
            got: function(G, V, E)
            {
                return [V['Magni'], V['Móði']];
            },
        },
        {
            fun: function(G, V, E)
            {
                Dagoba.addAlias('daughters', [['in', ['parent']], ['filter', [{gender: 'female'}]]]);
                return G.v('Thor').daughters().run();
            },
            got: function(G, V, E)
            {
                return [V['Þrúðr']];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Fjörgynn').daughters().as('me').in().out().out().filter({name: 'Bestla'})
                    .back('me').unique().run();
            },
            got: function(G, V, E)
            {
                return [V['Frigg']];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Fjörgynn').in().as('me').in().out().out().filter({_id: 'Bestla'})
                    .back('me').unique().run();
            },
            got: function(G, V, E)
            {
                return [V['Frigg']];
            },
        },
        {
            fun: function(G, V, E)
            {
                G.addEdge({_in: 'Odin', _out: 'Frigg', _label: 'spouse', order: 1});
                G.addEdge({_in: 'Odin', _out: 'Jörð', _label: 'spouse', order: 2});
                G.addEdge({_in: 'Odin', _out: 'Fenrir', _label: 'owner', order: 2});
                return G.v('Odin').in().run();
            },
            got: function(G, V, E)
            {
                return [V['Fenrir'], V['Jörð'], V['Frigg'], V['Thor'], V['Baldr']];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Odin').in('parent').run();
            },
            got: function(G, V, E)
            {
                return [V['Thor'], V['Baldr']];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Odin').in(['parent', 'spouse']).run();
            },
            got: function(G, V, E)
            {
                return [V['Jörð'], V['Frigg'], V['Thor'], V['Baldr']];
            },
        },
        {
            fun: function(G, V, E)
            {
                return G.v('Odin').in({_label: 'spouse', order: 2}).run();
            },
            got: function(G, V, E)
            {
                return [V['Jörð']];
            },
        },
    ];

    return {vertices: vertices, edges: edges, tests: tests};
};
