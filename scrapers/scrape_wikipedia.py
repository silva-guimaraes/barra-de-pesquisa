import sqlite3
import scrape_links as sl


# def is_article(url):
#     return


def queue_links(cursor, url_list):
    for url in url_list:
        try:
            cursor.execute('INSERT INTO urls (url) VALUES (?)',
                           (url,))
        except sqlite3.IntegrityError:
            print("já presente em fila")


def set_visited(cursor, url):
    cursor.execute('INSERT INTO visited (url) VALUES (?)', (url,))


def dequeue(cursor):
    cursor.execute('SELECT id, url FROM urls ORDER BY id LIMIT 1')
    row = cursor.fetchone()

    if not row:
        raise Exception('if not row')

    id_, data = row
    cursor.execute('DELETE FROM urls WHERE id = ?', (id_,))
    return data


def create_tables(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            type text
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

    cursor.execute('SELECT count(*) FROM urls')
    queue_length = cursor.fetchone()[0]

    while queue_length > 0:

        next = dequeue(cursor)
        print(next)
        links = sl.extract_links(next, True)
        articles = [link for link in links if is_article(link)]
        print(articles)
        return



if __name__ == '__main__':
    main()
