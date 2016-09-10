# coding:utf-8
import functools
import logging, threading, time, uuid
import mysql.connector

class Dict(dict):
    def __init__(self, names=(), values=(), **kw):
        super(Dict,self).__init__(**kw)
        for k,v in zip(names,values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key ,val):
        self[key] = val

def next_id(t=None):
    '''
    Return next id as 50-char string.
    Args:
        t: unix timestamp, default to None and using time.time().
    '''
    if t is None:
        t = time.time()
    return '%015d%s000' % (int(t * 1000), uuid.uuid4().hex)

def _profiling(start, sql=''):
    t = time.time() - start
    if t > 0.1:
        logging.warning('[PROFILING] [DB] %s: %s' % (t, sql))
    else:
        logging.info('[PROFILING] [DB] %s: %s' % (t, sql))

# 数据库引擎对象:
class _Engine(object):
    def __init__(self, connect):
        self._connect = connect
    def connect(self):
        return self._connect()

engine = None
class DBError(Exception):
    pass

# 初始化数据库引擎实例
def create_engine(user, password, database, host='127.0.0.1', port=3306):
    global engine
    if engine is not None:
        raise DBError('engine is already exists.')
    params = dict(user=user, password=password, database=database, host=host, port=port)
    defaults = dict(
        use_unicode=True,
        charset='utf8',
        collation='utf8_general_ci',
        autocommit=False,
        buffered=True)
    params.update(defaults)
    # lambda 定义函数
    engine = _Engine(lambda: mysql.connector.connect(**params))
    logging.info('engine %s is created' % hex(id(engine)))


# 持有数据库连接的上下文对象:
class _DbCtx(threading.local):
    def __init__(self):
        self.connection = None
        self.transactions = 0

    def is_init(self):
        return not self.connection is None

    def init(self):
        self.connection = _LazyConnection()
        self.transactions = 0

    def cleanup(self):
        self.connection.cleanup()
        self.connection = None

    def cursor(self):
        return self.connection.cursor()

_db_ctx = _DbCtx()

class _LazyConnection(object):

    def __init__(self):
        self.connection = None

    def cursor(self):
        if self.connection is None:
            connection = engine.connect()
            logging.info('open connection <%s>...' % hex(id(connection)))
            self.connection = connection
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def cleanup(self):
        if self.connection is not None:
            connection = self.connection
            self.connection = None
            logging.info('close connection <%s>...' % hex(id(connection)))
            connection.close()

class _ConnectionCtx(object):
    def __enter__(self):
        global _db_ctx
        self.should_cleanup = False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_cleanup = True
        return self

    def __exit__(self, exctype, excvalue, traceback):
        global _db_ctx
        if self.should_cleanup:
            _db_ctx.cleanup()

def connection():
    return _ConnectionCtx()

def with_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        with connection():
            return func(*args, **kw)
    return wrapper

@with_connection
def __select(sql, first, *args):
    global _db_ctx
    sql = sql.replace('?','%s')
    cursor = None
    logging.info('SQL: %s, ARGS: %s' % (sql, args))
    try:
        cursor = _db_ctx.cursor()
        cursor.execute(sql,args)
        if cursor.description:
            names = [x[0] for x in cursor.description]
        if first:
            values = cursor.fetchone()
            if values is None:
                return None
            return Dict(names,values)
        return [Dict(names,x) for x in cursor.fetchall()]
    finally:
        if cursor:
            cursor.close()

def select(sql, *args):
    return __select(sql, False, *args)

class MultiColumnsError(DBError):
    pass

def select_one(sql, *args):
    return __select(sql, True, *args)

def select_int(sql, *args):
    d = __select(sql, True, *args)
    if len(d)!=1:
        raise MultiColumnsError('Expect only one column.')
    return d.values()[0]

@with_connection
def __update(sql, *args):
    global _db_ctx
    cursor = None
    sql = sql.replace('?','%s')
    try:
        cursor = _db_ctx.cursor()
        cursor.execute(sql, args)
        r = cursor.rowcount
        if _db_ctx.transactions==0:
            logging.info('auto commit')
            _db_ctx.connection.commit()
        return r
    finally:
        if cursor:
            cursor.close()

def insert(table, **kw):
    cols, args = zip(*kw.iteritems())
    sql = 'insert into `%s` (%s) values (%s)' \
        % (
        table,
        ','.join(['`%s`' % col for col in cols]),
        ','.join(['?' for i in range(len(cols))])
        )
    return __update(sql, *args)

def update(sql, *args):
    return __update(sql, *args)

class _TransactionCtx(object):
    def __enter__(self):
        global _db_ctx
        self.should_close_conn = False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_close_conn = True
        _db_ctx.transactions = _db_ctx.transactions + 1
        return self

    def __exit__(self, exctype, excvalue, traceback):
        global _db_ctx
        _db_ctx.transactions = _db_ctx.transactions - 1
        try:
            if _db_ctx.transactions==0:
                if exctype is None:
                    self.commit()
                else:
                    self.rollback()
        finally:
            if self.should_close_conn:
                _db_ctx.cleanup()

    def commit(self):
        global _db_ctx
        try:
            _db_ctx.connection.commit()
        except:
            _db_ctx.connection.rollback()
            raise

    def rollback(self):
        global _db_ctx
        _db_ctx.connection.rollback()

if __name__=='__main__':
    logging.basicConfig(level=logging.DEBUG)
    create_engine('root', 'root', 'crose')
    select_int('select count(*) from user')
    # import doctest
    # doctest.testmod()
