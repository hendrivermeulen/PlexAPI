import coverage
import unittest

if __name__ == '__main__':
    cov = coverage.Coverage(source=["..\\src"], omit=["*__init__.py"])
    cov.start()

    try:
        testsuite = unittest.TestLoader().discover('.')
        unittest.TextTestRunner(verbosity=0).run(testsuite)
    except:  # catch-all except clause
        pass

    cov.stop()
    cov.save()

    cov.html_report()
    print("Done.")
