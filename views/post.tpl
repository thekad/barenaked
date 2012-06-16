<!doctype html>
<!--[if lt IE 7]> <html class="no-js lt-ie9 lt-ie8 lt-ie7" lang="en"> <![endif]-->
<!--[if IE 7]>    <html class="no-js lt-ie9 lt-ie8" lang="en"> <![endif]-->
<!--[if IE 8]>    <html class="no-js lt-ie9" lang="en"> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js" lang="en"> <!--<![endif]-->
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <title>{{title}}</title>
        <meta name="description" content="">
        <meta name="author" content="{{author}}">
        <meta name="viewport" content="width=device-width">
        <link rel="stylesheet" href="{{conf['url']}}/static/style.css">
        <script src="{{conf['url']}}/static/modernizr-2.5.3.min.js"></script>
    </head>
    <body>
        <header>
            <h1>{{title}}</h1>
        </header>
        <div role="main">
            {{!content}}
        </div>
        <footer>
            <p class="author">Copyright &copy; {{author}}</p>
            <p class="date">{{author}}</p>
        </footer>
    </body>
</html>

