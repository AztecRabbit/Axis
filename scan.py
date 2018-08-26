import sys
import aztecrabbit

args = len(sys.argv) - 1

if (args <= 2):
    sys.exit('\nUsage: python %s (Phone-Number) (Password) (Package-Start) (Package-Stop)' % (__file__))

username      = sys.argv[1]
password      = sys.argv[2]
package_start = sys.argv[3]
package_stop  = ''

if (args >= 4):
    package_stop = sys.argv[4]

def main(threads):
    axis = aztecrabbit.axis(threads)
    axis.sign_in(username, password)
    axis.send_package(package_start, package_stop)

if __name__ == '__main__':

    main(threads = 25)
