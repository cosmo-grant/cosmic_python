import abc

import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class SqlRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch: model.Batch):
        (batch_id,) = self.session.execute(
            "insert into batches (reference, sku, _purchased_quantity, eta) values (?, ?, ?, ?) returning id",
            (batch.reference, batch.sku, batch._purchased_quantity, batch.eta),
        ).fetchone()

        # executemany does not support "returning", and support does not seem to be planned
        # https://github.com/python/cpython/issues/100021
        # so we make multiple round trips :(
        for order_line in batch._allocations:
            (orderline_id,) = self.session.execute(
                "insert into order_lines (sku, qty, orderid) values (?, ?, ?) returning id",
                (order_line.sku, order_line.qty, order_line.orderid),
            ).fetchone()
            self.session.execute(
                "insert into allocations (orderline_id, batch_id) values (?, ?)",
                (orderline_id, batch_id),
            )

    def get(self, reference) -> model.Batch:
        res = self.session.execute(
            "select * from batches where reference = ?",
            (reference,),
        )
        (id, ref, sku, qty, eta) = res.fetchone()
        batch = model.Batch(ref, sku, qty, eta)

        res = self.session.execute(
            """
            select order_lines.*
            from order_lines
            join allocations on order_lines.id = allocations.orderline_id
            where allocations.batch_id = ?
            """,
            (id,),
        )

        order_lines = [
            model.OrderLine(orderid, sku, qty)
            for (_, sku, qty, orderid) in res.fetchall()
        ]

        for order_line in order_lines:
            batch.allocate(order_line)

        return batch
