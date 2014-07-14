
# Created from dockerfile: ./Dockerfile
# Maintainer:              
from shutit_module import ShutItModule

class redis(ShutItModule):

        def is_installed(self,shutit):
                return False

        def build(self,shutit):
		#add
		shutit.send('groupadd -r redis && useradd -r -g redis redis')
		shutit.install('build-essential tcl valgrind')
		shutit.send_host_dir('/usr/src/redis','context/.')
		shutit.send('make -C /usr/src/redis')
		#in
		shutit.send('make -C /usr/src/redis test || true')
		shutit.send('make -C /usr/src/redis install')
		shutit.send('mkdir /data && chown redis:redis /data')
		shutit.send('pushd /data')
		shutit.send('popd')
                return True

	def finalize(self,shutit):
		return True

	def test(self,shutit):
		return True

	def is_installed(self,shutit):
		return False

	def get_config(self,shutit):
		return True

def module():
        return redis(
                'shutit.tk.redis.redis', 782914092.00,
		description='',
                depends=['shutit.tk.setup']
        )