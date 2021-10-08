(require :asdf)
(load "house.asd")
(asdf:load-system "house")

(house:define-handler (hello-world :content-type "text/plain") ()
                "Hello world!")

(house:start 4040)
