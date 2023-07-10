
import express from 'express';
import path from 'path';

const app = express();
const port = 3000;

app.get('/', (req, res) => {
    req = req;
    let { search } = req.query;

    if (search == undefined) {
        res.sendFile(path.join(__dirname, 'pages', 'index.html'))
        return
    }
    console.log(search)
    res.sendFile(path.join(__dirname, 'pages', 'search.html'))
})

app.get('/*', express.static('pages'))


app.use('*', (req, res) => {
    req = req;
    res.status(404).send('404');
});

app.listen(port, () => {
    console.log(`[server]: Server is running at http://localhost:${port}`);
});
