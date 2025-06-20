class Schema:
    def __init__(self, con):
        self._con = con

    def create_all(self):
        self.create_allocations_table()
        self.create_order_lines_table()
        self.create_batches_table()

    def create_order_lines_table(self):
        self._con.execute(
            """
            create table order_lines (
                id integer primary key,
                sku varchar(256),
                qty integer not null,
                orderid varchar(256)
            )
            """
        )

    def create_batches_table(self):
        self._con.execute(
            """
            create table batches (
                id integer primary key,
                reference varchar(255),
                sku varchar(255),
                _purchased_quantity int not null,
                eta date
            )
            """
        )

    def create_allocations_table(self):
        self._con.execute(
            """
            create table allocations (
                id integer primary key,
                orderline_id int references order_lines (id),
                batch_id int references batches (id)
            )
            """
        )
