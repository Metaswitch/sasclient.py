# @file __init__.py
# Copyright (C) 2015  Metaswitch Networks Ltd

# This bit of magic turns this package into a namespace package, allowing us to
# have metaswitch.common and metaswitch.sasclient etc. in different eggs.
import pkg_resources
pkg_resources.declare_namespace(__name__)
