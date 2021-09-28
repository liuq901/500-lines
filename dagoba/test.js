'use strict';

var GG = [];

var trials = [
    trivial_trials,
    example_trials,
    family_trials,
    people_trials,
    asgard_trials,
];

var triallist = [];
trials.forEach(function(trial)
{
    triallist.push(trial());
});

function cleanclone(results)
{
    return results.map(function(item)
    {
        return JSON.parse(JSON.stringify(item, function(key, value)
        {
            return key[0] == '_' ? undefined : value;
        }));
    });
}

var resultlist = triallist.map(function(trial)
{
    var G = Dagoba.graph();
    GG.push(G);
    trial.vertices.forEach(G.addVertex.bind(G));
    trial.edges.forEach(G.addEdge.bind(G));
    var V = trial.vertices.reduce(function(acc, vertex)
    {
        acc[vertex._id] = G.findVertexById(vertex._id);
        return acc;
    }, {});
    var E = trial.edges;
    return [trial, trial.tests.map(function(test)
    {
        var output, expected;
        if (JSON.stringify(output = cleanclone(test.fun(G, V, E))) == JSON.stringify(expected = cleanclone(test.got(G, V, E))))
            return [1, test.fun, output];
        return [0, test.fun, output, expected];
    })];
});

var testdiv = document.getElementById('tests');

var total = 0, errors = 0;
resultlist.forEach(function(resultbox)
{
    var trial = resultbox[0];
    var header = document.createElement('header');
    testdiv.appendChild(header);
    header.innerHTML = '<p>vertices: <code><pre>' + JSON.stringify(trial.vertices, Dagoba.cleanVertex, 2) + '</pre></code></p>';
    header.innerHTML += '<p>edges: <code><pre>' + JSON.stringify(trial.edges, Dagoba.cleanEdge, 2) + '</pre></code></p>';

    resultbox[1].forEach(function(list)
    {
        var div = document.createElement('div');
        if (!list[0])
            div.classList.add('error');
        testdiv.appendChild(div);
        div.innerHTML = '<p>test: <code> ' + formatFun(list[1]) + '</code></p>';
        div.innerHTML += '<p>output: <code>' + JSON.stringify(list[2]) + '</code></p>';
        if (!list[0])
            div.innerHTML += '<p>expected: <code>' + JSON.stringify(list[3]) + '</code></p>';
        total++;
        errors += !list[0];
    });
});

var eltotal = document.getElementById('totals');
eltotal.innerHTML = '<h4>Total tests: ' + total + ' Errors: ' + errors + '</h4>'

function formatFun(fun)
{
    return fun.toString().slice(50, -15);
}

