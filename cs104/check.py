# __all__ = ['test_is_true', 'test_equal', 'test_close']

import traceback
import numpy as np
# from IPython.core.magic import register_cell_magic, needs_local_scope
# import sys
import ast


def in_otter():
    for frame in traceback.StackSummary.extract(traceback.walk_stack(None)):
        if frame.filename.endswith('ok_test.py'):
            return True
    return False

def print_message(test, message):
    # if in otter, skip the header and the ANSI color codes because Otter 
    #   already shows all the info in its HTML-formatted error messages.
    in_jupyter = not in_otter()
    
    if in_jupyter:
        print("\u001b[35;1m")
        print("---------------------------------------------------------------------------")
        print("Yipes! " + test)
        print("                                                                           ")
        
    if np.shape(message) == ():
        message = str(message).strip().split("\n")
    for line in message:
        print("  ", line)
        
    if in_jupyter:
        print("\u001b[0m")

def arguments_from_check_call(test_line):
    test_line = test_line.strip()
    tree = ast.parse(test_line, mode='eval')
    args = [ test_line[x.col_offset:x.end_col_offset].strip() for x in tree.body.args]
    return args
    
    
def source_for_check_call():
    # The frame with the test call is the third from the top if we call 
    # a test function directly
    tbo = traceback.extract_stack()
    return tbo[-3].line

def short_form_for_value(x):
    return np.array2string(np.array(x),threshold=10)


def term_and_value(arg, value):
    if arg == repr(value):
        return None, value
    else:
        return f"{arg} == {repr(value)}", value

def term_and_value_at_index(arg, value, index):
    if arg == repr(value):
        return None, value
    elif np.shape(value) == ():
        return f"{arg} == {repr(value)}", value
    else:
        return f"{arg}[{index}] == {value[index]}", value[index]

def binary_check(args_source, args_values, test_op, test_str):
    result = test_op(*args_values)
    if not np.all(result):
        shape = np.shape(result)
        if shape == ():
            terms,values = tuple(zip(*[ term_and_value(*x) for x in zip(args_source,args_values) ]))
            arg_terms = "".join([ x + " and " for x in terms if x != None])
            return [ f"{arg_terms} {test_str(*values)} is False" ]
        elif len(shape) == 1:
            message = [  ]
            false_indices = np.where(result == False)[0]
            for i in false_indices[0:3]:
                terms,values = tuple(zip(*[ term_and_value_at_index(*x,i) for x in zip(args_source,args_values) ]))
                arg_terms = "".join([ x + " and " for x in terms if x != None])
                message += [ f"{arg_terms} {test_str(*values)} is False" ]
            if len(false_indices) > 3:
                message += [ f"... omitting {len(false_indices)-3} more case(s) ..." ]
            return message 
        else:
            return [ f"    {test_str(*map(short_form_for_value, args_values))} is False" ]
    else:
        return []
    

    
def ordering_check(args, a, compare_fn, message_fn):
    message = []
    for i in range(len(a)-1):
        m = binary_check(args[i:i+2], a[i:i+2], compare_fn, message_fn)            
        if len(m) > 0 and len(message) > 0:
            message += [ "" ]
        message += m
    return message
        
def check(a):
    if not np.all(a):
        print_message(source_for_check_call(), "Expression is False")
                
def check_equal(a, b):
    text = source_for_check_call()
    args = arguments_from_check_call(text)            
    message = binary_check(args, [a, b], 
                           lambda x,y: x == y, 
                           lambda x,y: f"{repr(x)} == {repr(y)}")            
    if message != []:
        print_message(text, message)
    
    
def check_close(a, b, plus_or_minus=1e-5):
    text = source_for_check_call()
    args = arguments_from_check_call(text)        
    message = binary_check(args, [a, b], 
                           lambda x,y: np.isclose(x,y,atol=plus_or_minus), 
                           lambda x,y: f"{y-plus_or_minus} <= {x} <= {y+plus_or_minus}")
    if message != []:
        print_message(text, message)
    
def check_less_than(*a):
    text = source_for_check_call()
    args = arguments_from_check_call(text)    
    message = ordering_check(args, a, 
                             lambda x,y: x < y, 
                             lambda x,y: f"{repr(x)} < {repr(y)}")
    if message != []:
        print_message(text, message)    

