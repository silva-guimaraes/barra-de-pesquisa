import sqlite3
import scrape_links as sl


def queue_links(cursor, url_list):
    queued = 0
    for url in url_list:
        try:
            cursor.execute('INSERT INTO queue (url) VALUES (?)',
                           (url,))
            queued += 1
        except sqlite3.IntegrityError:
            # print(e)
            continue
    return queued


def set_visited(cursor, url):
    try:
        cursor.execute('INSERT INTO visited (url) VALUES (?)', (url,))
    except sqlite3.IntegrityError as e:
        print('foobar ->>>>>', url)
        raise e


def is_visited(cursor, url):
    cursor.execute('SELECT COUNT(*) FROM visited WHERE url = ?', (url,))
    count = cursor.fetchone()[0]
    return count > 0


def dequeue(cursor):
    cursor.execute('SELECT id, url FROM queue ORDER BY id LIMIT 1')
    row = cursor.fetchone()

    if not row:
        raise Exception('if not row')

    id_, url = row
    cursor.execute('DELETE FROM queue WHERE id = ?', (id_,))
    return url


def create_tables(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visited (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE
        )
    ''')


def is_article(url):
    meta = ['Help:', 'Category:', 'Wikipedia:', 'Special:', 'Portal:',
            'Template:', 'Talk:', 'File:', 'Template_talk:']

    return all(map(lambda m: m not in url, meta))


def main():
    conn = sqlite3.connect('wikipedia.db')
    cursor = conn.cursor()

    create_tables(cursor)
    conn.commit()

    cursor.execute('SELECT count(*) FROM queue')
    queue_length = cursor.fetchone()[0]

    while queue_length > 0:

        next = dequeue(cursor)
        set_visited(cursor, next)
        queue_length -= 1
        print(next)
        print('queue: ', queue_length)

        links = sl.extract_links(next, True)

        articles = [link for link in links if is_article(link)]

        articles = [article for article in articles
                    if not is_visited(cursor, article)]

        queued = queue_links(cursor, articles)
        queue_length += queued

        conn.commit()


if __name__ == '__main__':
    main()
