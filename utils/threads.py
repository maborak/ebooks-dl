import concurrent.futures


class Concurrent():

    def schedule(self, tasks: list = [], engine: object = None, handler: object = None, callback: object = None):
        #print(tasks)
        threads = len(tasks)
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            processed_pool = {executor.submit(
                handler, {'bloque': bloque, 'engine': engine}): bloque for bloque in tasks}
            for future in concurrent.futures.as_completed(processed_pool):
                _ = processed_pool[future]
                try:
                    data = future.result()
                except Exception as exc:
                    print('generated an exception: %s' % (exc))
                else:
                    if callback is not None and callable(callback) is True:
                        callback(data)
                    #print('%r page is %r total' % (3, data))