def check_less_than_or_equal(*a):
    text = source_for_check_call()
    args = arguments_from_check_call(text)    
    message = ordering_check(args, a, 
                             lambda x,y: x <= y, 
                             lambda x,y: f"{repr(x)} <= {repr(y)}")
    if message != []:
        print_message(text, message)

        
def check_type(a, t):
    text = source_for_check_call()
    args = arguments_from_check_call(text) 
    if type(a) is not t:
        print_message(text, f"{repr(a)} does not have type {t.__name__}.")

def check_in(a, *r):
    if len(r) == 1:
        r = r[0]
    if a not in r:
        print_message(source_for_check_call(), 
                      f"{a} is not in {short_form_for_value(r)}")
                
def grab_interval(*interval):
    if len(interval) == 1:
        interval = interval[0]
    if np.shape(interval) != (2,) or np.shape(interval[0]) != () or np.shape(interval[1]) != ():
        raise ValueError()            
    return interval
        
def check_between(a, *interval):
    text = source_for_check_call()
    args = arguments_from_check_call(text)
    
    try:
        interval = grab_interval(*interval)
    except ValueError as err:
        print_message(text, f"Interval must be passed as two numbers " +
                            f"or an array containing two numbers, not {interval}")
        return
    
    result = np.logical_and(interval[0] <= a, a < interval[1])
    
    if not np.all(result):
        shape = np.shape(result)
        if len(shape) == 1:
            message = [ ]
            false_indices = np.where(result == False)[0]
            for i in false_indices[0:3]:
                ai,av = term_and_value_at_index(args[0],a,i)
                if ai != None:
                    terms = ai + ", and "
                else:
                    terms = ""
                message += [ f"{terms}{repr(av)} is not in interval [{interval[0]},{interval[1]})" ]
            if len(false_indices) > 3:
                message += [ f"... omitting {len(false_indices)-3} more case(s) ..." ]
        else:
            message = [ f"{a} is not in interval [{interval[0]},{interval[1]})" ]
        print_message(text, message)
    











# def check(a):
#     if not a:
#         print_message(source_for_check_call(), "Expression is not True")
        
# def check_equal(a,b):
#     try:
#         np.testing.assert_equal(a,b)
#     except AssertionError as e:
#         print_message(source_for_check_call(), f"{a} is not equal to {b}")

# def check_close(a,b,atol=1e-5):
#     try:
#         np.testing.assert_allclose(a,b,atol=atol)
#     except AssertionError as e:
#         print_message(source_for_check_call(), f"{a} is not between {b-atol} and {b+atol}")

# def short_form_for_value(x):
#     return np.array2string(np.array(x),threshold=10)
#     # if np.shape(x) != () and len(x) > 10:
#     #     return "[" + " ".join([str(v) for v in x[:5]] + [ "..." ] + [str(v) for v in x[-5:]]) + "]"
#     # else:
#     #     return str(x)
        
def check_in(a, *r):
    if len(r) == 1:
        r = r[0]
    if a not in r:
        print_message(source_for_check_call(), f"{a} is not in {short_form_for_value(r)}")

# def _grab_interval(*interval):
#     if len(interval) == 1:
#         interval = interval[0]
#     if np.shape(interval) != (2,):
#         raise ValueError(f"Interval must be passed as two numbers " +
#                          "or an array containing two numbers, not {interval}")            
#     return interval
        
# def check_between(a, *interval):
#     interval = _grab_interval(*interval)
#     if a < interval[0] or a >= interval[1]:
#         print_message(source_for_check_call(), 
#                        f"{a} is not in interval [{interval[0]}, {interval[1]})")

# def check_between_or_equal(a, *interval):
#     interval = _grab_interval(*interval)
#     if a < interval[0] or a > interval[1]:
#         print_message(source_for_check_call(), 
#                        f"{a} is not in interval [{interval[0]}, {interval[1]}]")

# def check_strictly_between(a, *interval):
#     interval = _grab_interval(*interval)
#     if a <= interval[0] or a >= interval[1]:
#         print_message(source_for_check_call(), 
#                        f"{a} is not in interval ({interval[0]}, {interval[1]})")

