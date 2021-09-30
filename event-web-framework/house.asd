(asdf:defsystem #:house
    :depends-on (#:alexandria #:anaphora #:cl-base64 #:cl-ppcre #:cl-json #:bordeaux-threads #:cl-fad #:usocket #:optima #:flexi-streams #:lisp-unit #:trivial-timeout)
    :components ((:file "package")
                 (:file "model")
                 (:file "util")
                 (:file "define-handler")
                 (:file "house")
                 (:file "unit-tests")))

