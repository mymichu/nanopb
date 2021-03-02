#!/usr/bin/python3
from cpt.packager import ConanMultiPackager
from cpt.ci_manager import CIManager
from cpt.printer import Printer

if __name__ == "__main__":
    printer = Printer()
    ci_manager = CIManager(printer)
    builder = ConanMultiPackager(reference="nanopb/{}".format(ci_manager.get_commit_id()[:7]))
    builder.add_common_builds()
    builder.run()
