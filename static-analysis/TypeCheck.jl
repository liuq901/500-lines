module TypeCheck

    function Base.code_typed(f::Function)
        Expr[code_typed(m) for m in f.env]
    end

    function Base.code_typed(m::Method)
        linfo = m.func.code
        (tree, ty) = Base.typeinf(linfo, m.sig, ())
        if !isa(tree, Expr)
            ccall(:jl_uncompress_ast, Any, (Any, Any), linfo, tree)
        else
            tree
        end
    end

    function Base.whos(f, args ...)
        for e in code_typed(f, args ...)
            display(MethodSignature(e))
            for x in sort(e.args[2][2]; by=x -> x[1])
                println("\t", x[1], "\t", x[2])
            end
            println("")
        end
    end

    returntype(e::Expr) = e.args[3].typ

    body(e::Expr) = e.args[3].args

    returns(e::Expr) = filter(x -> typeof(x) == Expr && x.head == :return, body(e))

    function extractcallsfromreturns(e::Expr)
        rs = returns(e)
        rs_with_calls = filter(x -> typeof(x.args[1]) == Expr && x.args[1].head == :call, rs)
        Expr[expr.args[1] for expr in rs_with_calls]
    end

    AType = Union(Type, TypeVar)

    function argumenttypes(e::Expr)
        argnames = Symbol[typeof(x) == Symbol ? x : x.args[1] for x in e.args[1]]
        argtuples = filter(x -> x[1] in argnames, e.args[2][2])
        AType[t[2] for t in argtuples]
    end

    istop(e) = Base.is_expr(e, :call) && typeof(e.args[1]) == TopNode

    function returntype(e::Expr, context::Expr)
        if Base.is_expr(e, :new)
            return e.typ
        end
        if Base.is_expr(e, :call1) && isa(e.args[1], TopNode)
            return e.typ
        end
        if !Base.is_expr(e, :call)
            error("Expected :call Expr")
        end

        if istop(e)
            return e.typ
        end

        callee = e.args[1]
        if istop(callee)
            return returntype(callee, context)
        elseif isa(callee, SymbolNode)
            return Any
        elseif is(callee, Symbol)
            if e.typ != Any || any([isa(x, LambdaStaticData) for x in e.args[2 : end]])
                return e.typ
            end

            if isdefined(Base, callee)
                f = eval(Base, callee)
                if !isa(f, Function) || !isgeneric(f)
                    return e.typ
                end
                fargtypes = tuple([argumenttype(ea, context) for ea in e.args[2 : end]])
                return Union([returntype(ef) for ef in code_typed(f, fargtypes)] ...)
            else
                return @show e.typ
            end
        end

        return e.typ
    end

    function argumenttype(e::Expr, context::Expr)
        if Base.is_expr(e, :call) || Base.is_expr(e, :new) || Base.is_expr(e, :call1)
            return returntype(e, context)
        end

        @show e
        return Any
    end

    function argumenttype(s::Symbol, e::Expr)
        vartypes = [x[1] => x[2] for x in e.args[2][2]]
        s in vartypes ? (vartypes[@show s]) : Any
    end

    argumenttype(s::SymbolNode, e::Expr) = s.typ
    argumenttype(t::TopNode, e::Expr) = Any
    argumenttype(l::LambdaStaticData, e::Expr) = Function
    argumenttype(q::QuoteNode, e::Expr) = argumenttype(q.value, e)

    argumenttype(n::Number, e::Expr) = typeof(n)
    argumenttype(c::Char, e::Expr) = typeof(c)
    argumenttype(s::String, e::Expr) = typeof(s)
    argumenttype(i, e::Expr) = typeof(i)

    Base.start(t::DataType) = [t]
    function Base.next(t::DataType, arr::Vector{DataType})
        c = pop!(arr)
        append!(arr, [x for x in subtypes(c)])
        (c, arr)
    end
    Base.done(t::DataType, arr::Vector{DataType}) = length(arr) == 0

    function methodswithdescendants(t::DataType; onlyleaves::Bool=false, lim::Int=10)
        d = Dict{Symbol, int}()
        count = 0
        for s in t
            if !onlyleaves || (onlyleaves && isleaftype(s))
                count += 1
                fs = Set{Symbol}()
                for m in methodswith(s)
                    push!(fs, m.func.code.name)
                end
                for sym in fs
                    d[sym] = get(d, sym, 0) + 1
                end
            end
        end
        l = [(k, v / count) for (k, v) in d]
        sort!(l, by=(x -> x[2]), rev=true)
        l[1 : min(lim, end)]
    end

    function checkallmodule(m::Module; test=checkreturntypes, kwargs ...)
        score = 0
        for n in names(m)
            f = eval(m, n)
            if isgeneric(f) && typeof(f) == Function
                fm = test(f; mod=m, kwargs ...)
                score += length(fm.methods)
                display(fm)
            end
        end
        println("The total number of failed methods in $m is $score")
    end

    checkreturntypes(m::Module; kwargs ...) = checkallmodule(m; test=checckreturntypes, kwargs ...)
    checklooptypes(m::Module) = checkallmodule(m; test=checklooptypes)
    checkmethodcalls(m::Module) = checkmethodcalls(m; test=checkmethodcalls)

    type MethodSignature
        typs::Vector{AType}
        returntype::Union(Type, TypeVar)
    end
    MethodSignature(e::Expr) = MethodSignature(argumenttypes(e), returntype(e))
    function Base.writemime(io::IO, ::MIME"text/plain", x::MethodSignature)
        println(io, "(", join([string(t) for t in x.types], ","), ")::", x.returntype)
    end

    type FunctionSignature
        methods::Vector{MethodSignature}
        name::Symbol
    end

    function Base.writemime(io::IO, ::MIME"text/plain", x::FunctionSignature)
        for m in x.methods
            print(io, string(x.name))
            display(m)
        end
    end

    function checkreturntypes(f::Function; kwargs ...)
        results = MethodSignature[]
        for e in code_typed(f)
            (ms, b) = checkreturntype(e; kwargs ...)
            if b
                push!(results, ms)
            end
        end
        FunctionSignature(results, f.env.name)
    end

    function checkreturntype(e::Expr; kwargs ...)
        (typ, b) = isreturnbasedonvalues(e; kwargs ...)
        (MethodSignature(argumenttypes(e), typ), b)
    end

    function isreturnbasedonvalues(e::Expr; mod=Base)
        rt = returntype(e)
        ts = argumenttypes(e)
        if isleaftype(rt) || rt == None
            return (rt, false)
        end

        for t in ts
            if !isleaftype(t)
                return (rt, false)
            end
        end

        cs = [returntype(c, e) for c in extractcallsfromreturns(e)]
        for c in cs
            if rt == c
                return (rt, false)
            end
        end

        return (rt, true)
    end

    type LoopResult
        msig::MethodSignature
        lines::Vector{(Symbol, Type)}
        LoopResult(ms::MethodSignature, ls::Vector{(Symbol, Type)}) = new(ms, unique(ls))
    end

    function Base.writemime(io::IO, ::MIME"text/plain", x::LoopResult)
        display(x.msig)
        for (s, t) in x.lines
            println(io, "\t", string(s), "::", string(t))
        end
    end

    type LoopResults
        name::Symbol
        methods::Vector{LoopResult}
    end

    function Base.writemime(io::IO, ::MIME"text/plain", x::LoopResults)
        for lr in x.methods
            print(io, string(x.name))
            display(lr)
        end
    end

    function checklooptypes(f::Function; kwargs ...)
        lrs = LoopResult[]
        for e in code_typed(f)
            lr = checklooptypes(e)
            if length(lr.lines) > 0
                push!(lrs, lr)
            end
        end
        LoopResults(f.env.name, lrs)
    end

    checklooptypes(e::Expr; kwargs ...) = LoopResult(MethodSignature(e), loosetypes(loopcontents(e)))

    function loopcontents(e::Expr)
        b = body(e)
        loops = Int[]
        nesting = 0
        lines = {}
        for i in 1 : length(b)
            if typeof(b[i]) == LabelNode
                l = b[i].label
                jumpback = findnext(
                    x -> (typeof(x) == GotoNode && x.label == l) || (Base.is_expr(x, :gotoifnot) && x.args[end] == l),
                    b, i)
                if jumpback != 0
                    push!(loops, jumpback)
                    nesting += 1
                end
            end
            if nesting > 0
                push!(lines, (i, b[i]))
            end

            if typeof(b[i]) == GotoNode && in(i, loops)
                splice!(loops, findfirst(loops, i))
                nesting -= 1
            end
        end
        lines
    end

    function loosetypes(lr::Vector)
        lines = (Symbol, Type)[]
        for (i, e) in lr
            if typeof(e) == Expr
                es = copy(e.args)
                while !isempty(es)
                    e1 = pop!(es)
                    if typeof(e1) == Expr
                        append!(es, e1.args)
                    elseif typeof(e1) == SymbolNode && !isleaftype(e1.typ) && typeof(e1.typ) == UnionType
                        push!(lines, (e1.name, e1.typ))
                    end
                end
            end
        end
        return lines
    end

    type CallSignature
        name::Symbol
        argumenttypes::Vector{AType}
    end
    function Base.writemime(io::IO, ::MIME"text/plain", x::CallSignature)
        println(io, string(x.name), "(", join([strint(t) for t in x.argumenttypes], ","), ")")
    end

    type MethodCalls
        m::MethodSignature
        calls::Vector{CallSignature}
    end

    function Base.writemime(io::IO, ::MIME"text/plain", x::MethodCalls)
        display(x.m)
        for c in x.calls
            print(io, "\t")
            display(c)
        end
    end

    type FunctionCalls
        name::Symbol
        methods::Vector{MethodCalls}
    end

    function Base.writemime(io::IO, ::MIME"text/plain", x::FunctionCalls)
        for mc in x.methods
            print(io, string(x.name))
            display(mc)
        end
    end

    function checkmethodcalls(f::Function; kwargs ...)
        calls = MethodCalls[]
        for m in f.env
            e = code_typed(m)
            mc = checkmethodcalls(e, m; kwargs ...)
            if !isempty(mc.calls)
                push!(calls, mc)
            end
        end
        FunctionCalls(f.env.name, calls)
    end

    function checkmethodcalls(e::Expr, m::Method; kwargs ...)
        if Base.arg_decl_parts(m)[3] == symbol("deprecated.jl")
            CallSignature[]
        end
        nomethoderrors(e, methodcalls(e); kwargs ...)
    end

    function hasmatches(mod::Module, cs::CallSignature)
        if isdefined(mod, cs.name)
            f = eval(mod, cs.name)
            if isgeneric(f)
                opts = methods(f, tuple(cs.argumenttypes ...))
                if isempty(opts)
                    return false
                end
            end
        end
        return true
    end

    function nomethoderrors(e::Expr, cs::Vector{CallSignature}; mod=Base)
        output = CallSignature[]
        for callsig in cs
            if !hasmatches(mod, callsig)
                push!(output, callsig)
            end
        end
        MethodCalls(MethodSignature(e), output)
    end

    function methodcalls(e::Expr)
        b = body(e)
        lines = CallSignature[]
        for s in b
            if typeof(s) == Expr
                if s.head == :return
                    append!(b, s.args)
                elseif s.head == :call
                    if typeof(s.args[1]) == Symbol
                        push!(lines, CallSignature(s.args[1], [argumenttype(e1, e) for e1 in s.args[2 : end]]))
                    end
                end
            end
        end
        lines
    end

end
