module jsonp
open script

abstract sig Callback {}

sig JsonpRequest in BrowserHttpRequest {padding: Callback}
{
    response in JsonpResponse
}

sig JsonpResponse in Resource
{
    cb: Callback,
    payload: Resource,
}{
    payload != this
}

fact {all r: JsonpResponse | some req: JsonpRequest | req.response = r}

sig ExecCallback extends EventHandler
{
    cb: Callback,
    payload: Resource
}{
    causedBy in JsonpRequest
    to.context = causedBy.(BrowserHttpRequest <: doc)
    let resp = causedBy.response |
        cb = resp.@cb and
        payload = resp.@payload
}

run {some cb: ExecCallback | some cb.payload}
