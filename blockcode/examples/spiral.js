file.examples.spiral =
[
    ['Repeat', 10, [
        ['Left', 5, 'degrees'],
        ['Repeat', 10, [
            ['Forward', 10, 'steps'],
            ['Left', 14, 'degrees'],
        ]],
        ['Repeat', 10, [
            ['Right', 5, 'degrees'],
            ['Repeat', 17, [
                ['Forward', 13, 'steps'],
                ['Left', 3, 'degrees'],
            ]],
            ['Back to center'],
            ['Right', 3, 'degrees'],
            ['Repeat', 11, [
                ['Pen up'],
                ['Forward', 29, 'steps'],
                ['Pen down'],
                ['Right', 4, 'degrees'],
                ['Forward', -24, 'steps'],
            ]],
        ]],
    ]],
];
