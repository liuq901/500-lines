(ns hospital
  [:use [fdb core constructs graph query]]
  [:require [fdb.manage :as M]
   [clojure.test :as T :only (is)]])

(def db-name "hos12")
(M/drop-db-conn db-name)

(def hospital-db (M/get-db-conn db-name))

(def basic-kinds [:test/bp-systolic :test/bp-diastolic :test/temperature :person/patient :person/doctor])

(defn make-patient [id address symptoms]
  (-> (make-entity id)
      (add-attr (make-attr :patient/kind :person/patient :db/ref))
      (add-attr (make-attr :patient/city address :string))
      (add-attr (make-attr :patient/tests #{} :db/ref :indexed true :cardinality :db/multiple))
      (add-attr (make-attr :patient/symptoms (set symptoms) :string :cardinality :db/multiple))))

(defn make-test [t-id tests-map types]
  (let [ent (make-entity t-id)]
    (reduce #(add-attr %1 (make-attr (first %2)
                                     (second %2)
                                     (get types (first %2) :number)
                                     :indexed true))
            ent tests-map)))

(defn add-machine [id nm]
  (transact hospital-db (add-entity (-> (make-entity id)
                                        (add-attr (make-attr :machine/name nm :string))))))

(defn add-patient [id address symptoms]
  (transact hospital-db (add-entity (make-patient id address symptoms))))

(defn add-test-results-to-patient [pat-id test-result]
  (let [test-id (:id test-result)
        a (transact hospital-db (add-entity test-result))]
    (transact hospital-db (update-entity pat-id :patient/tests #{test-id} :db/add))))

(transact hospital-db (add-entities (map #(make-entity %) basic-kinds)))

(add-patient :pat1 "London" ["fever", "cough"])
(add-patient :pat2 "London" ["fever", "cough"])

(add-machine :1machine1 "M11")
(add-machine :2machine2 "M222")

(add-test-results-to-patient :pat1
                             (make-test :t2-pat1
                                        {:test/bp-systolic 170 :test/bp-diastolic 80 :test/machine :2machine2}
                                        {:test/machine :db/ref}))
(add-test-results-to-patient :pat2
                             (make-test :t4-pat2
                                        {:test/bp-systolic 170 :test/bp-diastolic 90 :test/machine :1machine1}
                                        {:test/machine :db/ref}))
(add-test-results-to-patient :pat2
                             (make-test :t3-pat2
                                        {:test/bp-systolic 140 :test/bp-diastolic 80 :test/machine :2machine2}
                                        {:test/machine :db/ref}))

(transact hospital-db (update-entity :pat1 :patient/symptoms #{"cold sweat" "sneeze"} :db/reset-to))
(transact hospital-db (update-entity :pat1 :patient/tests #{:t2-pat1} :db/add))
(transact hospital-db (remove-entity :t2-pat1))

(T/is (=
       (q @hospital-db {:find [?id ?k ?b]
                        :where [[?id :test/bp-systolic (> 200 ?b)]
                                [?id :test/bp-diastolic ?k]]})
       '(([("?id" :t4-pat2) ("?b" 170)] [("?id" :t4-pat2) ("?k" 90)])
         ([("?id" :t3-pat2) ("?b" 140)] [("?id" :t3-pat2) ("?k" 80)]))))

(T/is (=
       (q @hospital-db {:find [?id ?a ?v]
                        :where [[(= ?id :pat1) (= ?a :patient/city) ?v]]})
       '(([("?id" :pat1) ("?a" :patient/city) ("?v" "London")]))))

(T/is (=
       (q @hospital-db {:find [?id ?a ?b]
                        :where [[?id ?a (> 200 ?b)]]})
       '(([("?id" :t4-pat2) ("?a" :test/bp-systolic) ("?b" 170)] [("?id" :t4-pat2) ("?a" :test/bp-diastolic) ("?b" 90)])
         ([("?id" :t3-pat2) ("?a" :test/bp-systolic) ("?b" 140)] [("?id" :t3-pat2) ("?a" :test/bp-diastolic) ("?b" 80)]))))

(T/is (=
       (q @hospital-db {:find [?k ?e ?b]
                        :where [[?e :test/bp-systolic (> 160 ?b)]
                                [?e :test/bp-diastolic ?k]]})
       '(([("?e" :t3-pat2) ("?b" 140)] [("?e" :t3-pat2) ("?k" 80)]))))

(T/is (=
       (evolution-of (M/db-from-conn hospital-db) :pat1 :patient/symptoms)
       '({2 #{"cough" "fever"}} {12 #{"cold sweat" "sneeze"}})))

(T/is (=
       (evolution-of (M/db-from-conn hospital-db) :pat1 :patient/tests)
       '({2 #{}} {7 #{:t2-pat1}} {13 #{:t2-pat1}} {14 #{}})))