# # def _value_at_index_if_array(v, i):
# #     if np.shape(v) == ():
# #         return v
# #     else:
# #         return v.item(i)
        
# # def _binary_less_than(source_terms, values):
# #     result = np.less(values[0], values[1])
# #     if np.all(result):
# #         return None
# #     else:
# #         shape = np.shape(result)
# #         print(shape)
# #         if shape == ():
# #             return f"check_less_than({source_terms[0]}, {source_terms[1]}) failed:\n" + \
# #                    f"    Expression is not true: " + " < ".join([short_form_for_value(x) for x in values])
# #         elif len(shape) == 1:
# #             false_indices = np.where(result == False)
# #             return f"check_less_than({source_terms[0]}, {source_terms[1]}) failed:\n" + \
# #                    f"    Expression is not true at indices {short_form_for_value(false_indices[0])}"
# #         else:
# #             return f"Expression is not true: " + " < ".join([short_form_for_value(x) for x in values])

# # def check_less_than(*a):
# #     text = source_for_check_call()
# #     args = arguments_from_check_call(text)
# #     for i in range(len(a)-1):
# #         result = _binary_less_than(args[i:i+2], a[i:i+2])
# #         if result != None:
# #             print_message(source_for_check_call(), result)
# #             return
        
            
        
# def check_less_than(*a):
#     for i in range(len(a)-1):
#         result = np.less(a[i], a[i+1])
#         if not np.all(result):
#             text = source_for_check_call()
#             args = arguments_from_check_call(text)
#             print_message(source_for_check_call(), 
#                            f"Expression is not true: " + " < ".join([short_form_for_value(x) for x in args[i:i+2]]))
#             return

# # def check_less_than(*a):
# #     for i in range(len(a)-1):
# #         result = np.less(a[i], a[i+1])
# #         if not np.all(result):
# #             text = source_for_check_call()
# #             args = arguments_from_check_call(text)
# #             print_message(source_for_check_call(), 
# #                            f"Expression is not true: " + " < ".join([short_form_for_value(x) for x in args[i:i+2]]))
# #             return
        
        
# def check_less_than_or_equal(*a):
#     for i in range(len(a)-1):
#         if not np.all(np.less_equal(a[i], a[i+1])):
#             text = source_for_check_call()
#             args = arguments_from_check_call(text)
#             print_message(source_for_check_call(), 
#                            f"Expression is not true: " + " <= ".join([short_form_for_value(x) for x in args[i:i+2]]))
#             return

    
# # @register_cell_magic
# # @needs_local_scope
# # def test(line, cell, local_ns=None): 
# #     original_count = _message_count
# #     for text_as_text in cell.split("\n"):
# #         if text_as_text != '':
# #             try:
# #                 eval(text_as_text, local_ns)
# #             except Exception as e:
# #                 etype, evalue, tb = sys.exc_info()
                
# #                 # Take all the frames above the one for the call to eval, which
# #                 # will have the file name <string>.
# #                 files = [ frame.filename for frame in traceback.extract_tb(tb) ]
# #                 index = files.index('<string>')
# #                 limit = index - len(files) + 1
# #                 tbo = traceback.format_exception(etype, evalue, tb, limit=limit)
                
# #                 print_message(line + ": " + text_as_text, "\n".join(tbo))

# #     if original_count == _message_count:
# #         if line.strip() != '':
# #             print("\u001b[35;1mPassed all tests for " + line + "!\u001b[0m")
# #         else:
# #             print("\u001b[35;1mPassed all tests!\u001b[0m")
                
# #     return None
# # def extact_test_as_text():
# #     # The frame with the test call is the third from the top if we call 
# #     # a test function directly
# #     tbo = traceback.extract_stack()
# #     text = tbo[-3].line
    
# #     # # If we use the magic cells, then that frame will have an empty line,
# #     # # and we must look back to the fourth frame from the top to get the code
# #     # # from the local variable in the `test` function below.
# #     # if text == '':
# #     #     local_vars = sys._getframe().f_back.f_back.f_back.f_locals
# #     #     line = local_vars.get('line', '?')
# #     #     text = line + ": " + local_vars.get('text_as_text', 
# #     #                                         "<can't find test text>")
        
# #     return text

