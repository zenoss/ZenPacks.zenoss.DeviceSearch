##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2010, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


default: egg


egg:
    # setup.py will call 'make build' before creating the egg
	python setup.py bdist_egg


build:


clean:
	rm -rf build dist temp
	rm -rf *.egg-info
	find . -name *.pyc | xargs rm
