module origin
open http
open browser

sig Origin
{
    protocol: Protocol,
    host: Domain,
    port: lone Port,
}

fun origin[u: Url]: Origin
{
    {o: Origin | o.protocol = u.protocol and o.host = u.host and o.port = u.port}
}
fun origin[d: Document]: Origin{origin[d.src]}

fun currOrigin[d: Document, t: Time]: Origin
{
    {o: Origin | let u = d.src | o.protocol = u.protocol and o.host = d.domain.t and o.port = u.port}
}

fact
{
    no disj o1, o2: Origin |
        o1 != o2 and o1.protocol = o2.protocol and o1.host = o2.host and
        o1.port = o2.port
}
