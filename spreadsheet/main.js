'use strict';

angular.module('500lines', []).controller('Spreadsheet', function($scope, $timeout)
{
    $scope.Cols = [];
    $scope.Rows = [];
    for (var col of range('A', 'H'))
        $scope.Cols.push(col);
    for (var row of range(1, 20))
        $scope.Rows.push(row);

    function* range(cur, end)
    {
        while (cur <= end)
        {
            yield cur;
            cur = (isNaN(cur) ? String.fromCodePoint(cur.codePointAt() + 1) : cur + 1);
        }
    }

    $scope.keydown = function({which}, col, row)
    {
        switch (which)
        {
        case 38:
        case 40:
        case 13:
            $timeout(function()
            {
                const direction = (which == 38) ? -1 : +1;
                const cell = document.querySelector(`#${col}${row + direction}`);
                if (cell)
                    cell.focus();
            });
        }
    };

    $scope.reset = function()
    {
        $scope.sheet = {A1: 1874, B1: '+', C1: 2046, D1: '\u21D2', E1: '=A1+C1'};
    };

    ($scope.init = function()
    {
        $scope.sheet = angular.fromJson(localStorage.getItem(''));
        if (!$scope.sheet)
            $scope.reset();
        //$scope.worker = new Worker('./worker.js');
        $scope.worker = new Worker(URL.createObjectURL(new Blob(['(' + worker_function.toString() + ')()'],
            {type: 'text/javascript'})))
    }).call()

    $scope.errs = {};
    $scope.vals = {};

    $scope.calc = function()
    {
        const json = angular.toJson($scope.sheet);
        const promise = $timeout(function()
        {
            $scope.worker.terminate();
            $scope.init();
            $scope.calc();
        }, 99);

        $scope.worker.onmessage = function({data})
        {
            $timeout.cancel(promise);
            localStorage.setItem('', json);
            $timeout(function()
            {
                [$scope.errs, $scope.vals] = data;
            });
        };

        $scope.worker.postMessage($scope.sheet);
    };

    $scope.worker.onmessage = $scope.calc;
    $scope.worker.postMessage(null);
});
