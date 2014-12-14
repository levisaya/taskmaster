processes = []

processes.append({'name': 'test print (3s)',
                  'arguments': ['python', '-c', "import time; time.sleep(1); print('hello world'); time.sleep(1); print('goodbye world')"]})

processes.append({'name': 'very long!',
                  'arguments': ['python', '-c', "import time; time.sleep(5); print('all done!')"]})

processes.append({'name': 'many logs!',
                  'arguments': ['python', '-c', "[print('derp{}'.format(x)) for x in range(1000)]"]})
