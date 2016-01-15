from dbutils import transactional, get_connection
from testutils import DbUnitTestCase

class TransactionalTestCase(DbUnitTestCase):

    @transactional
    def create_table_and_insert(self):
        conn = get_connection()
        curs = conn.cursor()
        curs.execute("DROP TABLE IF EXISTS jamtest")
        curs.execute("CREATE TABLE jamtest(row1 int)")
        curs.execute("INSERT INTO jamtest VALUES(1)")

    @transactional
    def insert_and_fail(self):
        conn = get_connection()
        curs = conn.cursor()
        curs.execute("INSERT INTO jamtest VALUES(2)")
        raise Exception()

    @transactional
    def assert_correct_data(self, data):
        conn = get_connection()
        curs = conn.cursor()
        curs.execute("SELECT * FROM jamtest")
        self.assertEqual(curs.fetchall(), data)

    @transactional
    def outer_function(self):
        conn = get_connection()
        curs = conn.cursor()
        curs.execute("INSERT INTO jamtest VALUES(2)")
        self.inner_function()
        raise Exception()

    @transactional
    def inner_function(self):
        conn = get_connection()
        curs = conn.cursor()
        curs.execute("INSERT INTO jamtest VALUES(3)")

    def test_transactional(self):
        self.create_table_and_insert()
        try:
            self.insert_and_fail()
        except:
            pass
        self.assert_correct_data([[1,]])

    def test_nested(self):
        self.create_table_and_insert()
        try:
            self.outer_function()
        except:
            pass
        self.assert_correct_data([[1,]])
