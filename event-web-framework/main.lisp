(require :asdf)
(load "house.asd")
(asdf:load-system "house")

(write-line "hello-world")

;(define-closing-handler (hello-world :content-type "text/plain") ()
;                        "Hello world!")
;(start 4040)

(exit)
