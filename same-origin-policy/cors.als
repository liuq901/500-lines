module cors
open script
open origin

sig CorsRequest in XmlHttpRequest
{
    origin: Origin,
    allowedOrigins: set Origin,
}{
    from in Script
}

fact corsRule
{
    all r: CorsRequest |
        r.origin = origin[r.from.context.src] and
        r.origin in r.allowedOrigins
}
