import argparse
import asyncio
import logging

import crawling
import reporting

ARGS = argparse.ArgumentParser(description='Web crawler')
ARGS.add_argument('roots', nargs='*', default=[], 
    help='Root URL (may be repeated)')
ARGS.add_argument('--max_redirect', action='store', type=int, metavar='N', default=4,
    help='Limit redirection chains (for 301, 302 etc.)')
ARGS.add_argument('--max_tries', action='store', type=int, metavar='N', default=4,
    help='Limit retries on network errors')
ARGS.add_argument('--max_tasks', action='store', type=int, metavar='N', default=100,
    help='Limit concurrent connections')
ARGS.add_argument('--exclude', action='store', metavar='REGEX',
    help='Exclude matching URLs')
ARGS.add_argument('--strict', action='store_true', default=True,
    help='Strict host matching (default)')
ARGS.add_argument('--lenient', action='store_false', dest='strict', default=False,
    help='Lenient host matching')
ARGS.add_argument('-v', '--verbose', action='count', dest='level', default=2,
    help='Verbose logging (repeat for more verbose)')
ARGS.add_argument('-q', '--quiet', action='store_const', const=0, dest='level', default=2,
    help='Only log errors')

def fix_url(url):
    if '://' not in url:
        url = 'http://' + url
    return url

def main():
    args = ARGS.parse_args()
    if not args.roots:
        print('Use --help for command line help')
        return

    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
    logging.basicConfig(level=levels[min(args.level, len(levels) - 1)])

    loop = asyncio.SelectorEventLoop()
    asyncio.set_event_loop(loop)
    roots = {fix_url(root) for root in args.roots}

    crawler = crawling.Crawler(roots, exclude=args.exclude, strict=args.strict,
        max_redirect=args.max_redirect, max_tries=args.max_tries, max_tasks=args.max_tasks)

    try:
        loop.run_until_complete(crawler.crawl())
    except KeyboardInterrupt:
        sys.stderr.flush()
        print('\nInterrupted\n')
    finally:
        reporting.report(crawler)
        loop.run_until_complete(crawler.close())

        loop.stop()
        loop.run_forever()

        loop.close()

if __name__ == '__main__':
    main()
