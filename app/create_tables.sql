
CREATE TABLE "ORDER"(
   "ID"         INT     PRIMARY KEY     NOT NULL,
   "DATE"       DATE                    NOT NULL
);

CREATE TABLE "FOOD"(
   "ID"         INT     PRIMARY KEY     NOT NULL,
   "NAME"       TEXT                    NOT NULL,
   "PRICE"      DECIMAL(8,2)            NOT NULL,
   "AVAILABLE"  BOOLEAN                 NOT NULL
);

CREATE TABLE "ORDER_LINE"(
   "ID"         INT     PRIMARY KEY     NOT NULL,
   "ORDER_ID"   DATE                    NOT NULL,
   "FOOD_ID"    INT                     NOT NULL,
   "QUANTITY"   INT                     NOT NULL,
   "PRICE"      DECIMAL(8,2)            NOT NULL,

    CONSTRAINT fk_order FOREIGN KEY ("ORDER_ID") REFERENCES "ORDER" ("ID"),
    CONSTRAINT fk_food FOREIGN KEY ("FOOD_ID") REFERENCES "FOOD" ("ID")
);