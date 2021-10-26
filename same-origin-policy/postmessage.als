module postMessage

open origin
open script

sig PostMessage extends BrowserOp
{
    message: Resource,
    targetOrigin: Origin,
}{
    noDocumentChange[start, end]
}

sig ReceiveMessage extends EventHandler
{
    data: Resource,
    srcOrigin: Origin,
}{
    causedBy in PostMessage
    origin[to.context.src] = causedBy.targetOrigin
    data = causedBy.@message
    srcOrigin = origin[causedBy.@from.context.src]
}

run {some m: ReceiveMessage | m.srcOrigin != m.causedBy.targetOrigin}
