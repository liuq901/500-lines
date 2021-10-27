'use strict';

function worker_function()
{
    self.onmessage = function({data})
    {
        [sheet, errs, vals] = [data, {}, {}];

        for (const coord in sheet)
        {
            ['', '$'].map(function(p)
            {
                return [coord, coord.toLowerCase()].map(function(c)
                {
                    const name = p + c;
                    if ((Object.getOwnPropertyDescriptor(self, name) || {}).get)
                        return;

                    Object.defineProperty(self, name, {get: function()
                    {
                        if (coord in vals)
                            return vals[coord];
                        vals[coord] = NaN;

                        var x = +sheet[coord];
                        if (sheet[coord] !== x.toString())
                            x = sheet[coord];

                        try
                        {
                            vals[coord] = (('=' === x[0]) ? eval.call(null, x.slice(1)) : x);
                        }
                        catch (e)
                        {
                            const match = /\$?[A-z][a-z]+[1-9][0-9]*\b/.exec(e);
                            if (match && !(match[0] in self))
                            {
                                self[match[0]] = 0;
                                delete vals[coord];
                                return self[coord];
                            }
                            errs[coord] = e.toString();
                        }

                        switch (typeof vals[coord])
                        {
                        case 'function':
                        case 'object':
                            vals[coord] += '';
                        }
                        return vals[coord];
                    }});
                });
            });
        }

        for (const coord in sheet)
            self[coord];
        postMessage([errs, vals]);
    }
}
