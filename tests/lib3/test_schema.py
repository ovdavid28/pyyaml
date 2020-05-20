import yaml
import sys
import pprint

def check_bool(value, expected):
    if expected == 'false()' and value is False:
        return 1
    if expected == 'true()' and value is True:
        return 1
    print(value)
    print(expected)
    return 0

def check_int(value, expected):
    if (int(expected) == value):
        return 1
    print(value)
    print(expected)
    return 0

def check_float(value, expected):
    if expected == 'inf()':
        if value == float("inf"):
          return 1
    elif expected == 'inf-neg()':
        if value == float("-inf"):
          return 1
    elif expected == 'nan()':
        if value != value or (value == 0.0 and value == 1.0):
          return 1
    elif (float(expected) == value):
        return 1
    else:
        print(value)
        print(expected)
        return 0

def check_str(value, expected):
    if value == expected:
        return 1
    print(value)
    print(expected)
    return 0


def _fail(input, test):
    print("Input: >>" + input + "<<");
    print(test);

def test_implicit_resolver(data_filename, verbose=False):
    skip = {
        'Y': 1, 'y': 1, 'N': 1, 'n': 1,
        '!!bool Y': 1, '!!bool N': 1, '!!bool n': 1, '!!bool y': 1,
    }
    skip_dump = {
        '!!str N': 1, '!!str Y': 1, '!!str n': 1, '!!str y': 1,
    }
    types = {
        'str':   [str,   check_str],
        'int':   [int,   check_int],
        'float': [float, check_float],
        'inf':   [float, check_float],
        'nan':   [float, check_float],
        'bool':  [bool,  check_bool],
    }
    if verbose:
        print(skip)
    tests = yaml.load(open(data_filename, 'rb'), Loader=yaml.SafeLoader)

    i = 0;
    fail = 0;
    for input, test in sorted(tests.items()):
        if verbose:
            print('-------------------- ' + str(i))
        test = tests[input]
        i += 1
        if input in skip:
            continue
        exp_type = test[0];
        data     = test[1];
        exp_dump = test[2];

        try:
            loaded = yaml.safe_load(input)
        except:
            print("Error:", sys.exc_info()[0])
            fail+=1
            _fail(input, test)
            continue

        if verbose:
            print(input)
            print(test)
            print(loaded)
            print(type(loaded))

        if exp_type == 'null':
            if loaded is None:
                pass
            else:
                fail+=1
                _fail(input, test)
        else:
            t = types[exp_type][0]
            code = types[exp_type][1]
            if isinstance(loaded, t):
                if code(loaded, data):
                    pass
                else:
                    fail+=1
                    _fail(input, test)
            else:
                fail+=1
                _fail(input, test)

        if input in skip_dump:
            continue

        dump = yaml.safe_dump(loaded, explicit_end=False)
        if dump.endswith('\n...\n'):
            dump = dump[:-5]
        if dump.endswith('\n'):
            dump = dump[:-1]
        if dump == exp_dump:
            pass
        else:
            print("Compare: >>" + dump + "<< >>" + exp_dump + "<<");
            fail+=1
            _fail(input, test)

#        if i >= 80:
#            break

    if fail > 0:
        print("Failed " + str(fail) + " / " + str(i) + " tests");
        assert(False)
    else:
        print("Passed " + str(i) + " tests");
    print("Skipped " + str(len(skip)) + " load tests");
    print("Skipped " + str(len(skip_dump)) + " dump tests");

test_implicit_resolver.unittest = ['.schema']

if __name__ == '__main__':
    import test_appliance
    test_appliance.run(globals())

