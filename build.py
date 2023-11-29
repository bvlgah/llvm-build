import logging
import sys

from builders import LLVMBuildOptions, LLVMCMakeBuilder

_loggingFormat = '[%(asctime)s %(levelname)s ' \
  '%(module)s.%(name)s.%(funcName)s] %(message)s'

def _config_logging():
  logging.basicConfig(format=_loggingFormat)

def _main():
  _config_logging()
  rootLogger = logging.getLogger()
  try:
    buildOptions = LLVMBuildOptions.parse(sys.argv[1:])
    llvmBuilder = LLVMCMakeBuilder(buildOptions)
    llvmBuilder.build()
    rootLogger.info('building finished')
  except Exception as e:
    rootLogger.error('building failed: %s', e)
    sys.exit(1)

if __name__ == '__main__':
  _main()
