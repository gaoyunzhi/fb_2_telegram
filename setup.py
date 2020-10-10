import os
import sys

def kill():
	os.system("ps aux | grep ython | grep fb_2_telegram | awk '{print $2}' | xargs kill -9")

def setup():
	kill()
	if 'kill' in str(sys.argv):
		return 

	if 'debug' in str(sys.argv):
		os.system('python3 -u fb_2_telegram.py')
	else:
		os.system('nohup python3 -u fb_2_telegram.py %s &' % ' '.join(sys.argv[1:])) 
		if 'notail' not in sys.argv:
			os.system('touch nohup.out')
			os.system('tail -F nohup.out')


if __name__ == '__main__':
	setup()